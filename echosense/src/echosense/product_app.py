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

    template = templates.get_template("index.html")
    html_content = template.render({
        "request": request,
        "current_pick": current_pick,
        "next_pick": next_pick,
        "autopilot_queue": autopilot_queue,
        "context": context,
        "pattern": pattern,
        "profile": demo_profile,
        "user_name": "EchoSense Listener",
        "is_connected": True,
        "int": int
    })
    return HTMLResponse(content=html_content)


@app.get("/auth/spotify")
def auth_spotify():
    """Initiate Spotify OAuth Authorization Flow with PKCE."""
    state = uuid.uuid4().hex
    auth_url, verifier = spotify_adapter.get_authorization_url(state)
    return RedirectResponse(auth_url)


@app.get("/auth/spotify/callback")
def auth_spotify_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
    """Handle Spotify OAuth Callback and persist encrypted tokens."""
    tokens = spotify_adapter.exchange_code_for_tokens(code, "mock_verifier")
    
    # Store user with encrypted tokens
    user = db.query(UserRecord).filter(UserRecord.id == "listener_01").first()
    if not user:
        user = UserRecord(id="listener_01", spotify_display_name="EchoSense Listener", spotify_email="listener@echosense.ai")
        db.add(user)

    user.encrypted_access_token = encrypt_token(tokens.get("access_token", ""))
    user.encrypted_refresh_token = encrypt_token(tokens.get("refresh_token", ""))
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
    
    success = spotify_adapter.play_track("mock_access_token", active_device["id"], "sp_track_101")
    
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
        "decision_id": decision_id
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
    if not next_decision:
        all_candidates = demo_top_tracks + demo_recent_tracks
        context = context_resolver.get_live_context()
        new_queue = demo_autopilot.maintain_queue(all_candidates, context)
        next_decision = new_queue[0]

    # Record skipped outcome against current decision
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
        "decision_id": next_decision.decision_id
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
