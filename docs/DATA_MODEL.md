# Advisory Data Model

- **patterns**: validated concept labels with advisory weights, occurrence evidence, and `operator_confirmed` provenance;
- **edges**: associations between pattern digests with separate `operator_confirmed` provenance;
- **candidates**: passive Traditional Chinese concepts excluded from influence until cross-session promotion;
- **gaps**: bounded unresolved knowledge needs;
- **learning proposals**: one active proposal per stable gap identity;
- **staged artifacts**: scrubbed dark-state research, never read by influence;
- **promotion proposals**: proposal-only surfacing records, never direct Canon writes;
- **journal/metadata**: selected audit and maintenance state.

Every table is per-profile disposable MACES state, not Canon.

Existing databases receive an additive boolean column on patterns and edges, defaulting to unconfirmed. Migration preserves existing rows and weights but those weights are not eligible for influence. Fresh explicit confirmation is required and starts from zero. An explicit correction zeros the node and all incident edge weights and clears their confirmation flags. Candidate promotion and successful retrieval never confer confirmation. Missing operator provenance cannot confer confirmation either.
