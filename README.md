# Hermes MACES

**Modular Adaptive Cognitive Evolution System**

Hermes MACES is an install-and-run cognitive evolution plugin. It sits beneath Hermes memory and Obsidian knowledge, observes experience, consolidates machine-oriented cognition, detects epistemic gaps, generates bounded influence signals, and can extend itself through research, approval, memory, storage and canonical providers.

MACES does not replace Hermes Memory or Obsidian. They preserve experience and approved knowledge; MACES forms the deeper conceptual substrate that influences how the runtime approaches later tasks.

## Closed-loop architecture

```text
User → Hermes Runtime → Memory / Obsidian / Tools → Reasoning → Result
          ▲                                          │
          │                                          ▼
          └──── bounded InfluenceSignal ← MACES ← CognitiveEvent
                                      │
                    fast loop: observe → reflect → influence
                                      │
                    slow loop: consolidate → gap → learn
                                      │
              LearningStrategy → Research Provider → Staging
                                      │
              PromotionProposal → Approval Provider → Canon
```

## Install and use

```bash
python -m pip install -e '.[dev]'
pytest -q
```

MACES starts working as soon as the runtime emits events. There is no activation level.

```bash
maces --db var/maces.db observe event.json
maces --db var/maces.db influence commercial-display-design
maces --db var/maces.db capabilities
maces --db var/maces.db inspect gaps
```

Core capabilities are always available:

- event observation and idempotent replay;
- pattern and attention accumulation;
- epistemic gap detection;
- learning-intent generation;
- bounded subconscious influence signals;
- staging and evolution history.

External capabilities are discovered from installed providers:

- `ResearchProvider` performs autonomous evidence gathering;
- `ApprovalProvider` authorizes sensitive learning or promotion;
- `CanonicalProvider` writes approved artifacts to Obsidian, wiki, graph or another store;
- runtime and memory adapters normalize Hermes or third-party events.

When no research provider exists, MACES still detects and preserves the gap. When no canonical provider or approval grant exists, research remains in Staging.

## Safety invariants

- Influence signals are advisory priorities, not hidden facts or commands.
- Inferred patterns never override current user instructions or canonical knowledge.
- Research output is isolated in Staging.
- Canonical writes require a digest-bound promotion proposal and external authorization.
- Every event and state transition remains auditable and replayable.

## Documentation

- [Complete architecture](docs/ARCHITECTURE.md)
- [Provider development](docs/PROVIDERS.md)

## Status

Clean-room standalone implementation in `Hermes-maces`; it is intentionally separate from the previous Hermes memory-system repository.
