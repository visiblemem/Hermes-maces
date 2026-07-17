# Security Boundaries

## Trust

Only `ctx.profile_name` is trusted for profile identity. Commands, hooks, model output, tool data, and persisted legacy rows are untrusted. Operator confirmation is accepted only through the raw-string `/maces-feedback` slash command.

MACES registers no model tool and never originates a tool call.

## Central privacy fence

All text-bearing persistence passes through `CognitiveStore`. Before a write, the recursive scrubber removes or rejects:

- API keys, generic tokens, OAuth, JWT, Bearer, password, credential, authorization, cookie, and session-token fields;
- Base64/hex runs of at least 20 characters and high-entropy candidates;
- email and phone shapes, digit runs of at least eight characters;
- absolute POSIX, UNC, home-relative, and drive-letter paths;
- URLs containing credentials or query/fragment data.

Rejected content is not stored or hashed. Only a `scrubbed_candidates` count may be audited.

## Feedback command

```text
/maces-feedback confirmed 美學,建築設計
/maces-feedback corrected 過度留白 紫色漸層
```

The handler receives `raw_args: str`, uses a strict `shlex`-based parser, accepts only `confirmed`/`corrected`, and validates each complete concept at 2–32 characters. Malformed input writes nothing.

## Tool learning

Learning is deny-by-default. It requires an explicit `ok` status, no `error_type`, and an allowlisted tool. Only named safe string fields are considered. The result contributes only aggregate metadata such as length and success state; its body is not stored.

## Reporting a vulnerability

Do not open a public issue for suspected credential retention, profile-boundary violations, path disclosure, or unintended Canon writes. Use GitHub Private Vulnerability Reporting for this repository.

Include the affected MACES version, Hermes version, operating system, reproduction steps, and sanitized evidence. Never attach a real subconscious database, Vault content, Session SQLite file, credential, raw conversation, complete pattern list, session identifier, email address, or absolute private path.

If GitHub Private Vulnerability Reporting is not visible on the repository Security page, do not post sensitive details publicly. Contact the repository owner through a private channel and ask them to enable the private reporting form.

## Supported versions

Security fixes are provided for the latest published MACES release. Until a wider compatibility matrix is published, Hermes Agent 0.18.2 is the verified host version. CI verifies Python 3.11–3.13 on Ubuntu and macOS, while the blocking real-PluginManager E2E remains pinned to Python 3.11 and Hermes Agent 0.18.2.

## Verification

Privacy regression tests scan `subconscious.db`, `subconscious.db-wal`, and `subconscious.db-shm` while a read transaction keeps WAL state available. The real PluginManager E2E also verifies that Hindsight, Obsidian, Session SQLite, and profile memory sentinels remain byte-identical.

Repository release checks also reject tracked MACES databases, local data directories, private-key markers, and non-test absolute user paths. Fictional security fixtures remain in tests because they verify the scrubber boundary.
