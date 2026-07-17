from __future__ import annotations

from hashlib import sha256

from .models import InfluenceSignal
from .policy import MacesPolicy
from .store import CognitiveStore
from .validation import is_valid_pattern_label


def _key(value: str) -> str:
    return sha256(value.strip().lower().encode()).hexdigest()[:24]


class InfluenceEngine:
    def __init__(self, store: CognitiveStore, policy: MacesPolicy | None = None) -> None:
        self.store = store
        self.policy = policy or MacesPolicy()

    def signal(self, concepts: list[str]) -> InfluenceSignal:
        patterns = self.store.list_table("patterns")
        edges = self.store.list_table("edges")
        gaps = self.store.list_table("gaps")
        wanted = {_key(c): c.strip().lower() for c in concepts if c.strip()}

        # Validate persisted labels again at the output boundary so hostile legacy
        # rows can never be rendered into an LLM prompt.
        safe_patterns = [r for r in patterns if is_valid_pattern_label(str(r["label"]))]
        relevant = [r for r in safe_patterns if r["pattern_key"] in wanted]
        if not relevant:
            relevant = sorted(safe_patterns, key=lambda r: float(r["weight"]), reverse=True)[:2]

        attention_candidates = [
            (str(r["label"]), float(r["weight"]))
            for r in sorted(relevant, key=lambda r: float(r["weight"]), reverse=True)
            if float(r["weight"]) >= self.policy.minimum_influence_weight
        ]

        # Edges only expand from nodes that already carry enough node weight.
        # Mention-only edges cannot promote a zero-weight node into attention.
        weighted_keys = {
            r["pattern_key"]
            for r in safe_patterns
            if float(r["weight"]) >= self.policy.minimum_influence_weight
        }
        labels = {r["pattern_key"]: r["label"] for r in safe_patterns}
        connected = [
            r
            for r in edges
            if (r["key_a"] in wanted or r["key_b"] in wanted)
            and r["key_a"] in weighted_keys
            and r["key_b"] in weighted_keys
        ]
        association_candidates = [
            (str(labels[r["key_a"]]), str(labels[r["key_b"]]), float(r["weight"]))
            for r in sorted(connected, key=lambda r: float(r["weight"]), reverse=True)
            if float(r["weight"]) >= self.policy.minimum_influence_weight
        ]
        verify_candidates = [str(r["topic"]) for r in gaps if r["status"] == "open"]

        remaining = self.policy.influence_max_items
        attention = attention_candidates[:remaining]
        remaining -= len(attention)
        associations = association_candidates[:remaining]
        remaining -= len(associations)
        verify = verify_candidates[:remaining]

        values = [w for _, w in attention] + [w for _, _, w in associations]
        signal = InfluenceSignal(
            attention,
            associations,
            verify,
            sum(values) / len(values) if values else 0.0,
        )
        while signal.render() and len(signal.render()) > self.policy.influence_max_chars:
            if signal.verify:
                signal.verify.pop()
            elif signal.associations:
                signal.associations.pop()
            elif signal.attention:
                signal.attention.pop()
            else:
                break
        return signal
