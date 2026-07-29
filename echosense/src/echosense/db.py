"""
SQLite & SQLAlchemy Data Models for EchoSense Memory & Governance
"""

import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from echosense.config import settings

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserRecord(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    spotify_display_name = Column(String, default="")
    spotify_email = Column(String, default="")
    encrypted_access_token = Column(Text, default="")
    encrypted_refresh_token = Column(Text, default="")
    scopes = Column(Text, default="")
    connection_status = Column(String, default="connected")  # connected, missing_scopes, disconnected
    last_synced_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

class MusicDNARecord(Base):
    __tablename__ = "music_dna"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    entity_type = Column(String)  # artist, track, genre
    entity_name = Column(String)
    provider_id = Column(String, default="")
    affinity_score = Column(Float, default=0.5)
    evidence_count = Column(Integer, default=1)
    updated_at = Column(DateTime, default=datetime.utcnow)

class DecisionRecord(Base):
    __tablename__ = "decisions"
    
    decision_id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    chosen_track_id = Column(String)
    chosen_track_title = Column(String)
    chosen_artist_name = Column(String)
    confidence = Column(Float, default=0.85)
    why_now = Column(Text)
    factor_scores_json = Column(Text)  # JSON {dna_affinity, live_context, learned_pref, diversity}
    context_json = Column(Text)       # JSON {daypart, weather, road_setting, activity}
    policy_version = Column(String, default="1.0.0")
    created_at = Column(DateTime, default=datetime.utcnow)

class OutcomeRecord(Base):
    __tablename__ = "outcomes"
    
    outcome_id = Column(String, primary_key=True) # Idempotency key
    decision_id = Column(String, ForeignKey("decisions.decision_id"))
    user_id = Column(String, ForeignKey("users.id"))
    event_type = Column(String) # played, completed, skipped, saved, rating
    completion_ratio = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class TemporalPatternRecord(Base):
    __tablename__ = "temporal_patterns"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    daypart = Column(String) # morning, evening, afternoon, night
    pattern_name = Column(String)
    qualifying_events = Column(Integer, default=1)
    distinct_days = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    last_reinforced_at = Column(DateTime, default=datetime.utcnow)

class ConsentRecord(Base):
    __tablename__ = "consents"
    
    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"))
    purpose = Column(String) # music_dna_ingestion, location_context, temporal_learning
    granted = Column(Boolean, default=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    revoked_at = Column(DateTime, nullable=True)

def init_db():
    Base.metadata.create_all(bind=engine)
