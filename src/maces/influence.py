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
        wanted = {_key(c): c.strip().lower() for c in concepts if c.strip()}
        query_limit = max(self.policy.influence_max_items * 4, 8)
        patterns = self.store.get_relevant_patterns(list(wanted), query_limit)
        safe_patterns = [r for r in patterns if is_valid_pattern_label(str(r["label"]))]
        relevant = [r for r in safe_patterns if r["pattern_key"] in wanted]
        if not relevant:
            relevant = safe_patterns[:2]

        attention_candidates = [
            (str(r["label"]), float(r["weight"]))
            for r in relevant
            if float(r["weight"]) >= self.policy.minimum_influence_weight
        ]

        edges = self.store.get_connected_edges(list(wanted), query_limit)
        endpoint_keys = {str(r["key_a"]) for r in edges} | {str(r["key_b"]) for r in edges}
        endpoint_patterns = self.store.get_relevant_patterns(list(endpoint_keys), query_limit * 2)
        safe_endpoints = [r for r in endpoint_patterns if is_valid_pattern_label(str(r["label"]))]
        weighted_keys = {
            str(r["pattern_key"])
            for r in safe_endpoints
            if float(r["weight"]) >= self.policy.minimum_influence_weight
        }
        labels = {str(r["pattern_key"]): str(r["label"]) for r in safe_endpoints}
        association_candidates = [
            (labels[str(r["key_a"])], labels[str(r["key_b"])], float(r["weight"]))
            for r in edges
            if str(r["key_a"]) in weighted_keys
            and str(r["key_b"]) in weighted_keys
            and float(r["weight"]) >= self.policy.minimum_influence_weight
        ]
        verify_candidates = [
            str(r["topic"]) for r in self.store.get_open_gaps(query_limit)
        ]

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
