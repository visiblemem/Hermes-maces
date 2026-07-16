from __future__ import annotations

from .models import InfluenceSignal
from .policy import MacesPolicy
from .store import CognitiveStore


class InfluenceEngine:
    def __init__(self, store: CognitiveStore, policy: MacesPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or MacesPolicy()

    def signal(self, subject: str) -> InfluenceSignal:
        patterns = self.store.list_table("patterns")
        gaps = self.store.list_table("gaps")
        ranked = sorted(
            (row for row in patterns if float(row.get("weight", 0)) >= self.policy.minimum_pattern_weight),
            key=lambda row: float(row.get("weight", 0)),
            reverse=True,
        )[: self.policy.max_influence_items]
        attention = {str(row.get("label")): float(row.get("weight", 0)) for row in ranked}
        open_gaps = [
            str(row.get("topic"))
            for row in gaps
            if str(row.get("status", "open")) in {"open", "researching"}
        ][: self.policy.max_influence_items]
        confidence = min(1.0, sum(attention.values()) / max(1, len(attention)))
        return InfluenceSignal(
            subject=subject,
            attention=attention,
            cautions=[f"Unresolved knowledge gap: {topic}" for topic in open_gaps],
            verify=open_gaps,
            suggestions=["Use these signals as advisory priorities, never as facts."],
            confidence=confidence,
        )
