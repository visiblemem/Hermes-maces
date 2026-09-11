from __future__ import annotations

import sqlite3
from hashlib import sha256

import pytest

from maces.engine import MacesEngine
from maces.models import CognitiveEvent
from maces.policy import MacesPolicy
from maces.secure_store import CognitiveStore


def key(label):
    return sha256(label.encode()).hexdigest()[:24]


def observe(engine, kind, labels, **payload):
    return engine.observe(CognitiveEvent(
        kind=kind, source="test", payload={
            "concepts": labels, "operator_driven": True, **payload,
        },
    ))


@pytest.mark.parametrize("threshold", [0.0, 0.1])
def test_retrieval_is_evidence_not_preference(tmp_path, threshold):
    engine = MacesEngine(CognitiveStore(tmp_path / "state.db"),
                         MacesPolicy(minimum_influence_weight=threshold))
    for _ in range(5):
        observe(engine, "retrieval.used", ["purple", "gradient"])
    assert len(engine.store.list_table("events")) == 5
    assert all(row["evidence_count"] == 5 for row in engine.store.list_table("patterns"))
    assert all(row["weight"] == 0 for row in engine.store.list_table("patterns"))
    assert all(row["weight"] == 0 for row in engine.store.list_table("edges"))
    assert engine.influence(["purple", "gradient"]).render() == ""


@pytest.mark.parametrize("threshold", [0.0, 0.1])
def test_correction_withdraws_node_and_incident_association_after_restart(tmp_path, threshold):
    path = tmp_path / "state.db"
    policy = MacesPolicy(minimum_influence_weight=threshold)
    engine = MacesEngine(CognitiveStore(path), policy)
    for _ in range(3):
        observe(engine, "answer.confirmed", ["purple", "gradient"])
    assert engine.influence(["purple"]).render()
    observe(engine, "answer.corrected", ["purple"])
    engine = MacesEngine(CognitiveStore(path), policy)
    assert engine.influence(["purple"]).render() == ""
    assert "purple" not in engine.influence(["gradient"]).render()
    assert engine.store.pattern(key("purple"))["weight"] == 0
    assert engine.store.edge(key("purple"), key("gradient"))["weight"] == 0
    for _ in range(5):
        observe(engine, "retrieval.used", ["purple", "gradient"])
        observe(engine, "task.completed", ["purple", "gradient"])
    assert engine.influence(["purple"]).render() == ""
    observe(engine, "answer.confirmed", ["purple"])
    assert engine.store.pattern(key("purple"))["weight"] == pytest.approx(0.1)
    assert engine.influence(["purple"]).attention
    assert not engine.influence(["purple"]).associations


def test_retrieval_does_not_strengthen_confirmed_patterns_or_edges(tmp_path):
    engine = MacesEngine(CognitiveStore(tmp_path / "state.db"))
    observe(engine, "answer.confirmed", ["purple", "gradient"])
    for _ in range(5):
        observe(engine, "retrieval.used", ["purple", "gradient"])
    assert engine.store.pattern(key("purple"))["weight"] == pytest.approx(0.1)
    assert engine.store.edge(key("purple"), key("gradient"))["weight"] == pytest.approx(0.1)


@pytest.mark.parametrize("operator", [False, None])
def test_confirmation_requires_explicit_operator_provenance(tmp_path, operator):
    engine = MacesEngine(CognitiveStore(tmp_path / "state.db"))
    observe(engine, "answer.confirmed", ["purple"], operator_driven=operator)
    assert engine.influence(["purple"]).render() == ""


def test_legacy_weights_are_preserved_but_not_trusted(tmp_path):
    path = tmp_path / "legacy.db"
    with sqlite3.connect(path) as db:
        db.executescript("""
            CREATE TABLE patterns(pattern_key TEXT PRIMARY KEY, label TEXT NOT NULL,
                weight REAL NOT NULL, evidence_count INTEGER NOT NULL,
                last_event_id TEXT NOT NULL, last_seen TEXT NOT NULL);
            CREATE TABLE edges(key_a TEXT NOT NULL, key_b TEXT NOT NULL,
                weight REAL NOT NULL, evidence_count INTEGER NOT NULL,
                last_seen TEXT NOT NULL, PRIMARY KEY(key_a,key_b));
        """)
        for label in ("purple", "gradient"):
            db.execute("INSERT INTO patterns VALUES(?,?,0.9,12,'old','2026-01-01')",
                       (key(label), label))
        a, b = sorted((key("purple"), key("gradient")))
        db.execute("INSERT INTO edges VALUES(?,?,0.8,12,'2026-01-01')", (a, b))
    engine = MacesEngine(CognitiveStore(path))
    assert engine.store.pattern(key("purple"))["weight"] == 0.9
    assert engine.store.pattern(key("purple"))["evidence_count"] == 12
    assert engine.influence(["purple", "gradient"]).render() == ""
    assert engine.store.top_patterns() == []
    for label in ("purple", "gradient"):
        observe(engine, "answer.confirmed", [label])
    assert engine.store.pattern(key("purple"))["weight"] == pytest.approx(0.1)
    assert not engine.influence(["purple", "gradient"]).associations
    engine = MacesEngine(CognitiveStore(path))
    assert engine.influence(["purple"]).attention
    assert len([r for r in engine.store.list_table("journal")
                if r["event_type"] == "migration.feedback_evidence"]) == 1


def test_profile_feedback_does_not_cross_databases(tmp_path):
    one = MacesEngine(CognitiveStore(tmp_path / "one.db"))
    two = MacesEngine(CognitiveStore(tmp_path / "two.db"))
    observe(one, "answer.confirmed", ["purple"])
    observe(two, "answer.confirmed", ["purple"])
    observe(one, "answer.corrected", ["purple"])
    assert one.influence(["purple"]).render() == ""
    assert two.influence(["purple"]).attention
