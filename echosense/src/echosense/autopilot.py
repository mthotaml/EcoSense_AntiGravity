"""
Continuous Music DNA Autopilot Queue Engine
Maintains continuous dynamic queue of arbitrary depth (15-20+ tracks), prevents duplicates,
handles automatic candidate replenishment, and provides pagination slicing (FR-10, AC-AUTO-02).
"""

import math
from typing import List, Set, Optional, Dict, Tuple
from echosense.provider.models import Track, RecommendationDecision, FactorScore
from echosense.dna.ranker import ContextualRanker

class MusicDNAAutopilot:
    def __init__(self, ranker: ContextualRanker):
        self.ranker = ranker
        self.upcoming_queue: List[RecommendationDecision] = []
        self.history_track_ids: Set[str] = set()
        self.is_enabled: bool = True

    def maintain_queue(
        self,
        candidates: List[Track],
        context_data: dict,
        current_track_id: Optional[str] = None,
        target_size: int = 20
    ) -> List[RecommendationDecision]:
        """
        Maintain continuous dynamic queue up to target_size (default 20 tracks).
        If is_enabled is False, streams tracks directly from connected Spotify service.
        """
        if not self.is_enabled:
            # Direct Spotify Mode: bypass DNA queue ranking
            direct_decisions = []
            for idx, track in enumerate(candidates[:target_size]):
                direct_decisions.append(RecommendationDecision(
                    decision_id=f"direct_{track.id}_{idx}",
                    track=track,
                    confidence=1.0,
                    why_now="Direct Spotify Streaming • DNA Autopilot OFF",
                    factors=FactorScore(
                        dna_affinity=1.0,
                        live_context_fit=1.0,
                        learned_preference=0.0,
                        diversity_guard=1.0
                    ),
                    context_summary="Direct Spotify Stream"
                ))
            self.upcoming_queue = direct_decisions
            return self.upcoming_queue

        if current_track_id:
            self.history_track_ids.add(current_track_id)

        # Exclude currently queued and historic tracks
        existing_queued_ids = {d.track.id for d in self.upcoming_queue}
        excluded_ids = existing_queued_ids.union(self.history_track_ids)

        new_decisions = self.ranker.rank_candidates(
            candidates=candidates,
            context_data=context_data,
            current_track_id=current_track_id,
            queued_track_ids=excluded_ids
        )

        # Replenish queue up to target_size
        needed = target_size - len(self.upcoming_queue)
        if needed > 0 and new_decisions:
            self.upcoming_queue.extend(new_decisions[:needed])

        # Fallback continuous replenishment if queue is under target_size
        attempts = 0
        while len(self.upcoming_queue) < target_size and attempts < 3:
            attempts += 1
            # Reset history to allow fresh cycling of candidates
            self.history_track_ids.clear()
            fallback_queued = {d.track.id for d in self.upcoming_queue}
            fallback_decisions = self.ranker.rank_candidates(
                candidates=candidates,
                context_data=context_data,
                current_track_id=current_track_id,
                queued_track_ids=fallback_queued
            )
            still_needed = target_size - len(self.upcoming_queue)
            if fallback_decisions:
                # Add unique decision IDs
                for fb in fallback_decisions:
                    if len(self.upcoming_queue) >= target_size:
                        break
                    fb_copy = RecommendationDecision(
                        decision_id=f"{fb.decision_id}_r{attempts}",
                        track=fb.track,
                        confidence=fb.confidence,
                        why_now=fb.why_now,
                        factors=fb.factors,
                        context_summary=fb.context_summary
                    )
                    self.upcoming_queue.append(fb_copy)
            else:
                break

        return self.upcoming_queue

    def get_paginated_queue(self, page: int = 1, page_size: int = 5) -> Tuple[List[RecommendationDecision], int, int, int, int]:
        """
        Return paginated slice of the active Autopilot queue along with metadata.
        Returns (items, page, page_size, total_pages, total_items).
        """
        total_items = len(self.upcoming_queue)
        page_size = max(1, page_size)
        total_pages = max(1, math.ceil(total_items / page_size))
        
        # Clamp page range
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_items = self.upcoming_queue[start_idx:end_idx]
        
        return page_items, page, page_size, total_pages, total_items

    def consume_next(self) -> Optional[RecommendationDecision]:
        """Advance queue when current track ends or is skipped."""
        if self.upcoming_queue:
            next_decision = self.upcoming_queue.pop(0)
            self.history_track_ids.add(next_decision.track.id)
            return next_decision
        return None
