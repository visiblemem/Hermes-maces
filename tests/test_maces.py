from pathlib import Path

import pytest

from maces import ActivationLevel, CognitiveEvent, CognitiveStore, MacesEngine, MacesPolicy


def test_observation_creates_machine_state(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    engine = MacesEngine(store)
    result = engine.observe(CognitiveEvent(
        kind="task.completed",
        source="test",
        subject="design",
        payload={
            "patterns": ["modular", "constructible"],
            "knowledge_gaps": [{"topic": "acrylic suspension", "priority": 0.8}],
        },
    ))
    assert result == {"patterns": 3, "gaps": 1, "proposals": 1}
    assert len(store.list_table("patterns")) == 3
    assert len(store.list_table("learning_proposals")) == 1


def test_duplicate_event_is_idempotent(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    engine = MacesEngine(store)
    event = CognitiveEvent(kind="task.completed", source="test", payload={"patterns": ["x"]})
    engine.observe(event)
    assert engine.observe(event) == {"patterns": 0, "gaps": 0, "proposals": 0}


def test_shadow_mode_cannot_research(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    engine = MacesEngine(store)
    with pytest.raises(PermissionError):
        engine.stage_research(
            "missing", title="x", content="x", sources=[], query_count=0, confidence=0.5
        )


def test_research_writes_only_to_staging(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    policy = MacesPolicy(activation=ActivationLevel.RESEARCH)
    engine = MacesEngine(store, policy)
    engine.observe(CognitiveEvent(
        kind="task.completed",
        source="test",
        payload={"knowledge_gaps": ["lighting optics"]},
    ))
    proposal = store.list_table("learning_proposals")[0]
    store.set_learning_status(proposal["proposal_id"], "approved")
    artifact = engine.stage_research(
        proposal["proposal_id"],
        title="Lighting optics",
        content="Evidence-backed staged research.",
        sources=[{"url": "https://example.test", "title": "Primary source"}],
        query_count=1,
        confidence=0.8,
    )
    assert artifact.proposal_id == proposal["proposal_id"]
    assert len(store.list_table("staged_artifacts")) == 1
    assert store.list_table("promotion_proposals") == []
