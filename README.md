# Hermes MACES

> **Status: Public Beta. Install in shadow mode first.** MACES learns local advisory
> signals; it does not train model weights or replace Hermes memory providers.
> It is not production-ready until a real multi-day Shadow validation report is PASS.

MACES is a **profile-bound, low-weight, unverified advisory layer** for Hermes Agent. It records bounded preference signals, concept associations, Traditional Chinese candidates, and epistemic gaps. It does not replace Hindsight, profile memory, session history, or Obsidian/LLM Wiki, and it never writes Canon directly.

## Safety contract

- Obsidian/LLM Wiki remains the only formal knowledge Canon.
- Hindsight remains responsible for conversational and experiential memory.
- MACES state is disposable advisory state, never a source of truth.
- MACES does not train, fine-tune, or modify model weights.
- Model output cannot confirm or correct a MACES concept.
- MACES never originates tool calls or modifies the Hermes system prompt.
- The default is `shadow_mode: true` with an empty `learnable_tool_fields` allowlist.
- Disabling the plugin removes its hooks without changing Hermes core, Hindsight, Obsidian, Session SQLite, `USER.md`, or `MEMORY.md`.

## Verified compatibility and installer behavior

- Verified Hermes host baseline: `hermes-agent==0.18.2`.
- CI covers Python 3.11, 3.12, and 3.13 on Ubuntu and macOS.
- The blocking real-PluginManager E2E remains pinned to Hermes Agent 0.18.2 and Python 3.11.
- `hermes plugins install owner/repo` shallow-clones the repository's default branch. It does **not** pin a GitHub Release tag.
- `main` is therefore the version users actually install and must contain only reviewed, CI-green releaseable commits.
- Read [`CHANGELOG.md`](CHANGELOG.md) before updating an existing installation.

Windows and Hermes versions other than the listed baseline are not yet part of the verified compatibility matrix.

## Install one profile at a time

1. Select one profile and install without enabling:

   ```bash
   hermes profile use default
   hermes plugins install jefferyzkj01/Hermes-maces --no-enable
   ```

2. Back up the active profile's Hermes `config.yaml`.
3. Copy the safe defaults from [`config.example.yaml`](config.example.yaml) into that profile's config.
4. Keep `shadow_mode: true` and `learnable_tool_fields: {}` until fields have been reviewed.
5. Add only two or three reviewed retrieval tools and safe query-like string fields for a meaningful Shadow evaluation.
6. Enable the plugin and restart the gateway:

   ```bash
   hermes plugins enable hermes-maces --no-allow-tool-override
   hermes gateway restart
   ```

7. Confirm that the only MACES state directory is:

   ```text
   <active-profile-HERMES_HOME>/data/maces/
   ```

8. Run Shadow validation for at least seven days before considering bounded influence.

MACES resolves the active profile through trusted `ctx.profile_name` and `hermes_constants.get_hermes_home()`. Its database is:

```text
<active-profile-HERMES_HOME>/data/maces/subconscious.db
```

The plugin checkout must not contain a live database. On first registration, a legacy checkout database is moved into the active profile data directory and the transition is recorded as a `migration` audit event.

## Safe default configuration

```yaml
plugins:
  enabled:
    - hermes-maces
  entries:
    hermes-maces:
      shadow_mode: true
      influence:
        max_items: 4
        max_chars: 700
        minimum_weight: 0.10
      learnable_tool_fields: {}
      limits:
        max_patterns: 5000
        max_edges: 20000
        max_open_gaps: 500
        max_candidates: 5000
      maintenance:
        decay_interval_hours: 24
        prune_batch_size: 500
      traditional_chinese:
        candidate_min_sessions: 3
        stopwords:
          - 我們
          - 你們
          - 這個
          - 那個
```

All numeric values are bounded. Invalid settings force MACES into shadow mode and log a warning; they do not prevent Hermes from starting. The repository does not contain a user `config.yaml`, so plugin updates cannot overwrite profile behavior settings.

### Reviewed Shadow allowlist example

After reviewing the tools and confirming that only query-like strings are exposed, a single-profile Shadow test may explicitly add:

```yaml
learnable_tool_fields:
  session_search:
    - query
  web_search:
    - query
```

This is not the default. Do not allowlist write tools, file contents, credentials, paths, complete result bodies, or arbitrary unreviewed fields.

### Tool-learning gate

A tool call can reinforce concepts only when all of the following are true:

```text
status == "ok"
error_type is None
tool_name is present in learnable_tool_fields
```

Only explicitly listed safe string fields are read. Full arguments and result bodies are never persisted. Failed, cancelled, approval-denied, unlisted, or status-ambiguous calls do not create a positive signal.

### Traditional Chinese learning

Passive Traditional Chinese text uses a two-stage path:

1. a bounded complete concept becomes a low-weight candidate;
2. it becomes a zero-weight pattern only after recurring in at least three distinct sessions.

Candidates never enter influence. Explicit operator feedback or a validated successful retrieval can create the complete concept immediately. Configurable stopwords and bounded negation prefixes such as `不要`, `別`, `不喜歡`, and `避免` suppress candidate creation. MACES does not call an additional model for extraction.

## Slash commands

Feedback is available only as an explicit operator command, never as a model tool:

```text
/maces-feedback confirmed 美學,建築設計
/maces-feedback corrected 過度留白,紫色漸層
/maces-status
/maces-top 10
```

Invalid feedback returns usage text and writes nothing. Status output is aggregate-only and never displays raw sensitive material.

## Shadow rollout

Keep `shadow_mode: true` for at least seven days and satisfy the minimum evidence requirements in [`docs/PUBLIC_RELEASE_GUIDE.md`](docs/PUBLIC_RELEASE_GUIDE.md). Shadow mode records safe signals but injects no advisory context.

The de-identified report belongs in [`docs/PUBLIC_BETA_VALIDATION.md`](docs/PUBLIC_BETA_VALIDATION.md). Do not record raw conversations, complete patterns, real paths, session IDs, credentials, email addresses, or database contents.

A nearly empty high-weight table is expected under strict valenced learning. If fewer than ten reviewable patterns are produced, extend Shadow instead of weakening the learning gate.

## Known limitations

- Patterns are speculative advisory signals, not facts.
- Strict learning gates may produce little data; this is expected behavior.
- Traditional Chinese segmentation uses bounded rules and is not full semantic understanding.
- Only the listed Hermes, Python, and operating-system combinations are verified.
- Every profile must complete its own Shadow validation.
- Unsafe user-added allowlist fields can expand privacy risk.
- `main` is the installer source, so updates should follow the Changelog and CI status.
- MACES provides no cloud sync, cross-device synchronization, or remote backup.
- Promotion remains proposal-only; MACES does not automatically write Obsidian or another Canon.

## Privacy and reliability

Every persistence path crosses `maces.secure_store.CognitiveStore`. It scrubs credentials, tokens, JWT/Bearer values, email addresses, phone and long-digit shapes, absolute paths, sensitive URLs, long identifiers, and high-entropy candidates before SQLite writes.

SQLite uses WAL, a busy timeout, per-store serialization, and bounded whole-transaction retries on fresh connections. Influence reads only bounded indexed queries and emits at most the configured item and character budgets. Staged research content is never queried by the influence engine.

Report suspected credential retention, profile-boundary violations, path disclosure, or unintended Canon writes through the private process described in [`docs/SECURITY.md`](docs/SECURITY.md). Never upload a real MACES database, Vault, Session SQLite file, credential, or private absolute path.

## Disable, remove, and clear data

Disable first:

```bash
hermes plugins disable hermes-maces
hermes gateway restart
```

Confirm ordinary Hermes behavior, Hindsight recall, Canon files, Session SQLite, and profile memory remain normal. Preserve the MACES database for local investigation.

Remove the plugin only after that verification:

```bash
hermes plugins remove hermes-maces
```

To clear MACES state, stop the gateway, verify the active profile, and delete only:

```text
<active-profile-HERMES_HOME>/data/maces/
```

Never delete Hindsight data, Obsidian, Hermes Session SQLite, `USER.md`, `MEMORY.md`, or Hermes core files as part of MACES cleanup.

## Development and release checks

```bash
python -m pip install -e '.[dev]'
ruff check src tests __init__.py
python -m compileall -q src __init__.py
pytest -q -m "not e2e"
python -m pip install 'hermes-agent==0.18.2'
pytest -q -m e2e
python -m pip install build twine
python -m build
python -m twine check dist/*
```

See [`SUBCONSCIOUS.md`](SUBCONSCIOUS.md), [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md), [`docs/SECURITY.md`](docs/SECURITY.md), [`docs/INSTALLATION.md`](docs/INSTALLATION.md), and [`docs/PUBLIC_RELEASE_GUIDE.md`](docs/PUBLIC_RELEASE_GUIDE.md).
