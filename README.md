# Hermes MACES

**The subconscious layer for Hermes.**

MACES sits beneath Hermes's existing memory architecture. It does not replace episodic memory, Obsidian, session history, tools, or the runtime. It passively absorbs operator-driven usage traces, consolidates weighted concepts and associations, detects epistemic gaps, and returns only compact advisory influence.

## Install

```bash
hermes plugins install jefferyzkj01/Hermes-maces --enable
```

Restart Hermes. No Python package installation, runtime patch, or manual hook wiring is required.

Hermes installs the repo into `~/.hermes/plugins/Hermes-maces/`, loads `plugin.yaml`, and calls the root `register(ctx)` entrypoint.

## Architecture

```text
User
  ↓
Hermes Runtime
  ├─ episodic/session memory
  ├─ Obsidian / canonical knowledge
  └─ tools
       ↓ usage traces
┌─────────────────────────────────────────┐
│ MACES — subconscious layer              │
│                                         │
│ Observe → reinforce / penalize → decay  │
│         → concept nodes + associations  │
│         → gaps → staging → proposals    │
└─────────────────────────────────────────┘
       │                         │
       │ Influence              │ Surfacing
       ▼                         ▼
pre_llm_call advisory block   external approval gate
       │                         │
       └────────→ Hermes      explicit memory / canon
```

MACES communicates with the conscious system through exactly two channels:

1. **Influence** — statistics-only advisory context, never facts and never staged content.
2. **Surfacing** — digest-bound promotion proposals; the only route from subconscious state to explicit memory.

## What happens automatically

After enablement, the plugin registers native Hermes hooks:

- `pre_llm_call` — emits a bounded `[intuition — advisory, unverified]` block.
- `post_llm_call` — absorbs completed-turn traces.
- `post_tool_call` — absorbs retrieval/tool usage traces.
- `maces_feedback` — records explicit operator `confirmed` or `corrected` feedback.

State is stored locally at:

```text
~/.hermes/plugins/hermes-maces/data/subconscious.db
```

The SQLite state is disposable and rebuildable from its append-only journal. It is never a source of truth.

## Learning dynamics

- Confirmation: `w ← w + 0.10 × (1 − w)`
- Correction: `w ← w × 0.65`
- Decay: `w ← w × exp(−days / 45)`
- Prune below `0.02`
- Co-occurring concepts form weighted association edges.
- Outbound association weight is capped to prevent hub collapse.
- Staging-originated material cannot reinforce itself.

## Safety invariants

- MACES never writes canon directly.
- MACES never originates tool calls.
- Influence never contains staged artifact text.
- Current user instructions and approved knowledge outrank every MACES signal.
- Disabling the plugin leaves normal Hermes behavior intact.
- Every state transition is journaled and replayable.

## Development

```bash
python -m pip install pytest ruff
PYTHONPATH=src pytest -q
ruff check src tests __init__.py
```

See [SUBCONSCIOUS.md](SUBCONSCIOUS.md) for the normative specification and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for implementation detail.
