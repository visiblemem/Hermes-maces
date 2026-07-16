# Hermes MACES Architecture

## Position in the Hermes stack

```text
Hermes Runtime
    ↓
Hermes Memory: episodic and personal continuity
    ↓
Obsidian / Wiki: approved explicit knowledge
    ↓
MACES: conceptual substrate and cognitive evolution
```

MACES is the deepest layer. It is not queried like a memory store during ordinary use. It receives normalized experience after tasks and returns only compact, bounded `InfluenceSignal` objects before later reasoning.

## Dual cognitive loop

```text
FAST LOOP — every meaningful task
Runtime → Experience → CognitiveEvent → Observe → Pattern / Gap update
   ▲                                                   │
   └──────────── advisory InfluenceSignal ─────────────┘

SLOW LOOP — event-count or schedule triggered
Conceptual Substrate → Consolidation → Contradiction / Decay / Gap ranking
        → LearningIntent → LearningStrategy → ResearchProvider
        → Evidence validation → Staging → PromotionProposal
        → ApprovalProvider → CanonicalProvider
        → new approved knowledge → future experience
```

The fast loop improves the next task without loading the complete substrate into context. The slow loop changes the system's long-term conceptual structure.

## Always-on core

Installation enables the complete safe core immediately:

- event normalization and idempotent observation;
- pattern, attention and confidence accumulation;
- epistemic-gap detection;
- learning-intent generation;
- influence-signal generation;
- staging isolation;
- append-only evolution history.

There are no activation levels. Availability of external actions is determined by installed capabilities.

## Capability bus

```text
CapabilityBus
├─ Runtime / Memory Adapters
├─ ResearchProvider
├─ ApprovalProvider
├─ CanonicalProvider
└─ Storage Provider boundary
```

Missing capabilities degrade naturally. Without research, a gap remains open. Without approval, a promotion remains a proposal. Without a canonical provider, nothing can leave Staging.

## Influence contract

MACES does not alter model weights, inject hidden facts or override routing. `InfluenceSignal` contains:

- attention priorities;
- known failure cautions;
- concepts requiring verification;
- optional reasoning suggestions;
- aggregate confidence.

The runtime may adopt or ignore each signal. Current user instructions and canonical knowledge always retain higher authority.

## Autonomous learning pipeline

```text
EpistemicGap
  → LearningIntent
  → LearningStrategy selects evidence classes and validation rules
  → CapabilityBus selects a compatible ResearchProvider
  → bounded multi-query research
  → provenance-preserving StagedArtifact
  → digest-bound PromotionProposal
  → external authorization
  → canonical write transaction
```

A learning strategy is domain-sensitive: construction favors manufacturer, engineering and code sources; software favors official documentation and repositories; brand research favors official publications, interviews and operational evidence.

## Authority and safety

1. Current user instruction.
2. Approved canonical knowledge.
3. Runtime policy and permissions.
4. Verified evidence.
5. Memory and episodic context.
6. MACES influence signals and inferred patterns.
7. Staged research and unresolved hypotheses.

MACES can influence reasoning only at levels 6–7. It cannot promote itself in this hierarchy.

## Persistence

The reference implementation uses SQLite WAL. Storage implementations must preserve event idempotency, proposal deduplication, append-only journal semantics, staging isolation and promotion digest integrity.
