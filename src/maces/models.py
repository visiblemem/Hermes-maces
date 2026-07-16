from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from hashlib import sha256
from json import dumps
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


class ActivationLevel(StrEnum):
    OFF = "off"
    SHADOW = "shadow"
    ADVISORY = "advisory"
    RESEARCH = "research"
    PROMOTION = "promotion"


class ProposalStatus(StrEnum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    RUNNING = "running"
    STAGED = "staged"
    REJECTED = "rejected"
    PROMOTED = "promoted"


@dataclass(slots=True)
class CognitiveEvent:
    kind: str
    source: str
    payload: dict[str, Any]
    subject: str | None = None
    confidence: float = 1.0
    authority: str = "evidence"
    occurred_at: str = field(default_factory=utc_now)
    event_id: str = field(default_factory=lambda: str(uuid4()))

    def validate(self) -> None:
        if not self.kind.strip() or not self.source.strip():
            raise ValueError("kind and source are required")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(slots=True)
class LearningProposal:
    topic: str
    reason: str
    priority: float
    required_sources: list[str]
    gap_key: str
    status: ProposalStatus = ProposalStatus.PROPOSED
    proposal_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    @property
    def digest(self) -> str:
        body = dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(body.encode()).hexdigest()


@dataclass(slots=True)
class StagedArtifact:
    proposal_id: str
    title: str
    content: str
    sources: list[dict[str, str]]
    confidence: float
    artifact_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class PromotionProposal:
    artifact_id: str
    target_provider: str
    target_path: str
    operation: str = "create"
    proposal_id: str = field(default_factory=lambda: str(uuid4()))
    created_at: str = field(default_factory=utc_now)

    @property
    def digest(self) -> str:
        body = dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return sha256(body.encode()).hexdigest()
