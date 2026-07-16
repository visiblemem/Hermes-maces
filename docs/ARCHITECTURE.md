# Hermes MACES Architecture

## Position

MACES is a general Hermes plugin installed under `~/.hermes/plugins/`. It is deeper than explicit memory but remains outside the authority chain.

```text
Hermes conscious system
├─ Runtime reasoning
├─ Session / episodic memory
├─ Obsidian / canonical knowledge
└─ Tools
       │ operator-driven traces
       ▼
MACES subconscious system
├─ weighted concept nodes
├─ association edges
├─ epistemic gaps
├─ staging darkroom
└─ append-only journal
       │
       ├─ Influence → pre_llm_call advisory context
       └─ Surfacing → proposal → external approval → canon
```

## Native plugin lifecycle

The repository root contains `plugin.yaml` and `__init__.py`. Hermes calls `register(ctx)`, which registers:

- `pre_llm_call` for bounded influence injection;
- `post_llm_call` for completed-turn traces;
- `post_tool_call` for retrieval/tool-use traces;
- `on_session_end` for decay consolidation;
- `maces_feedback` for explicit confirmation/correction events.

No Hermes core file is patched.

## Fast loop

```text
User message
→ extract candidate concepts
→ query node/edge/gap statistics
→ render ≤8 advisory items
→ Hermes reasons normally
→ completed turn and used tools become weak traces
```

Influence is ephemeral and is appended to the user message by Hermes's plugin hook system. It never modifies the system prompt or session history.

## Slow loop

```text
Explicit confirmation → asymptotic reinforcement
Explicit correction   → asymmetric penalty
Session end           → exponential decay + pruning
Co-occurrence         → association reinforcement + hub normalization
Gap observed          → learning proposal
Research result       → staging only
Useful staged result  → promotion proposal
Approval gate         → explicit memory / canon
```

## Dynamics

- `α = 0.10`: `w ← w + α(1 − w)`
- `β = 0.35`: `w ← w(1 − β)`
- `τ = 45 days`: `w ← w exp(−days/τ)`
- prune below `0.02`
- normalize outbound edge totals above `3.0`

A correction has more force than three ordinary confirmations. Repetition has diminishing returns. Forgetting is intentional.

## Statistics-only influence

The influence engine reads only:

- `patterns.label`, `patterns.weight`;
- `edges` and the labels of their endpoint nodes;
- open `gaps.topic` values.

It does not query `staged_artifacts`. This provides a structural prompt-injection barrier: autonomous research text cannot enter model context before approval.

## Authority

1. Current operator instruction
2. Approved canonical knowledge
3. Hermes runtime policy
4. Verified evidence
5. Explicit memory
6. MACES advisory statistics
7. Staged or unresolved material

MACES cannot promote itself upward in this hierarchy.

## Persistence and reversibility

The local SQLite database is disposable. It can be deleted without harming Hermes memory or Obsidian. The conscious system remains functional when the plugin is disabled or removed.
