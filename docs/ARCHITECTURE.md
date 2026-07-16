# Hermes MACES Architecture

## Purpose

MACES is a provider-neutral cognitive evolution substrate. It is not a memory store and it is not a canonical knowledge authority. It converts runtime and provider observations into machine-oriented cognitive state and governed learning work.

## Layers

```text
1. Agent Runtime
   - executes tasks
   - emits normalized or adapter-compatible events

2. Provider Adapters
   - normalize source-specific records
   - preserve source identity and authority
   - never promote or rewrite source data

3. Cognitive Substrate
   - pattern accumulation
   - epistemic gap detection
   - learning proposal queue
   - staging sandbox
   - evolution journal

4. External Governance
   - approves learning work
   - authorizes research budgets
   - issues digest-bound promotion grants

5. Canonical Providers
   - Obsidian, wiki, graph, database, files, or another system
   - remain outside MACES ownership
```

## Activation levels

| Level | Behavior |
|---|---|
| `off` | No processing |
| `shadow` | Observe and record only |
| `advisory` | May expose bounded suggestions to runtime |
| `research` | Approved learning proposals may create staged artifacts |
| `promotion` | May create promotion proposals, but cannot execute canonical writes |

## Authority model

MACES artifacts have advisory authority only. A pattern is a weighted observation, not a fact. A gap is an unresolved question, not proof of absence. A staged artifact is unapproved research. A promotion proposal is only a request addressed to an external approval system.

## Data flow

```text
raw provider/runtime event
        ↓ adapter
CognitiveEvent
        ↓ idempotent event log
pattern updates + gap updates
        ↓
deduplicated LearningProposal
        ↓ external approval
bounded research
        ↓
StagedArtifact
        ↓
PromotionProposal + digest
        ↓ external Approval Gate
canonical provider transaction
```

## Non-goals

- training or fine-tuning model weights;
- replacing the runtime router;
- owning user identity or permissions;
- silently browsing or learning without policy authorization;
- writing directly to canonical knowledge;
- coupling the architecture to a specific memory vendor.

## Initial implementation

The first implementation uses SQLite WAL for deterministic local state. Storage is an implementation detail behind `CognitiveStore`; future stores must preserve idempotency, append-only journal semantics, proposal deduplication, staging isolation, and promotion digest integrity.
