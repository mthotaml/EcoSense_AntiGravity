"""
Unit tests for Music DNA Ranker, 35% Context Cap, DNA Floor, & Diversity Guards.
"""

import unittest
from echosense.provider.models import Track
from echosense.dna.profile import MusicDNAProfile
from echosense.dna.ranker import ContextualRanker

class TestDNARanker(unittest.TestCase):

    def setUp(self):
        self.profile = MusicDNAProfile("test_user")
        self.track1 = Track("t1", "Midnight City", "M83", "art1", "Album A", 200000, category="Deep Focus")
        self.track2 = Track("t2", "Starlight", "M83", "art1", "Album B", 210000, category="Deep Focus")
        self.track3 = Track("t3", "Outro", "M83", "art1", "Album C", 220000, category="Deep Focus")
        self.track4 = Track("t4", "Ocean Breeze", "Coastal Echoes", "art2", "Album D", 190000, category="Nature Soundscapes")

        self.profile.ingest_signals([self.track1, self.track4], [])
        self.ranker = ContextualRanker(self.profile)

    def test_35_percent_context_cap(self):
        """Verify context influence is capped at 35% of pre-diversity score (GR-04, FR-06)."""
        context = {"daypart": "evening", "weather": "rain", "road_setting": "scenic", "activity": "focus"}
        decisions = self.ranker.rank_candidates([self.track1], context)
        
        self.assertTrue(len(decisions) > 0)
        factors = decisions[0].factors
        self.assertLessEqual(factors.live_context_fit, 0.35)

    def test_dna_floor_enforcement(self):
        """Verify candidates failing DNA floor (<0.20) are excluded (GR-03)."""
        self.profile.artist_affinities["unknown metal"] = 0.05
        self.profile.genre_affinities["metal"] = 0.05
        bad_track = Track("t_bad", "Heavy Metal Metal", "Unknown Metal", "art_bad", "Album X", 180000, category="Metal")
        context = {"daypart": "afternoon"}
        decisions = self.ranker.rank_candidates([bad_track], context)
        
        self.assertEqual(len(decisions), 0)

    def test_artist_fatigue_cap(self):
        """Verify max 2 tracks per artist in Autopilot preview (FR-07)."""
        candidates = [self.track1, self.track2, self.track3, self.track4]
        context = {"daypart": "afternoon"}
        decisions = self.ranker.rank_candidates(candidates, context)

        m83_count = sum(1 for d in decisions if d.track.artist_name == "M83")
        self.assertLessEqual(m83_count, 2)

    def test_negative_feedback_override(self):
        """Verify explicit dislike excludes track unconditionally (GR-05)."""
        self.ranker.add_disliked_track("t1")
        decisions = self.ranker.rank_candidates([self.track1, self.track4], {})
        
        track_ids = [d.track.id for d in decisions]
        self.assertNotIn("t1", track_ids)

if __name__ == '__main__':
    unittest.main()
