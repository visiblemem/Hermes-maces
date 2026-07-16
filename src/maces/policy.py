from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MacesPolicy:
    reinforcement_alpha: float = 0.10
    correction_beta: float = 0.35
    decay_tau_days: float = 45.0
    weight_floor: float = 0.02
    outbound_edge_cap: float = 3.0
    interest_threshold: float = 0.60
    interest_cooldown_days: int = 14
    influence_max_items: int = 8
    influence_max_chars: int = 1200
    minimum_influence_weight: float = 0.10
    max_research_queries: int = 6
    max_sources: int = 12
    max_artifact_chars: int = 32_000

    def reinforce(self, weight: float) -> float:
        return min(1.0, weight + self.reinforcement_alpha * (1.0 - weight))

    def penalize(self, weight: float) -> float:
        return max(0.0, weight * (1.0 - self.correction_beta))
