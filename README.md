# MACES Hermes runtime distribution

Generated from the development repository; see SOURCE.json for the exact source
commit and SHA-256 of every shipped source file. Runtime code is copied unchanged.
Tests, CI, and build tooling remain in the development source commit, not here.

This is a Public Beta preview, not a stable release. Install one profile first.
Keep shadow_mode: true and learnable_tool_fields: {}. No automatic activation.
Observe for at least seven days and complete separate local validation before
considering advisory influence. Each profile owns its own data/maces database.

Operator commands: /maces-status, /maces-top, /maces-feedback.
Chinese feedback previews do not write preferences. Explicit confirmation is required.
MACES does not replace Hermes memory or Hindsight, and registers no model tools.

Use the native Hermes installer with a fixed commit and its security scan enabled.
Disabling hermes-maces through the native plugin registry removes its hooks on
the next runtime startup; preserve its database when diagnosing an issue.
