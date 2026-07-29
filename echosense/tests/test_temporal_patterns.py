"""
Unit tests for Temporal Listening Patterns, 28-day window rules, decay, correction, & reset.
"""

import unittest
from datetime import datetime, timedelta
from echosense.context.temporal import TemporalPatternLearner

class TestTemporalPatterns(unittest.TestCase):

    def setUp(self):
        self.learner = TemporalPatternLearner("test_listener")

    def test_single_play_no_pattern(self):
        """Verify single track play returns no pattern (AC-TMI-02)."""
        self.learner.record_listening_event("morning", "t1", 0.90)
        pattern = self.learner.detect_stable_pattern("morning")
        self.assertIsNone(pattern)

    def test_qualifying_pattern_creation(self):
        """Verify 3 qualifying events across 2 distinct days create stable pattern (AC-TMI-01)."""
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)

        self.learner.record_listening_event("morning", "t1", 0.90, today)
        self.learner.record_listening_event("morning", "t2", 0.85, today)
        self.learner.record_listening_event("morning", "t3", 0.95, yesterday)

        pattern = self.learner.detect_stable_pattern("morning")
        self.assertIsNotNone(pattern)
        self.assertTrue(pattern["qualifying_events"] >= 3)
        self.assertTrue(pattern["distinct_days"] >= 2)

    def test_morning_evening_isolation(self):
        """Verify morning and evening patterns remain isolated (AC-TMI-03)."""
        today = datetime.utcnow()
        yesterday = today - timedelta(days=1)

        self.learner.record_listening_event("morning", "t1", 0.90, today)
        self.learner.record_listening_event("morning", "t2", 0.85, today)
        self.learner.record_listening_event("morning", "t3", 0.95, yesterday)

        morning_pattern = self.learner.detect_stable_pattern("morning")
        evening_pattern = self.learner.detect_stable_pattern("evening")

        self.assertIsNotNone(morning_pattern)
        self.assertIsNone(evening_pattern)

    def test_manual_pattern_correction(self):
        """Verify listener correction overrides detected pattern (AC-TMI-05)."""
        self.learner.correct_pattern("morning", "Energetic Morning Focus Workout")
        pattern = self.learner.detect_stable_pattern("morning")

        self.assertIsNotNone(pattern)
        self.assertEqual(pattern["pattern"], "Energetic Morning Focus Workout")
        self.assertTrue(pattern["is_corrected"])

    def test_temporal_memory_reset(self):
        """Verify reset clears temporal memory (AC-TMI-06)."""
        self.learner.correct_pattern("morning", "Test Pattern")
        self.learner.reset_temporal_memory()

        pattern = self.learner.detect_stable_pattern("morning")
        self.assertIsNone(pattern)

if __name__ == '__main__':
    unittest.main()
