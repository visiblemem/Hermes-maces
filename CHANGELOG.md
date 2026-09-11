# Changelog

## Unreleased

- Add read-only Traditional Chinese feedback previews and explicit `肯定` / `更正` aliases.
- Distinguish supported persistent preference statements from one-off, ambiguous, quoted, conditional, conflicting, and sensitive feedback without calling a model or saving preview text.
- Skip recognized temporary/ambiguous feedback during passive concept extraction.

- Successful retrieval records occurrence evidence without reinforcing preference or association weights.
- Explicit correction immediately retracts the concept and all incident associations; passive events cannot reactivate them.
- Persist operator-confirmation provenance, including a fail-closed additive migration for legacy weights.
- Reject zero-weight influence even when the configured threshold is zero; `/maces-top` shows only confirmed positive weights.
- Bound pending extraction state when newer hosts skip overlapping observers, and expose aggregate eviction counts.
- Add feedback, migration, restart, and profile-isolation regressions plus active-mode PluginManager coverage.
- Expand CI targets to Windows and pinned Hermes 0.21.1 source without claiming completed Shadow validation.

## 1.2.0

- Resolve state through the trusted active Hermes profile home.
- Add namespaced plugin loading for real multi-profile PluginManager operation.
- Parse explicit feedback from the native raw-string slash-command contract.
- Enforce exact success and allowlist gates for retrieval learning.
- Add two-stage Traditional Chinese candidates, stopwords, and bounded negation suppression.
- Centralize all persistence scrubbing, cap enforcement, orphan-edge cleanup, lock retry, and daily decay.
- Add aggregate status/top commands without model-tool exposure.
- Replace the layout-only check with unit-security and real PluginManager E2E jobs.
- Add Ubuntu/macOS compatibility testing for Python 3.11–3.13.
- Add package build and Twine metadata verification.
- Add a cross-platform public repository boundary contract and `.gitignore` hygiene.
- Publish Shadow-first Public Beta documentation, private vulnerability reporting guidance, a de-identified validation template, and draft release notes.
- Keep the formal `v1.2.0` Tag and GitHub Release blocked until real Shadow validation is PASS and repository protection settings are verified.

## 1.1.0

- Initial runtime hardening pass for profile binding, privacy scrubbing, bounded queries, WAL, and shadow mode.
