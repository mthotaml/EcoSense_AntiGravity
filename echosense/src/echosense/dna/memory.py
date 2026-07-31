"""
Cognitive Memory Store Engine
Supports Episodic Memory (timestamped experiences), Semantic Memory (subject-predicate propositions with supersession),
and Working Memory (short-lived expiring reasoning context).
"""

import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

class CognitiveMemoryStore:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.episodic_memories: List[Dict] = []
        self.semantic_memories: List[Dict] = []
        self.working_memories: List[Dict] = []

    def record_episode(self, experience: str, context: Dict, confidence: float = 0.9) -> Dict:
        """Record timestamped episodic experience."""
        memory = {
            "memory_id": f"ep_{uuid.uuid4().hex[:10]}",
            "user_id": self.user_id,
            "type": "episodic",
            "experience": experience,
            "context": context,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.episodic_memories.append(memory)
        return memory

    def record_semantic_proposition(self, subject: str, predicate: str, object_val: str, confidence: float = 0.85) -> Dict:
        """Record proposition about subject and predicate. Mark previous active propositions as superseded."""
        for prop in self.semantic_memories:
            if prop["subject"] == subject and prop["predicate"] == predicate and prop["status"] == "active":
                prop["status"] = "superseded"
                prop["superseded_at"] = datetime.utcnow().isoformat()

        memory = {
            "memory_id": f"sem_{uuid.uuid4().hex[:10]}",
            "user_id": self.user_id,
            "type": "semantic",
            "subject": subject,
            "predicate": predicate,
            "object": object_val,
            "confidence": confidence,
            "status": "active",
            "created_at": datetime.utcnow().isoformat()
        }
        self.semantic_memories.append(memory)
        return memory

    def set_working_context(self, key: str, value: str, ttl_minutes: int = 30) -> Dict:
        """Set short-lived expiring reasoning context in working memory."""
        expiry = datetime.utcnow() + timedelta(minutes=ttl_minutes)
        memory = {
            "memory_id": f"wm_{uuid.uuid4().hex[:10]}",
            "user_id": self.user_id,
            "type": "working",
            "key": key,
            "value": value,
            "expires_at": expiry.isoformat()
        }
        self.working_memories.append(memory)
        return memory

    def get_active_memories(self) -> Dict:
        """Retrieve user-scoped active memories capped at 100 entries."""
        now = datetime.utcnow().isoformat()
        active_wm = [m for m in self.working_memories if m.get("expires_at", "") > now]
        active_sem = [m for m in self.semantic_memories if m.get("status") == "active"]
        
        return {
            "user_id": self.user_id,
            "episodic": self.episodic_memories[-20:],
            "semantic": active_sem[-20:],
            "working": active_wm[-20:]
        }

    def delete_user_memories(self) -> int:
        """Consent-derived deletion of all cognitive memories."""
        count = len(self.episodic_memories) + len(self.semantic_memories) + len(self.working_memories)
        self.episodic_memories.clear()
        self.semantic_memories.clear()
        self.working_memories.clear()
        return count
