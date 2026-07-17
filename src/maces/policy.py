from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class MacesPolicy:
    reinforcement_alpha: float = 0.10
    retrieval_alpha: float = 0.03
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
    # Tool arguments are untrusted. A tool learns only from explicitly named
    # string fields; an absent tool name means an empty allowlist.
    learnable_tool_fields: dict[str, tuple[str, ...]] = field(default_factory=dict)

    def reinforce(self, weight: float) -> float:
        return min(1.0, weight + self.reinforcement_alpha * (1.0 - weight))

    def reinforce_retrieval(self, weight: float) -> float:
        return min(1.0, weight + self.retrieval_alpha * (1.0 - weight))

    def penalize(self, weight: float) -> float:
        return max(0.0, weight * (1.0 - self.correction_beta))

    def learnable_fields_for(self, tool_name: str) -> tuple[str, ...]:
        return self.learnable_tool_fields.get(tool_name, ())
