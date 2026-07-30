"""
Decision Provenance, Learning Attribution, Consent & Data Deletion Engine
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Optional
from sqlalchemy.orm import Session
from echosense.db import DecisionRecord, OutcomeRecord, ConsentRecord, UserRecord, MusicDNARecord, TemporalPatternRecord
from echosense.provider.models import RecommendationDecision

class GovernanceEngine:
    def __init__(self, db_session: Session):
        self.db = db_session

    def log_decision(self, user_id: str, decision: RecommendationDecision) -> DecisionRecord:
        """Persist recommendation decision provenance idempotently before playback (GR-10, Requirement 9.1)."""
        existing = self.db.query(DecisionRecord).filter(DecisionRecord.decision_id == decision.decision_id).first()
        if existing:
            return existing

        record = DecisionRecord(
            decision_id=decision.decision_id,
            user_id=user_id,
            chosen_track_id=decision.track.id,
            chosen_track_title=decision.track.title,
            chosen_artist_name=decision.track.artist_name,
            confidence=decision.confidence,
            why_now=decision.why_now,
            factor_scores_json=json.dumps({
                "dna_affinity": decision.factors.dna_affinity,
                "live_context_fit": decision.factors.live_context_fit,
                "learned_preference": decision.factors.learned_preference,
                "diversity_guard": decision.factors.diversity_guard
            }),
            context_json=json.dumps({"summary": decision.context_summary}),
            policy_version="1.0.0",
            created_at=datetime.utcnow()
        )
        try:
            self.db.add(record)
            self.db.commit()
            return record
        except Exception:
            self.db.rollback()
            return self.db.query(DecisionRecord).filter(DecisionRecord.decision_id == decision.decision_id).first()

    def record_outcome_idempotent(
        self,
        outcome_id: str,
        user_id: str,
        decision_id: str,
        event_type: str,
        completion_ratio: float = 0.0
    ) -> dict:
        """Record explicit or implicit playback outcome idempotently (GR-10, AC-RES-04)."""
        existing = self.db.query(OutcomeRecord).filter(OutcomeRecord.outcome_id == outcome_id).first()
        if existing:
            return {
                "status": "success",
                "outcome_id": outcome_id,
                "is_duplicate": True,
                "message": "Duplicate outcome ignored idempotently."
            }

        outcome = OutcomeRecord(
            outcome_id=outcome_id,
            decision_id=decision_id,
            user_id=user_id,
            event_type=event_type,
            completion_ratio=completion_ratio,
            created_at=datetime.utcnow()
        )
        self.db.add(outcome)
        self.db.commit()

        return {
            "status": "success",
            "outcome_id": outcome_id,
            "is_duplicate": False,
            "message": "Outcome recorded cleanly."
        }

    def delete_consent_data(self, user_id: str) -> dict:
        """
        Delete all consent-derived user data, credentials, and memory records (FR-20, AC-PRV-03).
        Returns deletion receipt.
        """
        deletion_receipt = {
            "user_id": user_id,
            "deleted_at": datetime.utcnow().isoformat(),
            "receipt_id": f"del_{uuid.uuid4().hex[:12]}",
            "deleted_records": {}
        }

        # Delete Records
        num_dna = self.db.query(MusicDNARecord).filter(MusicDNARecord.user_id == user_id).delete()
        num_dec = self.db.query(DecisionRecord).filter(DecisionRecord.user_id == user_id).delete()
        num_out = self.db.query(OutcomeRecord).filter(OutcomeRecord.user_id == user_id).delete()
        num_pat = self.db.query(TemporalPatternRecord).filter(TemporalPatternRecord.user_id == user_id).delete()
        num_usr = self.db.query(UserRecord).filter(UserRecord.id == user_id).delete()

        self.db.commit()

        deletion_receipt["deleted_records"] = {
            "music_dna": num_dna,
            "decisions": num_dec,
            "outcomes": num_out,
            "temporal_patterns": num_pat,
            "user_account": num_usr
        }

        return deletion_receipt
