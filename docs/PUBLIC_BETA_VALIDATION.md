# Public Beta Shadow Validation

> Status: **NOT YET EXECUTED**. This file is a de-identified evidence template, not a claim that real-world Shadow validation has passed. Until every required field is supported by observed data, the release verdict remains `EXTEND_SHADOW`.

## Environment

- MACES commit: pending release candidate commit
- Hermes version: `0.18.2` required for the verified baseline
- OS and Python: pending
- Shadow start/end: pending; minimum duration seven days
- Interfaces exercised: pending; must include PWA and at least one other real interface

## Minimum evidence

- Completed turns: pending; minimum 30
- Distinct sessions: pending; minimum 5
- Successful allowlisted retrievals: pending; minimum 10
- Gateway restarts: pending; minimum 1
- Disable/restart/re-enable cycles: pending; minimum 1

## Signal review

- Patterns reviewed: pending
- Candidates reviewed: pending
- Reviewable non-zero patterns: pending
- Complete and understandable patterns: pending; target at least 80%
- Scrubbed candidate count: pending
- Negation reinforcement errors: pending; required value 0
- Signal sufficiency: pending; fewer than 10 reviewable patterns requires `EXTEND_SHADOW`

## Safety and isolation

- Plugin errors: pending; required value 0
- Gateway crashes attributable to MACES: pending; required value 0
- Cross-profile violations: pending; required value 0
- Sensitive-content retention findings: pending; required value 0
- Canon/Hindsight/Session/`USER.md`/`MEMORY.md` mutations attributable to MACES: pending; required value 0
- DB/WAL/SHM location verified: pending
- Table caps respected: pending
- `/maces-status` raw-content disclosure findings: pending; required value 0

## Performance and rollback

- Database bytes at start/end: pending aggregate counts only
- Hook latency p50/p95: pending; p95 must be at most 20 ms
- Disable/re-enable result: pending
- Hermes behavior after disable/restart: pending

## Privacy-test protocol

Sensitive-string testing must use a temporary fictional profile only. Never plant credentials or private data in a real profile. Scan the database, WAL, and SHM before removing the temporary profile. Do not record raw test content, real paths, session identifiers, emails, conversations, patterns, Vault content, or database contents in this report.

## Verdict

**EXTEND_SHADOW** — no real seven-day evidence has been recorded yet.

Allowed final values are `PASS`, `EXTEND_SHADOW`, or `FAIL`. Any privacy, profile-isolation, or Canon-boundary failure requires `FAIL`; standards must not be lowered to obtain a release.
