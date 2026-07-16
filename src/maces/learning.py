from __future__ import annotations

from dataclasses import dataclass

from .capabilities import CapabilityBus
from .models import LearningIntent, ResearchPlan, StagedArtifact
from .policy import MacesPolicy


@dataclass(slots=True)
class LearningStrategy:
    def plan(self, intent: LearningIntent) -> ResearchPlan:
        topic = intent.topic.strip()
        source_types = intent.required_evidence or ["primary"]
        queries = [
            topic,
            f"{topic} official documentation",
            f"{topic} implementation case study",
            f"{topic} limitations safety maintenance",
        ]
        return ResearchPlan(
            intent_id=intent.intent_id,
            topic=topic,
            queries=queries,
            source_types=source_types,
            validation_rules=[
                "prefer primary and official sources",
                "preserve source provenance",
                "separate evidence from inference",
                "record unresolved contradictions",
            ],
            stop_conditions=[
                "required evidence classes covered",
                "query budget exhausted",
                "no material new evidence found",
            ],
        )


class LearningExecutor:
    def __init__(self, bus: CapabilityBus, policy: MacesPolicy | None = None) -> None:
        self.bus = bus
        self.policy = policy or MacesPolicy()
        self.strategy = LearningStrategy()

    def execute(self, intent: LearningIntent) -> StagedArtifact | None:
        if self.policy.require_learning_approval:
            approved = any(provider.approve_learning(intent) for provider in self.bus.approvals)
            if not approved:
                return None
        plan = self.strategy.plan(intent)
        self.policy.validate_research_budget(len(plan.queries), self.policy.max_sources)
        provider = self.bus.select_research(plan.source_types)
        if provider is None:
            return None
        artifact = provider.research(plan)
        self.policy.validate_artifact(artifact.content)
        return artifact
