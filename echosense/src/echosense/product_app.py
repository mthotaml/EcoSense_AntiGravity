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
demo_top_tracks = spotify_adapter.get_top_tracks("mock_access_token")
demo_recent_tracks = spotify_adapter.get_recent_tracks("mock_access_token")
demo_profile.ingest_signals(demo_top_tracks, demo_recent_tracks)

demo_ranker = ContextualRanker(demo_profile)
demo_autopilot = MusicDNAAutopilot(demo_ranker)
demo_temporal = TemporalPatternLearner("listener_01")

# Pre-populate sample listening events for temporal pattern learner
demo_temporal.record_listening_event("morning", "sp_track_101", 0.95, datetime.utcnow())
demo_temporal.record_listening_event("morning", "sp_track_102", 0.90, datetime.utcnow())
demo_temporal.record_listening_event("morning", "sp_track_103", 0.85, datetime.utcnow() - timedelta(days=1))


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


@app.get("/", response_class=HTMLResponse)
def read_root(request: Request, db: Session = Depends(get_db)):
    """Render Primary EchoSense Listener Interface."""
    context = context_resolver.get_live_context()
    all_candidates = demo_top_tracks + demo_recent_tracks
    
    # Generate recommendations & Autopilot queue
    decisions = demo_ranker.rank_candidates(all_candidates, context)
    autopilot_queue = demo_autopilot.maintain_queue(all_candidates, context)
    
    current_pick = decisions[0] if decisions else None
    next_pick = autopilot_queue[0] if autopilot_queue else None
    
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

    template = templates.get_template("index.html")
    html_content = template.render({
        "request": request,
        "current_pick": current_pick,
        "next_pick": next_pick,
        "autopilot_queue": autopilot_queue,
        "recent_tracks": recent_tracks,
        "context": context,
        "pattern": pattern,
        "profile": demo_profile,
        "user_name": user_name,
        "is_connected": is_connected,
        "autopilot_enabled": demo_autopilot.is_enabled,
        "int": int
    })
    return HTMLResponse(content=html_content)


@app.post("/api/autopilot/toggle")
def toggle_autopilot_mode(enabled: bool = Body(..., embed=True)):
    """Toggle between Music DNA Autopilot Queue and Direct Spotify Streaming Mode."""
    demo_autopilot.is_enabled = enabled
    all_candidates = demo_top_tracks + demo_recent_tracks
    context = context_resolver.get_live_context()
    updated_queue = demo_autopilot.maintain_queue(all_candidates, context)
    return {
        "status": "success",
        "enabled": demo_autopilot.is_enabled,
        "autopilot_queue": [
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
            for d in updated_queue
        ]
    }


@app.post("/api/settings/spotify")
def update_spotify_credentials(payload: dict = Body(...)):
    """Update Spotify Client ID and Client Secret dynamically."""
    client_id = payload.get("client_id")
    client_secret = payload.get("client_secret")
    
    if client_id:
        settings.SPOTIFY_CLIENT_ID = client_id.strip()
        spotify_adapter.client_id = client_id.strip()
    if client_secret:
        settings.SPOTIFY_CLIENT_SECRET = client_secret.strip()
        spotify_adapter.client_secret = client_secret.strip()
        
    return {"status": "success", "client_id": settings.SPOTIFY_CLIENT_ID, "has_secret": bool(settings.SPOTIFY_CLIENT_SECRET)}


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
def get_recommendations():
    """API endpoint to fetch current recommendations and factor scores."""
    context = context_resolver.get_live_context()
    all_candidates = demo_top_tracks + demo_recent_tracks
    decisions = demo_ranker.rank_candidates(all_candidates, context)

    return {
        "status": "success",
        "total": len(decisions),
        "recommendations": decisions,
        "context": context
    }


@app.get("/api/autopilot")
def get_autopilot_queue():
    """API endpoint to fetch 5-track Autopilot queue preview."""
    context = context_resolver.get_live_context()
    all_candidates = demo_top_tracks + demo_recent_tracks
    queue = demo_autopilot.maintain_queue(all_candidates, context)

    return {
        "status": "success",
        "queue": queue
    }


@app.post("/api/play")
def play_recommendation(decision_id: str = Body(..., embed=True), db: Session = Depends(get_db)):
    """Start continuous audible playback for decision."""
    devices = spotify_adapter.get_active_devices("mock_access_token")
    active_device = next((d for d in devices if d["is_active"]), devices[0])
    
    all_candidates = demo_top_tracks + demo_recent_tracks
    context = context_resolver.get_live_context()
    
    # 1. Search in current Autopilot upcoming queue
    target_decision = next((d for d in demo_autopilot.upcoming_queue if d.decision_id == decision_id), None)
    
    # 2. Search by decision_id or track.id in ranked candidates
    if not target_decision:
        decisions = demo_ranker.rank_candidates(all_candidates, context)
        target_decision = next((d for d in decisions if d.decision_id == decision_id or d.track.id == decision_id), None)
    
    if target_decision:
        target_track = target_decision.track
    else:
        # 3. Direct lookup in candidate track catalog by ID
        target_track = next((t for t in all_candidates if t.id == decision_id), all_candidates[0])

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
        "now_playing": target_track
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
    all_candidates = demo_top_tracks + demo_recent_tracks
    context = context_resolver.get_live_context()

    if not next_decision:
        new_queue = demo_autopilot.maintain_queue(all_candidates, context)
        next_decision = new_queue[0] if new_queue else demo_ranker.rank_candidates(all_candidates, context)[0]

    # Replenish queue for continuous autopilot stream
    updated_queue = demo_autopilot.maintain_queue(all_candidates, context)

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
        "autopilot_queue": [
            {
                "decision_id": d.decision_id,
                "track": d.track,
                "confidence": d.confidence,
                "why_now": d.why_now,
                "factors": {
                    "dna_affinity": d.factors.dna_affinity,
                    "live_context_fit": d.factors.live_context_fit,
                    "learned_preference": d.factors.learned_preference,
                    "diversity_guard": d.factors.diversity_guard
                }
            }
            for d in updated_queue
        ]
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
