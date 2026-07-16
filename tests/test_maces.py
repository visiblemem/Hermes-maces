from pathlib import Path

from maces import CapabilityBus, CognitiveEvent, CognitiveStore, MacesEngine


def test_install_and_observe_creates_machine_state(tmp_path: Path) -> None:
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


def test_influence_is_advisory_and_bounded(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    engine = MacesEngine(store)
    for index in range(3):
        engine.observe(CognitiveEvent(
            kind="task.completed",
            source="test",
            subject="design",
            event_id=f"event-{index}",
            payload={"patterns": ["constructible"], "knowledge_gaps": ["fire safety"]},
        ))
    signal = engine.influence("design")
    assert signal.subject == "design"
    assert "constructible" in signal.attention
    assert "fire safety" in signal.verify
    assert signal.suggestions


def test_research_without_provider_stops_at_intent(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    bus = CapabilityBus()
    engine = MacesEngine(store, capabilities=bus)
    assert bus.capabilities()["research"] == []
    assert engine.capabilities.select_research(["official"]) is None


def test_manual_research_writes_only_to_staging(tmp_path: Path) -> None:
    store = CognitiveStore(tmp_path / "maces.db")
    engine = MacesEngine(store)
    engine.observe(CognitiveEvent(
        kind="task.completed",
        source="test",
        payload={"knowledge_gaps": ["lighting optics"]},
    ))
    proposal = store.list_table("learning_proposals")[0]
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
