# MACES Provider Development

MACES extends through structural Python protocols. Installing the package activates the safe cognitive core; providers add external capabilities.

## ResearchProvider

```python
class ResearchProvider(Protocol):
    name: str
    source_types: set[str]
    def research(self, plan: ResearchPlan) -> StagedArtifact: ...
```

A research provider must obey the supplied plan, preserve provenance, return only a staged artifact, and never write canonical knowledge.

## ApprovalProvider

```python
class ApprovalProvider(Protocol):
    name: str
    def approve_learning(self, intent: LearningIntent) -> bool: ...
    def authorize_promotion(self, proposal: PromotionProposal) -> str | None: ...
```

Promotion authorization should be digest-bound, scoped to the target and operation, attributable to an approver, and short-lived.

## CanonicalProvider

```python
class CanonicalProvider(Protocol):
    name: str
    def write(self, proposal, artifact, grant): ...
```

Canonical providers may target Obsidian, a wiki, a graph database, files or another system. They must validate the grant and proposal digest before writing.

## Registration

```python
bus = CapabilityBus()
bus.register(MyResearchProvider())
bus.register(MyApprovalProvider())
bus.register(MyObsidianProvider())
engine = MacesEngine(store, capabilities=bus)
```

`bus.capabilities()` reports what the installed system can currently perform. Missing providers do not disable observation, consolidation, gap detection or influence generation.

## Provider rules

- preserve source identity and timestamps;
- separate source text, extracted claims and model inference;
- enforce budgets and stop conditions;
- never convert staged material into canonical knowledge implicitly;
- remain replaceable without changing MACES core models.
