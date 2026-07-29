"""
Music DNA Normalization & Affinity Profiler
"""

from typing import List, Dict
from echosense.provider.models import Track, Artist

class MusicDNAProfile:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.artist_affinities: Dict[str, float] = {}
        self.genre_affinities: Dict[str, float] = {}
        self.evidence_count: int = 0

    def ingest_signals(self, top_tracks: List[Track], recent_tracks: List[Track]):
        """Build provider-neutral Music DNA from top and recent track signals."""
        self.evidence_count = len(top_tracks) + len(recent_tracks)
        
        for track in top_tracks:
            self.artist_affinities[track.artist_name.lower()] = 0.85
            self.genre_affinities[track.category.lower()] = 0.80

        for track in recent_tracks:
            curr = self.artist_affinities.get(track.artist_name.lower(), 0.5)
            self.artist_affinities[track.artist_name.lower()] = min(1.0, curr + 0.1)

    def get_track_dna_affinity(self, track: Track) -> float:
        """Calculate durable Music DNA affinity for a candidate track."""
        artist_score = self.artist_affinities.get(track.artist_name.lower(), 0.5)
        category_score = self.genre_affinities.get(track.category.lower(), 0.5)
        
        # Weighted average of artist affinity and category fit
        return (artist_score * 0.6) + (category_score * 0.4)
