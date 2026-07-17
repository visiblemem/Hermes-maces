from __future__ import annotations

from dataclasses import replace

from .models import CognitiveEvent, PromotionProposal, StagedArtifact
from .store import CognitiveStore as BaseCognitiveStore
from .validation import is_valid_pattern_label, scrub_text, scrub_value


class CognitiveStore(BaseCognitiveStore):
    """Store boundary that sanitizes every persisted text-bearing payload."""

    def journal(self, event_type: str, entity_id: str | None, payload: dict) -> None:
        safe_type, _ = scrub_text(event_type)
        safe_entity, _ = scrub_text(entity_id or "")
        safe_payload, _ = scrub_value(payload)
        super().journal(safe_type[:64], safe_entity[:128] or None, safe_payload)

    def save_event(self, event: CognitiveEvent) -> bool:
        safe_source, _ = scrub_text(event.source)
        safe_subject, _ = scrub_text(event.subject or "")
        safe_payload, scrubbed = scrub_value(event.payload)
        safe = replace(
            event,
            source=safe_source[:128],
            subject=safe_subject[:256] or None,
            payload=safe_payload,
        )
        created = super().save_event(safe)
        if created and scrubbed:
            super().journal(
                "candidates.scrubbed", safe.event_id, {"scrubbed_candidates": scrubbed}
            )
        return created

    def put_pattern(self, key: str, label: str, weight: float, event_id: str, seen: str) -> None:
        if not is_valid_pattern_label(label):
            raise ValueError("pattern label must be <=32 lowercase letters/CJK/digits/hyphen")
        if len(key) != 24 or any(ch not in "0123456789abcdef" for ch in key):
            raise ValueError("pattern key must be a 24-character lowercase hex digest")
        super().put_pattern(key, label, weight, event_id, seen)

    def upsert_gap(self, key: str, topic: str, kind: str, reason: str, priority: float) -> None:
        safe_topic, _ = scrub_text(topic)
        safe_kind, _ = scrub_text(kind)
        safe_reason, _ = scrub_text(reason)
        if safe_topic:
            super().upsert_gap(key, safe_topic[:256], safe_kind[:64], safe_reason[:512], priority)

    def stage(self, artifact: StagedArtifact) -> None:
        title, title_count = scrub_text(artifact.title)
        content, content_count = scrub_text(artifact.content)
        sources, source_count = scrub_value(artifact.sources)
        safe = replace(artifact, title=title[:256], content=content, sources=sources)
        super().stage(safe)
        count = title_count + content_count + source_count
        if count:
            super().journal(
                "candidates.scrubbed", artifact.artifact_id, {"scrubbed_candidates": count}
            )

    def create_promotion(self, proposal: PromotionProposal) -> None:
        target, scrubbed = scrub_text(proposal.target_path)
        if not target or scrubbed:
            raise ValueError("promotion target must be a non-sensitive relative path")
        super().create_promotion(replace(proposal, target_path=target[:512]))
