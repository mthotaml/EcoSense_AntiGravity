"""
Provider-Neutral Domain Models for Music DNA & Recommendation Engine
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict

@dataclass
class Artist:
    id: str
    name: str
    genres: List[str] = field(default_factory=list)
    affinity_score: float = 0.5

@dataclass
class Track:
    id: str
    title: str
    artist_name: str
    artist_id: str
    album_name: str
    duration_ms: int
    isrc: Optional[str] = None
    preview_url: Optional[str] = None
    cover_url: Optional[str] = None
    category: str = "General"
    
    @property
    def isrc_or_slug(self) -> str:
        if self.isrc:
            return f"isrc:{self.isrc}"
        clean_title = "".join(c for c in self.title.lower() if c.isalnum())
        clean_artist = "".join(c for c in self.artist_name.lower() if c.isalnum())
        return f"slug:{clean_title}_{clean_artist}"

@dataclass
class PlaybackState:
    device_id: str
    device_name: str
    track_id: str
    track_title: str
    artist_name: str
    is_playing: bool
    progress_ms: int
    duration_ms: int

@dataclass
class FactorScore:
    dna_affinity: float      # Long-term taste score (0.0 to 1.0)
    live_context_fit: float  # Time/weather/road fit (0.0 to 1.0, capped at 35%)
    learned_preference: float # Bounded learning boost (-0.2 to +0.2)
    diversity_guard: float   # Variety bonus / fatigue penalty (-0.3 to +0.1)

    @property
    def composite_score(self) -> float:
        # Context influence capped at 35%
        capped_context = min(self.live_context_fit, 0.35)
        raw = (self.dna_affinity * 0.45) + capped_context + (self.learned_preference * 0.10) + (self.diversity_guard * 0.10)
        return max(0.01, min(0.99, raw))

@dataclass
class RecommendationDecision:
    decision_id: str
    track: Track
    confidence: float
    why_now: str
    factors: FactorScore
    context_summary: str
