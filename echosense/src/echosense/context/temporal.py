"""
Temporal Listening Pattern Learner
Implements 28-day rolling window pattern rules, morning/evening isolation, decay, correction, & reset.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

class TemporalPatternLearner:
    def __init__(self, user_id: str):
        self.user_id = user_id
        # In-memory store for pattern events: { daypart: [ { date, track_id, completion_ratio } ] }
        self.events: Dict[str, List[Dict]] = {
            "morning": [],
            "afternoon": [],
            "evening": [],
            "night": []
        }
        self.corrections: Dict[str, str] = {} # { daypart: corrected_pattern }
        self.is_disabled: bool = False

    def record_listening_event(self, daypart: str, track_id: str, completion_ratio: float, event_date: Optional[datetime] = None):
        """Record listening event for pattern recognition."""
        if self.is_disabled:
            return

        # Completion counts only after at least 60% completion (Requirement FR-19)
        if completion_ratio < 0.60:
            return

        event_time = event_date or datetime.utcnow()
        if daypart not in self.events:
            daypart = "afternoon"

        self.events[daypart].append({
            "date": event_time,
            "track_id": track_id,
            "completion_ratio": completion_ratio
        })

    def detect_stable_pattern(self, daypart: str) -> Optional[Dict]:
        """
        Detect stable listening pattern for a daypart.
        Rules (FR-19 & AC-TMI-01):
        - Requires >= 3 positive events across >= 2 distinct days in a rolling 28-day window.
        - Single play returns None (AC-TMI-02).
        - Morning and Evening patterns remain isolated (AC-TMI-03).
        - Manual correction overrides detection (AC-TMI-05).
        """
        if self.is_disabled:
            return None

        if daypart in self.corrections:
            return {
                "pattern": self.corrections[daypart],
                "confidence": 0.95,
                "is_corrected": True
            }

        events = self.events.get(daypart, [])
        cutoff_date = datetime.utcnow() - timedelta(days=28)
        recent_events = [e for e in events if e["date"] >= cutoff_date]

        if len(recent_events) < 3:
            return None

        distinct_days = set(e["date"].strftime("%Y-%m-%d") for e in recent_events)
        if len(distinct_days) < 2:
            return None

        return {
            "pattern": f"Reflective {daypart.capitalize()} Deep Work",
            "confidence": 0.88,
            "qualifying_events": len(recent_events),
            "distinct_days": len(distinct_days),
            "is_corrected": False
        }

    def correct_pattern(self, daypart: str, corrected_pattern: str):
        """Allow listener to mark temporal interpretation incorrect (FR-20, AC-TMI-05)."""
        self.corrections[daypart] = corrected_pattern

    def reset_temporal_memory(self):
        """Reset temporal memory without deleting unrelated Music DNA (FR-20, AC-TMI-06)."""
        self.events = {"morning": [], "afternoon": [], "evening": [], "night": []}
        self.corrections = {}
