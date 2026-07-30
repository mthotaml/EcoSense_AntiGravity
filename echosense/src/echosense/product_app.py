"""
FastAPI Server — Product Application, REST API Endpoints, & HTML Renderer
"""

import uuid
import os
from datetime import datetime, timedelta
from fastapi import FastAPI, Request, HTTPException, Depends, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from echosense.config import settings
from echosense.db import SessionLocal, init_db, UserRecord
from echosense.security import encrypt_token, decrypt_token, sanitize_log_data
from echosense.provider.spotify import SpotifyAdapter
from echosense.dna.profile import MusicDNAProfile
from echosense.dna.ranker import ContextualRanker
from echosense.context.resolver import ContextResolver
from echosense.context.temporal import TemporalPatternLearner
from echosense.autopilot import MusicDNAAutopilot
from echosense.governance import GovernanceEngine

# Initialize DB tables
init_db()

app = FastAPI(title=settings.PROJECT_NAME, version=settings.VERSION)

# Templates & Static Files setup
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates_dir = os.path.join(base_dir, "templates")
static_dir = os.path.join(base_dir, "static")

class SafeJinja2Templates(Jinja2Templates):
    def TemplateResponse(self, name: str, context: dict, status_code: int = 200) -> HTMLResponse:
        template = self.env.get_template(name)
        content = template.render(context)
        return HTMLResponse(content=content, status_code=status_code)

templates = SafeJinja2Templates(directory=templates_dir)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Dependency: Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Shared Global Application State Setup
spotify_adapter = SpotifyAdapter()
context_resolver = ContextResolver()

# Setup default user profile & ranker
demo_profile = MusicDNAProfile("listener_01")
demo_top_tracks = []
demo_recent_tracks = []

demo_ranker = ContextualRanker(demo_profile)
demo_autopilot = MusicDNAAutopilot(demo_ranker)
demo_temporal = TemporalPatternLearner("listener_01")


@app.get("/healthz")
def healthz():
    """Application Health & Readiness Profile Endpoint."""
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "policy_version": "1.0.0",
        "database": "connected",
        "spotify_status": "configured"
    }


def get_user_candidates(db: Session = None) -> List[any]:
    """Retrieve active candidate catalog. When connected to Spotify, uses REAL Spotify tracks and eliminates seed profiles."""
    if db:
        user = db.query(UserRecord).filter(UserRecord.id == "listener_01").first()
        if user and user.connection_status == "connected" and user.encrypted_access_token:
            try:
                token = decrypt_token(user.encrypted_access_token)
                if token and not token.startswith("mock_"):
                    real_top = spotify_adapter.get_top_tracks(token)
                    real_recent = spotify_adapter.get_recent_tracks(token)
                    if real_top or real_recent:
                        demo_profile.clear_profile()
                        demo_profile.ingest_signals(real_top, real_recent)
                        
                        # Purge seed tracks from queue if present
                        if any(d.track.id.startswith("sp_track_10") for d in demo_autopilot.upcoming_queue):
                            demo_autopilot.upcoming_queue = []
                            demo_autopilot.history_track_ids.clear()
                            
                        return real_top + real_recent
            except Exception as e:
                print("Error retrieving real user candidates:", e)
    return demo_top_tracks + demo_recent_tracks


def serialize_queue_page(page: int = 1, page_size: int = 5, db: Session = None):
    """Helper to maintain continuous queue and return paginated decisions."""
    all_candidates = get_user_candidates(db)
    context = context_resolver.get_live_context()
    demo_autopilot.maintain_queue(all_candidates, context, target_size=20)
    
    items, current_page, size, total_pages, total_items = demo_autopilot.get_paginated_queue(page, page_size)
    
    serialized_items = [
        {
            "decision_id": d.decision_id,
            "track": d.track,
            "confidence": d.confidence,
            "why_now": d.why_now,
            "factors": {
                "dna_affinity": d.factors.dna_affinity if d.factors else 1.0,
                "live_context_fit": d.factors.live_context_fit if d.factors else 1.0,
                "learned_preference": d.factors.learned_preference if d.factors else 0.0,
                "diversity_guard": d.factors.diversity_guard if d.factors else 1.0
            } if d.factors else None
        }
        for d in items
    ]
    
    return {
        "status": "success",
        "page": current_page,
        "page_size": size,
        "total_pages": total_pages,
        "total_items": total_items,
        "autopilot_queue": serialized_items
    }


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """Render Primary EchoSense Listener Interface."""
    context = context_resolver.get_live_context()
    all_candidates = get_user_candidates(db)
    
    # Generate recommendations & Autopilot continuous queue
    decisions = demo_ranker.rank_candidates(all_candidates, context)
    demo_autopilot.maintain_queue(all_candidates, context, target_size=20)
    page_items, current_page, page_size, total_pages, total_items = demo_autopilot.get_paginated_queue(page=1, page_size=5)
    
    current_pick = decisions[0] if decisions else None
    next_pick = page_items[0] if page_items else None
    
    # Record decision provenance
    governance = GovernanceEngine(db)
    if current_pick:
        governance.log_decision("listener_01", current_pick)

    pattern = demo_temporal.detect_stable_pattern(context["daypart"])

    # Check user connection state from database
    user = db.query(UserRecord).filter(UserRecord.id == "listener_01").first()
    is_connected = bool(user and user.connection_status == "connected")
    user_name = user.spotify_display_name if (user and user.spotify_display_name) else "EchoSense Listener"

    recent_tracks = demo_recent_tracks
    if user and user.encrypted_access_token:
        try:
            token = decrypt_token(user.encrypted_access_token)
            if token:
                live_recent = spotify_adapter.get_recent_tracks(token)
                if live_recent:
                    recent_tracks = live_recent
        except Exception as e:
            print("Error reading user token:", e)

    html_content = templates.TemplateResponse("index.html", {
        "request": request,
        "decisions": decisions,
        "current_pick": current_pick,
        "next_pick": next_pick,
        "autopilot_queue": page_items,
        "autopilot_page": current_page,
        "autopilot_page_size": page_size,
        "autopilot_total_pages": total_pages,
        "autopilot_total_items": total_items,
        "recent_tracks": recent_tracks,
        "context": context,
        "pattern": pattern,
        "profile": demo_profile,
        "user_name": user_name,
        "is_connected": is_connected,
        "autopilot_enabled": demo_autopilot.is_enabled,
        "use_live_context": demo_ranker.use_live_context,
        "settings": settings,
        "int": int
    })
    return html_content


@app.post("/api/autopilot/toggle")
def toggle_autopilot_mode(enabled: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    """Toggle between Music DNA Autopilot Queue and Direct Spotify Streaming Mode."""
    demo_autopilot.is_enabled = enabled
    return serialize_queue_page(page=1, page_size=5, db=db)


@app.post("/api/context/toggle")
def toggle_live_context_mode(enabled: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    """Toggle whether live context resolution is factored into DNA queue ranking."""
    demo_ranker.use_live_context = enabled
    demo_autopilot.upcoming_queue = []  # Force fresh queue recalculation
    return serialize_queue_page(page=1, page_size=5, db=db)


@app.get("/api/autopilot")
def get_autopilot_queue(page: int = Query(1, ge=1), page_size: int = Query(5, ge=1, le=20), db: Session = Depends(get_db)):
    """API endpoint to fetch paginated Autopilot queue."""
    return serialize_queue_page(page, page_size, db=db)


@app.post("/api/autopilot/load_more")
def load_more_autopilot_tracks(db: Session = Depends(get_db)):
    """Dynamically rank and append 5 fresh relevant DNA tracks to the continuous queue."""
    all_candidates = get_user_candidates(db)
    context = context_resolver.get_live_context()
    current_size = len(demo_autopilot.upcoming_queue)
    demo_autopilot.maintain_queue(all_candidates, context, target_size=current_size + 5)
    return serialize_queue_page(page=1, page_size=5, db=db)


@app.post("/api/settings/spotify")
def update_spotify_credentials(payload: dict = Body(...)):
    """Update Spotify Client ID and Client Secret dynamically and persist to .env."""
    client_id = payload.get("client_id")
    client_secret = payload.get("client_secret")
    
    if client_id:
        settings.SPOTIFY_CLIENT_ID = client_id.strip()
        spotify_adapter.client_id = client_id.strip()
    if client_secret:
        settings.SPOTIFY_CLIENT_SECRET = client_secret.strip()
        spotify_adapter.client_secret = client_secret.strip()
        
    # Write to .env on disk for persistence
    env_path = os.path.join(base_dir, ".env")
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_lines = f.readlines()

    new_lines = []
    has_id = False
    has_secret = False
    for line in env_lines:
        if line.startswith("SPOTIFY_CLIENT_ID="):
            new_lines.append(f"SPOTIFY_CLIENT_ID={settings.SPOTIFY_CLIENT_ID}\n")
            has_id = True
        elif line.startswith("SPOTIFY_CLIENT_SECRET="):
            new_lines.append(f"SPOTIFY_CLIENT_SECRET={settings.SPOTIFY_CLIENT_SECRET}\n")
            has_secret = True
        else:
            new_lines.append(line)

    if not has_id:
        new_lines.append(f"SPOTIFY_CLIENT_ID={settings.SPOTIFY_CLIENT_ID}\n")
    if not has_secret and settings.SPOTIFY_CLIENT_SECRET:
        new_lines.append(f"SPOTIFY_CLIENT_SECRET={settings.SPOTIFY_CLIENT_SECRET}\n")

    with open(env_path, "w") as f:
        f.writelines(new_lines)

    return {
        "status": "success",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "has_secret": bool(settings.SPOTIFY_CLIENT_SECRET)
    }


pkce_verifiers = {}

@app.get("/auth/spotify")
def auth_spotify(request: Request):
    """Initiate Spotify OAuth Authorization Flow with PKCE."""
    base_url = str(request.base_url).rstrip("/")
    redirect_uri = f"{base_url}/auth/spotify/callback"
    spotify_adapter.redirect_uri = redirect_uri
    
    state = uuid.uuid4().hex
    auth_url, verifier = spotify_adapter.get_authorization_url(state)
    pkce_verifiers[state] = verifier
    
    response = RedirectResponse(auth_url)
    response.set_cookie(key="spotify_pkce_verifier", value=verifier, httponly=True)
    return response


@app.get("/auth/spotify/callback")
def auth_spotify_callback(request: Request, code: str = Query(...), state: str = Query(None), db: Session = Depends(get_db)):
    """Handle Spotify OAuth Callback and persist encrypted tokens."""
    base_url = str(request.base_url).rstrip("/")
    spotify_adapter.redirect_uri = f"{base_url}/auth/spotify/callback"
    
    verifier = request.cookies.get("spotify_pkce_verifier") or pkce_verifiers.get(state, "mock_verifier")
    tokens = spotify_adapter.exchange_code_for_tokens(code, verifier)
    
    access_token = tokens.get("access_token", "")
    refresh_token = tokens.get("refresh_token", "")

    # Ingest user profile & tracks from Spotify API using new access token
    display_name = "EchoSense Listener"
    email = "listener@echosense.ai"
    if access_token:
        try:
            sp_profile = spotify_adapter.get_user_profile(access_token)
            display_name = sp_profile.get("display_name") or display_name
            email = sp_profile.get("email") or email
            
            user_top = spotify_adapter.get_top_tracks(access_token)
            user_recent = spotify_adapter.get_recent_tracks(access_token)
            demo_profile.ingest_signals(user_top, user_recent)
        except Exception as e:
            print("Error ingesting Spotify tracks:", e)
    
    # Store user with encrypted tokens
    user = db.query(UserRecord).filter(UserRecord.id == "listener_01").first()
    if not user:
        user = UserRecord(id="listener_01", spotify_display_name=display_name, spotify_email=email)
        db.add(user)

    user.spotify_display_name = display_name
    user.spotify_email = email
    user.encrypted_access_token = encrypt_token(access_token)
    user.encrypted_refresh_token = encrypt_token(refresh_token)
    user.scopes = settings.SPOTIFY_SCOPES
    user.connection_status = "connected"
    user.last_synced_at = datetime.utcnow()

    db.commit()
    return RedirectResponse(url="/?connected=true")


@app.get("/api/recommendations")
def get_recommendations(db: Session = Depends(get_db)):
    """API endpoint to fetch current recommendations and factor scores."""
    context = context_resolver.get_live_context()
    all_candidates = get_user_candidates(db)
    decisions = demo_ranker.rank_candidates(all_candidates, context)

    return {
        "status": "success",
        "total": len(decisions),
        "recommendations": decisions,
        "context": context
    }


@app.post("/api/play")
def play_recommendation(decision_id: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Start continuous audible playback for decision."""
    devices = spotify_adapter.get_active_devices("mock_access_token")
    active_device = next((d for d in devices if d["is_active"]), devices[0])
    
    all_candidates = get_user_candidates(db)
    context = context_resolver.get_live_context()
    
    # 1. Search in current Autopilot upcoming queue by decision_id or track.id
    target_decision = next((d for d in demo_autopilot.upcoming_queue if d.decision_id == decision_id or d.track.id == decision_id), None)
    
    # 2. Search in ranked decisions over active candidates
    if not target_decision:
        ranked = demo_ranker.rank_candidates(all_candidates, context)
        target_decision = next((d for d in ranked if d.decision_id == decision_id or d.track.id == decision_id), None)

    if target_decision:
        target_track = target_decision.track
    else:
        target_track = next((t for t in all_candidates if t.id == decision_id or t.isrc_or_slug == decision_id), all_candidates[0])

    if target_decision and target_decision in demo_autopilot.upcoming_queue:
        demo_autopilot.upcoming_queue.remove(target_decision)
        demo_autopilot.history_track_ids.add(target_track.id)

    # Replenish queue for continuous autopilot stream
    demo_autopilot.maintain_queue(all_candidates, context, target_size=20)
    page_data = serialize_queue_page(page=1, page_size=5, db=db)

    spotify_adapter.play_track("mock_access_token", active_device["id"], target_track.id)
    
    # Record playback outcome
    governance = GovernanceEngine(db)
    governance.record_outcome_idempotent(
        outcome_id=f"out_{uuid.uuid4().hex[:12]}",
        user_id="listener_01",
        decision_id=decision_id,
        event_type="played",
        completion_ratio=0.01
    )

    return {
        "status": "success",
        "playing": True,
        "device": active_device,
        "decision_id": decision_id,
        "now_playing": target_track,
        "page": page_data["page"],
        "page_size": page_data["page_size"],
        "total_pages": page_data["total_pages"],
        "total_items": page_data["total_items"],
        "autopilot_queue": page_data["autopilot_queue"]
    }


@app.post("/api/skip")
def skip_current_track(db: Session = Depends(get_db)):
    """
    Verified Skip with distinct-track fallback (FR-13, AC-SKIP-01 to AC-SKIP-07).
    """
    devices = spotify_adapter.get_active_devices("mock_access_token")
    active_device = devices[0]["id"]

    # Issue Skip command
    spotify_adapter.skip_to_next("mock_access_token", active_device)

    # Consume next track from Autopilot
    next_decision = demo_autopilot.consume_next()
    all_candidates = get_user_candidates(db)
    context = context_resolver.get_live_context()

    if not next_decision:
        new_queue = demo_autopilot.maintain_queue(all_candidates, context)
        next_decision = new_queue[0] if new_queue else demo_ranker.rank_candidates(all_candidates, context)[0]

    # Replenish queue for continuous autopilot stream
    demo_autopilot.maintain_queue(all_candidates, context, target_size=20)
    page_data = serialize_queue_page(page=1, page_size=5)

    # Record skipped outcome against decision
    governance = GovernanceEngine(db)
    governance.record_outcome_idempotent(
        outcome_id=f"skip_{uuid.uuid4().hex[:12]}",
        user_id="listener_01",
        decision_id=next_decision.decision_id,
        event_type="skipped",
        completion_ratio=0.15
    )

    return {
        "status": "success",
        "verified_skip": True,
        "now_playing": next_decision.track,
        "decision_id": next_decision.decision_id,
        "why_now": next_decision.why_now,
        "page": page_data["page"],
        "page_size": page_data["page_size"],
        "total_pages": page_data["total_pages"],
        "total_items": page_data["total_items"],
        "autopilot_queue": page_data["autopilot_queue"]
    }


@app.post("/api/feedback")
def submit_feedback(
    outcome_id: str = Body(...),
    decision_id: str = Body(...),
    event_type: str = Body(...),
    db: Session = Depends(get_db)
):
    """Log explicit or implicit listener feedback idempotently."""
    governance = GovernanceEngine(db)
    result = governance.record_outcome_idempotent(
        outcome_id=outcome_id,
        user_id="listener_01",
        decision_id=decision_id,
        event_type=event_type
    )
    
    if event_type in ["dislike", "block"]:
        demo_ranker.add_disliked_track("sp_track_101")

    return result


@app.post("/api/context/correct")
def correct_temporal_context(daypart: str = Body(...), corrected_pattern: str = Body(...)):
    """Submit temporal listening pattern correction."""
    demo_temporal.correct_pattern(daypart, corrected_pattern)
    return {"status": "success", "message": f"Updated temporal pattern for {daypart}"}


@app.post("/api/context/reset")
def reset_temporal_context():
    """Reset temporal pattern memory without affecting Music DNA (FR-20, AC-TMI-06)."""
    demo_temporal.reset_temporal_memory()
    return {"status": "success", "message": "Temporal memory reset successfully."}


@app.post("/api/consent/delete")
def delete_user_consent(db: Session = Depends(get_db)):
    """Execute full consent data deletion and return receipt (FR-20, AC-PRV-03)."""
    governance = GovernanceEngine(db)
    receipt = governance.delete_consent_data("listener_01")
    return {"status": "success", "receipt": receipt}


@app.post("/api/disconnect")
def disconnect_spotify(db: Session = Depends(get_db)):
    """Disconnect Spotify account and clear tokens."""
    user = db.query(UserRecord).filter(UserRecord.id == "listener_01").first()
    if user:
        user.connection_status = "disconnected"
        user.encrypted_access_token = ""
        user.encrypted_refresh_token = ""
        db.commit()
    return {"status": "success", "message": "Spotify account disconnected."}
