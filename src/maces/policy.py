from __future__ import annotations

from dataclasses import dataclass

from .models import ActivationLevel


@dataclass(frozen=True, slots=True)
class MacesPolicy:
    activation: ActivationLevel = ActivationLevel.SHADOW
    max_research_queries: int = 4
    max_sources: int = 8
    max_artifact_chars: int = 24_000
    allow_runtime_advice: bool = False

    def can_research(self) -> bool:
        return self.activation in {ActivationLevel.RESEARCH, ActivationLevel.PROMOTION}

    def can_propose_promotion(self) -> bool:
        return self.activation is ActivationLevel.PROMOTION

    def can_influence_runtime(self) -> bool:
        return self.activation in {
            ActivationLevel.ADVISORY,
            ActivationLevel.RESEARCH,
            ActivationLevel.PROMOTION,
        } and self.allow_runtime_advice

    def validate_research_budget(self, query_count: int, source_count: int) -> None:
        if query_count > self.max_research_queries:
            raise PermissionError("research query budget exceeded")
        if source_count > self.max_sources:
            raise PermissionError("research source budget exceeded")
