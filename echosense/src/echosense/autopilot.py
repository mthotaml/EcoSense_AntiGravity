"""
Continuous Music DNA Autopilot Queue Engine
Maintains 5 distinct tracks ahead, prevents duplicates, & handles queue replenishment.
"""

from typing import List, Set, Optional
from echosense.provider.models import Track, RecommendationDecision
from echosense.dna.ranker import ContextualRanker

class MusicDNAAutopilot:
    def __init__(self, ranker: ContextualRanker):
        self.ranker = ranker
        self.upcoming_queue: List[RecommendationDecision] = []
        self.history_track_ids: Set[str] = set()

    def maintain_queue(
        self,
        candidates: List[Track],
        context_data: dict,
        current_track_id: Optional[str] = None,
        target_size: int = 5
    ) -> List[RecommendationDecision]:
        """
        Maintain 5 distinct tracks ahead in the Autopilot queue (FR-10, AC-AUTO-02).
        Prevents already played or queued tracks from re-entering (AC-AUTO-05).
        """
        if current_track_id:
            self.history_track_ids.add(current_track_id)

        # Exclude queued and historic tracks
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

        return self.upcoming_queue[:target_size]

    def consume_next(self) -> Optional[RecommendationDecision]:
        """Advance queue when current track ends or is skipped."""
        if self.upcoming_queue:
            next_decision = self.upcoming_queue.pop(0)
            self.history_track_ids.add(next_decision.track.id)
            return next_decision
        return None
