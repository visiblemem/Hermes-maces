# Safe rollout

1. Install in one profile only.
2. Keep `rollout.shadow_mode: true` for seven days.
3. Inspect database size, scrub counts, error logs, latency, and the highest-weight concepts.
4. Confirm no sensitive strings or incorrect concepts are present.
5. Set `shadow_mode: false` to enable bounded advisory influence.
6. Repeat the same process separately for each profile.

Removing MACES must not modify Hermes core, Hindsight, Obsidian, profile memory, or session history.
