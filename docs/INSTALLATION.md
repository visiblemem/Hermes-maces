# Installation and Operations

## Preconditions

Record the Hermes version and MACES commit, record configuration changes and rollback information under the operator's backup policy, verify Hindsight health, and record hashes for profile memory. Do not copy live session databases just to install MACES. Install only one profile at a time.

## Install without enabling

```bash
hermes profile use default
hermes plugins install visiblemem/Hermes-maces --ref <RUNTIME_COMMIT_SHA> --no-enable
```

Use a reviewed runtime-distribution SHA as described in [Runtime distribution](RUNTIME_DISTRIBUTION.md). Verify that local CLI help supports `--ref`. Keep security scanning enabled; do not force a blocked development checkout into production.

Add the `plugins.entries.hermes-maces` section from `config.example.yaml` to the active profile's Hermes configuration. Do not use a `config.yaml` inside the repository as user configuration.

Optionally populate a small allowlist for two or three reviewed retrieval tools to evaluate occurrence extraction. Retrievals never create preference weight. Meaningful non-zero influence evaluation requires explicit operator feedback, regardless of the allowlist.

## Enable in shadow mode

```bash
hermes plugins enable hermes-maces
hermes gateway restart
```

Keep `shadow_mode: true`. Verify that the only new database is:

```text
<profile-HERMES_HOME>/data/maces/subconscious.db
```

Run shadow for at least seven days. Acceptance is based on privacy, concept quality, negation behavior, latency, profile placement, and host stability—not on learning volume.

## Enable influence

After human review, set `shadow_mode: false` for this profile and restart its gateway. Advisory output remains bounded to the configured limits and explicitly unverified.

## Observe

Use `/maces-status` for aggregate profile, shadow, table, database, decay, error, scrub, and latest influence metrics. Use `/maces-top [1-20]` for validated high-weight labels only.

## Roll back

```bash
hermes plugins disable hermes-maces
hermes gateway restart
```

Verify Hermes conversation, Hindsight recall, Obsidian, session SQLite, and profile memory. Keep MACES SQLite for inspection. Remove the plugin only after ordinary behavior is confirmed.

To wipe only MACES state, stop Hermes and delete `<profile-HERMES_HOME>/data/maces/`.
