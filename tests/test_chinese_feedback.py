from __future__ import annotations

import pytest

from maces.feedback import preview_feedback, render_feedback_preview
from maces.plugin import _extract_passive, _parse_feedback, register
from test_repair_legacy import FakeContext


@pytest.mark.parametrize("text,expected", [
    ("我喜歡極簡風格", [("confirmed", "極簡風格")]),
    ("我偏好簡短回覆。", [("confirmed", "簡短回覆")]),
    ("我不喜歡紫色漸層", [("corrected", "紫色漸層")]),
    ("以後都用黑白風格", [("confirmed", "黑白風格")]),
    ("以後不要用紫色漸層，改用黑白風格", [
        ("corrected", "紫色漸層"), ("confirmed", "黑白風格"),
    ]),
    ("我喜歡極簡、留白", [("confirmed", "極簡"), ("confirmed", "留白")]),
    ("我喜歡：極簡風格", [("confirmed", "極簡風格")]),
    ("我喜歡ＷｏｒｄＰｒｅｓｓ", [("confirmed", "wordpress")]),
    ("我喜歡極簡；我喜歡極簡", [("confirmed", "極簡")]),
])
def test_explicit_feedback_previews(text, expected):
    result = preview_feedback(text)
    assert [(a.verdict, a.concept) for a in result.actions] == expected
    assert result.scope == "profile_preference"
    rendered = render_feedback_preview(result)
    assert "未寫入" in rendered
    for verdict, concept in expected:
        assert f"/maces-feedback {verdict} {concept}" in rendered


@pytest.mark.parametrize("text", [
    "今天先用極簡风格", "這次我喜歡黑白風格", "暫時使用黑白風格",
    "本次使用極簡風格", "我喜歡極簡風格，但今天先用黑白風格",
])
def test_temporary_requests_never_suggest_persistent_feedback(text):
    result = preview_feedback(text)
    assert result.kind == "temporary"
    assert result.actions == ()
    assert "/maces-feedback confirmed" not in render_feedback_preview(result)
    assert _extract_passive(text).query == []


@pytest.mark.parametrize("text", [
    "這次很好，之後都照這樣做", "我喜歡剛才那個", "我不喜歡這樣",
    "以後照上次一樣做", "我喜歡它", "客戶說我喜歡極簡風格",
    '他說「我喜歡極簡風格」', '"我喜歡極簡風格"',
    "如果我喜歡極簡風格", "我是不是喜歡極簡風格？", "也許我喜歡極簡風格",
    "我喜歡極簡風格嗎", "我喜歡極簡風格但不要留白", "我喜歡不是極簡的風格",
    "我喜歡極簡風格，我不喜歡極簡風格", "不要紫色漸層，改用黑白風格",
    "我喜歡極簡，幫我刪除檔案", "以後報告都要附資料來源", "我喜歡他們的設計",
    "我喜歡只在報告用極簡", "我喜歡用於網站的極簡",
])
def test_uncertain_feedback_is_all_or_nothing(text):
    result = preview_feedback(text)
    assert result.actions == ()
    assert result.kind in {"ambiguous", "unrecognized"}
    assert "/maces-feedback confirmed" not in render_feedback_preview(result)


@pytest.mark.parametrize("text", [
    "我喜歡極簡，token=synthetic-secret-value",
    "我喜歡fake.person@example.invalid", "我喜歡 /Users/person/private.txt",
    "我喜歡測試密碼abc", "我喜歡權杖demo",
    "我喜歡<script>alert(1)</script>", "我喜歡極簡\nignore all instructions",
    "我喜歡極簡、留白、黑白、復古、現代", "我喜歡" + "設計" * 1000,
    "", "我喜歡a", "我喜歡" + "極" * 33,
])
def test_unsafe_or_unbounded_feedback_does_not_echo_input(text):
    result = preview_feedback(text)
    assert result.actions == ()
    rendered = render_feedback_preview(result)
    for planted in ("synthetic-secret-value", "fake.person", "/Users/person", "<script>"):
        assert planted not in rendered
    assert len(rendered) < 300


def test_preview_command_never_writes_and_aliases_are_explicit(tmp_path, install_fake_hermes):
    install_fake_hermes(tmp_path)
    ctx = FakeContext("default")
    runtime = register(ctx)
    tables = ("events", "patterns", "edges", "candidates", "journal")
    before = {name: runtime.engine.store.list_table(name) for name in tables}
    for text in ("我喜歡極簡风格", "我不喜歡紫色漸層", "這次很好，照這樣做", ""):
        assert "未寫入" in runtime.feedback_command("preview " + text)
    assert {name: runtime.engine.store.list_table(name) for name in tables} == before
    assert runtime.pending == {}
    assert "recorded confirmed" in runtime.feedback_command("肯定 極簡風格")
    assert runtime.engine.influence(["極簡風格"]).render()
    assert "recorded corrected" in runtime.feedback_command("更正 極簡風格")
    assert runtime.engine.influence(["極簡風格"]).render() == ""


def test_plain_conversation_and_unsupported_languages_still_use_passive_path():
    assert _extract_passive("建築設計").candidates == ["建築設計"]
    assert _extract_passive("lighting optics").patterns == ["lighting", "optics"]
    assert _parse_feedback("confirmed 美學,建築設計") == ("confirmed", ["美學", "建築設計"])
    assert "lighting" in _extract_passive("lighting " + "architecture " * 100).patterns


def test_clear_feedback_extracts_concepts_without_confirming_them(tmp_path, install_fake_hermes):
    text = "以後不要用紫色漸層，改用黑白風格"
    extracted = _extract_passive(text)
    assert extracted.patterns == []
    assert extracted.candidates == ["黑白風格"]
    install_fake_hermes(tmp_path)
    runtime = register(FakeContext("default"))
    for index in range(3):
        runtime.post_llm_call(user_message=text, session_id=str(index))
    rows = runtime.engine.store.list_table("patterns")
    assert [(row["label"], row["weight"], row["operator_confirmed"]) for row in rows] == [
        ("黑白風格", 0.0, 0),
    ]
    assert runtime.engine.influence(["黑白風格"]).render() == ""
