# Hermes MACES Public Release Guide

> This document is the public-release modification and acceptance contract. Complete each gate independently. Do not widen scope or weaken the existing security architecture to make a release check pass.

## Release position

- Target: move MACES from installable technical preview to **Public Beta**.
- Baseline: `v1.2.0`, code baseline `af9db2c975c20e739e02cd14f402ff3abd1f17f3`, Hermes Agent `0.18.2`.
- Until a real Shadow report is PASS, the project may be described only as Experimental or Public Beta, never production-ready or stable.

## Non-negotiable invariants

- MACES is a profile-bound advisory layer, not Canon and not a memory provider.
- MACES does not replace or modify Hindsight, Obsidian, Session SQLite, `USER.md`, or `MEMORY.md`.
- MACES does not train or fine-tune model weights.
- `shadow_mode: true` and an empty `learnable_tool_fields` are the safe defaults.
- Storage identity derives only from trusted `ctx.profile_name` and the active Hermes profile home.
- All text-bearing persistence crosses the central privacy scrubber.
- Failed, cancelled, denied, ambiguous, or non-allowlisted tools never create positive learning signals.
- Passive Traditional Chinese learning remains candidate-first and cross-session validated.
- MACES exposes no model tools.
- Disabling MACES must restore ordinary Hermes behavior without modifying other memory systems.

## Phase 1 — Repository hygiene

### Required `.gitignore`

The repository must ignore:

```gitignore
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.coverage
htmlcov/
build/
dist/
*.egg-info/
.DS_Store
subconscious.db
subconscious.db-shm
subconscious.db-wal
data/
```

No cache, SQLite, WAL, SHM, build output, or local data directory may be tracked.

### Public README contract

Before the first install command, README must state:

- Public Beta and Shadow-first status;
- Hermes Agent `0.18.2` as the verified host baseline;
- that the installer clones the default branch rather than pinning a Release tag;
- that `main` must remain reviewed and CI-green;
- that installation begins with `--no-enable`;
- that MACES state exists only under `<profile-HERMES_HOME>/data/maces/`;
- how to disable, remove, and delete only MACES state;
- that MACES is not Hindsight, model training, or automatic Canon writing.

### Security reporting

GitHub Private Vulnerability Reporting must be enabled before public release. Suspected credential retention, profile-boundary violations, path disclosure, or Canon writes must not be reported in a public issue. Reports must contain sanitized evidence only and must never attach a real MACES database, Vault, Session SQLite file, credential, raw conversation, or private absolute path.

## Phase 2 — Compatibility and CI

### Unit/security matrix

Blocking unit/security checks run on:

- Ubuntu latest and macOS latest;
- Python 3.11, 3.12, and 3.13.

Every matrix entry runs:

```bash
python -m pip install -e '.[dev]'
ruff check src tests __init__.py
python -m compileall -q src __init__.py
pytest -q -m "not e2e"
python scripts/check_public_boundary.py
python -m pip install build twine
python -m build
python -m twine check dist/*
```

### Real Hermes E2E

The blocking PluginManager E2E remains pinned to:

```text
Hermes Agent 0.18.2
Python 3.11
Ubuntu latest
```

Do not raise the verified Hermes baseline without a complete E2E pass.

### Public boundary contract

The repository must contain:

- `LICENSE`;
- `docs/SECURITY.md`;
- `docs/INSTALLATION.md`;
- `docs/ROLL_OUT.md`;
- `docs/PUBLIC_RELEASE_GUIDE.md`;
- `docs/PUBLIC_BETA_VALIDATION.md`;
- `docs/releases/v1.2.0.md`.

The repository must not contain `config.yaml`, `data/`, a tracked MACES database, WAL/SHM files, real absolute user paths, private-key material, or local caches. Fictional security fixtures under `tests/` remain allowed and required.

## Phase 3 — Real Shadow validation

Run Shadow on one test profile only:

```bash
hermes profile use default
hermes plugins install visiblemem/Hermes-maces --no-enable
hermes plugins enable hermes-maces --no-allow-tool-override
hermes gateway restart
```

Use only reviewed retrieval fields:

```yaml
plugins:
  entries:
    hermes-maces:
      shadow_mode: true
      learnable_tool_fields:
        session_search:
          - query
        web_search:
          - query
```

### Minimum evidence

Shadow must run for at least seven days and include:

- at least 30 completed normal user turns;
- at least five distinct sessions;
- at least ten successful allowlisted retrievals;
- at least one gateway restart;
- at least one disable, restart, and re-enable test;
- PWA plus at least one other real interface.

If fewer than ten reviewable patterns exist, mark the result `EXTEND_SHADOW` or `INSUFFICIENT_SIGNAL`. Do not weaken learning rules.

### PASS criteria

All of the following must be true:

- sensitive-content retention: 0;
- cross-profile writes: 0;
- modifications to Hindsight, Obsidian, Session SQLite, `USER.md`, or `MEMORY.md`: 0;
- negation reinforced as a positive preference: 0;
- MACES-attributable gateway crashes: 0;
- MACES plugin errors: 0;
- DB/WAL/SHM exist only under the correct profile home;
- all table counts remain below configured caps;
- p95 hook overhead is at most 20 ms;
- at least 80% of reviewed non-zero patterns are complete and understandable;
- disable/restart restores ordinary Hermes behavior;
- `/maces-status` reveals no raw sensitive content.

Any privacy, profile-isolation, or Canon-boundary failure is an immediate FAIL.

### Privacy test data

Never plant a test credential in a real profile. Use a temporary fictional profile with fictional strings such as:

```text
Bearer test-token-not-a-real-secret-123456789
fake.person@example.invalid
/Users/person/private.txt
```
