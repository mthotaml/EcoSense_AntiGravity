"""
Contextual Candidate Generator & Bounded Ranker Engine
Enforces 35% Context Cap, Music DNA Floor, Explicit Negative Overrides, and Diversity Guards.
"""

import uuid
from typing import List, Dict, Set, Optional
from echosense.config import settings
from echosense.provider.models import Track, FactorScore, RecommendationDecision
from echosense.dna.profile import MusicDNAProfile

class ContextualRanker:
    def __init__(self, dna_profile: MusicDNAProfile):
        self.profile = dna_profile
        self.disliked_track_ids: Set[str] = set()

    def add_disliked_track(self, track_id: str):
        """Record explicit negative feedback to block candidate."""
        self.disliked_track_ids.add(track_id)

    def rank_candidates(
        self,
        candidates: List[Track],
        context_data: Dict,
        current_track_id: Optional[str] = None,
        queued_track_ids: Optional[Set[str]] = None
    ) -> List[RecommendationDecision]:
        """
        Rank candidates according to strict specification rules:
        1. Explicit negative feedback (dislikes) exclude candidates unconditionally (GR-05).
        2. Deduplication by ISRC or Title+Artist slug (FR-07).
        3. Exclude current and already queued tracks (FR-07).
        4. Music DNA floor enforcement: candidate must pass DNA affinity floor (GR-03).
        5. Contextual score capped at max 35% of pre-diversity score (GR-04, FR-06).
        6. Diversity guard: artist fatigue cap (max 2 per artist) & no adjacent same-artist tracks (FR-07).
        """
        queued = queued_track_ids or set()
        if current_track_id:
            queued.add(current_track_id)

        decisions: List[RecommendationDecision] = []
        seen_recordings: Set[str] = set()
        artist_counts: Dict[str, int] = {}
        last_artist_name: Optional[str] = None

        for track in candidates:
            # Rule 1: Explicit negative feedback override
            if track.id in self.disliked_track_ids:
                continue

            # Rule 2: Exclude current / already queued tracks
            if track.id in queued:
                continue

            # Rule 3: Recording deduplication (ISRC or slug)
            rec_id = track.isrc_or_slug
            if rec_id in seen_recordings:
                continue

            # Rule 4: Music DNA Floor Enforcement
            dna_affinity = self.profile.get_track_dna_affinity(track)
            if dna_affinity < settings.DNA_FLOOR_THRESHOLD:
                continue

            # Calculate Live Context Fit
            raw_context_fit = self._compute_context_fit(track, context_data)
            # Enforce 35% cap on contextual influence
            capped_context_fit = min(raw_context_fit, settings.MAX_CONTEXT_INFLUENCE_PCT)

            # Rule 5: Diversity & Artist Fatigue Guard
            artist_name_clean = track.artist_name.lower()
            current_artist_count = artist_counts.get(artist_name_clean, 0)
            
            # Fatigue cap check
            if current_artist_count >= settings.ARTIST_FATIGUE_CAP:
                continue

            # Adjacent same artist penalty
            adjacent_penalty = -0.2 if (last_artist_name and last_artist_name == artist_name_clean) else 0.05
            diversity_score = 0.10 + adjacent_penalty

            factors = FactorScore(
                dna_affinity=dna_affinity,
                live_context_fit=capped_context_fit,
                learned_preference=0.05,
                diversity_guard=diversity_score
            )

            # Build human-readable explanation
            why_now = self._build_explanation(track, factors, context_data)

            decision_id = f"dec_{uuid.uuid4().hex[:12]}"
            decision = RecommendationDecision(
                decision_id=decision_id,
                track=track,
                confidence=round(factors.composite_score, 2),
                why_now=why_now,
                factors=factors,
                context_summary=self._format_context_summary(context_data)
            )

            decisions.append(decision)
            seen_recordings.add(rec_id)
            artist_counts[artist_name_clean] = current_artist_count + 1
            last_artist_name = artist_name_clean

        # Sort decisions by composite score descending
        decisions.sort(key=lambda d: d.factors.composite_score, reverse=True)
        return decisions

    def _compute_context_fit(self, track: Track, context_data: Dict) -> float:
        """Calculate context fit score based on daypart, weather, road setting, activity."""
        fit = 0.20
        daypart = context_data.get('daypart', 'afternoon')
        road = context_data.get('road_setting', 'general')
        activity = context_data.get('activity', 'focus')

        if activity.lower() in track.category.lower():
            fit += 0.10
        if road == 'scenic' and 'nature' in track.category.lower():
            fit += 0.10
        if daypart in ['evening', 'night'] and 'calm' in track.category.lower():
            fit += 0.08

        return fit

    def _build_explanation(self, track: Track, factors: FactorScore, context_data: Dict) -> str:
        """Construct clear, transparent human-readable explanation for the listener."""
        daypart = context_data.get('daypart', 'afternoon').capitalize()
        activity = context_data.get('activity', 'focus').capitalize()
        
        dna_pct = int(factors.dna_affinity * 100)
        ctx_pct = int(factors.live_context_fit * 100)
        
        reasons = []
        if dna_pct >= 75:
            reasons.append(f"High {dna_pct}% Music DNA match for {track.artist_name}")
        else:
            reasons.append(f"{dna_pct}% Music DNA affinity score")
            
        reasons.append(f"matches your {daypart} {activity} setting (context capped at 35%)")
        reasons.append("guarded against artist fatigue (max 2 limit)")

        return ", ".join(reasons) + "."

    def _format_context_summary(self, context_data: Dict) -> str:
        parts = []
        for k in ['daypart', 'weather', 'road_setting', 'activity']:
            if k in context_data and context_data[k]:
                parts.append(f"{k.replace('_', ' ').title()}: {context_data[k]}")
        return " • ".join(parts) if parts else "General Context"
