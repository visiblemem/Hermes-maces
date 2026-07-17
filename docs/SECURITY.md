# Security boundaries

MACES treats all hook payloads, tool arguments, feedback text, gap topics, staged artifacts, promotion targets, and journal payloads as untrusted. Text-bearing persistence passes through `maces.secure_store.CognitiveStore`, which applies the central recursive scrubber before SQLite writes.

Profile identity is not accepted from hook kwargs, model calls, tool parameters, or feedback payloads. It is bound once from trusted `ctx.profile_name` during plugin registration.

The `maces-feedback` surface is registered only as an explicit Hermes command when the runtime supports commands. It is never registered as an LLM tool.

The journal is an audit aid, not a complete replay log.
