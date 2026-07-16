from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .models import CognitiveEvent


class EventAdapter(Protocol):
    def normalize(self, raw: dict[str, Any]) -> CognitiveEvent: ...


@dataclass(slots=True)
class HermesRuntimeAdapter:
    source_name: str = "hermes-runtime"

    def normalize(self, raw: dict[str, Any]) -> CognitiveEvent:
        kind = str(raw.get("event_type", raw.get("kind", "runtime.event")))
        payload = {
            "patterns": raw.get("patterns", []),
            "knowledge_gaps": raw.get("knowledge_gaps", []),
            "task_id": raw.get("task_id"),
            "route": raw.get("route"),
            "outcome": raw.get("outcome"),
            "metadata": raw.get("metadata", {}),
        }
        return CognitiveEvent(
            kind=kind,
            source=self.source_name,
            subject=raw.get("subject"),
            confidence=float(raw.get("confidence", 1.0)),
            authority=str(raw.get("authority", "evidence")),
            payload=payload,
            event_id=str(raw.get("event_id")) if raw.get("event_id") else CognitiveEvent(kind=kind, source=self.source_name, payload={}).event_id,
        )


@dataclass(slots=True)
class GenericMemoryAdapter:
    provider: str

    def normalize(self, raw: dict[str, Any]) -> CognitiveEvent:
        return CognitiveEvent(
            kind="memory.observed",
            source=f"memory:{self.provider}",
            subject=raw.get("subject"),
            confidence=float(raw.get("confidence", 0.7)),
            authority=str(raw.get("authority", "memory")),
            payload={
                "patterns": raw.get("patterns", []),
                "knowledge_gaps": raw.get("knowledge_gaps", []),
                "provider_ref": raw.get("id"),
            },
        )
