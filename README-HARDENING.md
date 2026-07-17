# MACES 1.1 Runtime Hardening

MACES is an advisory subconscious layer. It is not Canon, does not write Obsidian, and does not replace Hindsight, profile `MEMORY.md`, or session history.

## Profile binding

Each plugin instance is bound once at `register(ctx)` from trusted `ctx.profile_name`. Hook kwargs, tool arguments, and feedback payloads cannot select or override a profile. State is stored below the instance data root as:

```text
<plugin-data>/<profile-name>/subconscious.db
```

No shared fallback profile is created. Registration fails when Hermes does not provide a trusted profile name.

## Learning signals

- `task.completed` records occurrence and co-occurrence only.
- `retrieval.used` is accepted only for successful tools and configured learnable fields. The default allowlist is empty.
- Confirmed/corrected feedback is not exposed as an LLM tool. When supported by Hermes, it is registered as the explicit `maces-feedback` command.
- Staging content is never queried by the influence engine.

## Privacy and reliability

All persistence paths pass through the secure store boundary. Secrets, credentials, JWTs, bearer tokens, emails, phone numbers, absolute paths, credential-bearing URLs, long identifiers, and high-entropy candidates are removed before SQLite writes. SQLite uses WAL, `busy_timeout`, bounded lock retries, and per-store serialization.

Influence queries use bounded SQL methods and emit at most four advisory items. Decay is persisted in metadata and runs at most once per 24 hours.

## Journal scope

The journal is an audit trail only. It does not guarantee complete event replay or database reconstruction.

## Disable, remove, and clear data

Disabling the plugin removes its hooks and leaves Hermes, Hindsight, and Obsidian behavior unchanged. To clear MACES state, stop Hermes and delete only the relevant profile directory beneath the MACES plugin data root. Do not delete Hindsight, Obsidian, or Hermes session databases.

## Validation

```bash
ruff check src tests __init__.py
pytest -q
```

Production rollout should begin in one profile using shadow mode before bounded influence is enabled broadly.
