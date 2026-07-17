from __future__ import annotations

import sqlite3
from hashlib import sha256

import pytest

from maces.engine import MacesEngine
from maces.models import CognitiveEvent
from maces.plugin import _extract_concepts
from maces.policy import MacesPolicy
from maces.secure_store import CognitiveStore
from maces.validation import sanitize_profile_id


def key(label: str) -> str:
    return sha256(label.encode()).hexdigest()[:24]


def event(kind: str, concepts: list[str]) -> CognitiveEvent:
    return CognitiveEvent(
        kind=kind,
        source="test",
        payload={"concepts": concepts, "operator_driven": True},
    )


def test_scrubber_removes_sensitive_material_before_pattern_ingestion(tmp_path):
    text = (
        "api_key=sk-super-secret-value /Users/x/secret.txt a@b.com "
        "anodized aluminum"
    )
    concepts, scrubbed = _extract_concepts(text)
    assert concepts == ["anodized", "aluminum"]
    assert scrubbed >= 3

    db_path = tmp_path / "subconscious.db"
    store = CognitiveStore(db_path)
    engine = MacesEngine(store)
    engine.observe(event("retrieval.used", concepts))
    store.journal("candidates.scrubbed", None, {"scrubbed_candidates": scrubbed})

    raw = db_path.read_bytes()
    assert b"sk-super-secret-value" not in raw
    assert b"/Users/x/secret.txt" not in raw
    assert b"a@b.com" not in raw
    journals = store.list_table("journal")
    assert any("scrubbed_candidates" in row["payload_json"] for row in journals)


def test_store_rejects_invalid_pattern_labels(tmp_path):
    store = CognitiveStore(tmp_path / "subconscious.db")
    with pytest.raises(ValueError):
        store.put_pattern(key("bad label"), "bad label", 0.5, "event", "2026-01-01T00:00:00+00:00")


def test_influence_filters_hostile_legacy_labels(tmp_path):
    store = CognitiveStore(tmp_path / "subconscious.db")
    with sqlite3.connect(store.path) as db:
        db.execute(
            "INSERT INTO patterns VALUES(?,?,?,?,?,?)",
            (key("safe"), "safe", 0.8, 1, "event", "2026-01-01T00:00:00+00:00"),
        )
        db.execute(
            "INSERT INTO patterns VALUES(?,?,?,?,?,?)",
            (key("hostile"), "token=leak", 1.0, 1, "event", "2026-01-01T00:00:00+00:00"),
        )
    rendered = MacesEngine(store).influence([]).render()
    assert "safe" in rendered
    assert "token=leak" not in rendered


def test_mentions_do_not_raise_weight_or_attention(tmp_path):
    store = CognitiveStore(tmp_path / "subconscious.db")
    engine = MacesEngine(store)
    for _ in range(50):
        engine.observe(event("task.completed", ["topicx"]))
    row = store.pattern(key("topicx"))
    assert row is not None
    assert row["evidence_count"] == 50
    assert row["weight"] == 0
    assert "topicx" not in engine.influence(["topicx"]).render()


def test_valenced_history_outranks_mentions(tmp_path):
    store = CognitiveStore(tmp_path / "subconscious.db")
    engine = MacesEngine(store)
    for _ in range(50):
        engine.observe(event("task.completed", ["topicx"]))
    engine.observe(event("retrieval.used", ["topicz"]))
    engine.observe(event("retrieval.used", ["topicz"]))
    engine.observe(event("answer.confirmed", ["topicz"]))
    assert store.pattern(key("topicz"))["weight"] > store.pattern(key("topicx"))["weight"]


def test_profile_ids_cannot_escape_data_directory():
    with pytest.raises(ValueError):
        sanitize_profile_id("../../etc")
    with pytest.raises(ValueError):
        sanitize_profile_id("team／..／etc")
    assert sanitize_profile_id("design-team") == "design-team"


def test_retrieval_alpha_matches_batch_policy():
    policy = MacesPolicy()
    assert policy.reinforce_retrieval(0.0) == pytest.approx(0.03)
