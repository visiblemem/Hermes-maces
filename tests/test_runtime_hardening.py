from __future__ import annotations

import sqlite3
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field

import pytest

from maces.plugin import register


@dataclass
class FakeContext:
    profile_name: str
    plugin_data_dir: str
    hooks: dict[str, object] = field(default_factory=dict)
    commands: dict[str, object] = field(default_factory=dict)

    def register_hook(self, name, handler):
        self.hooks[name] = handler

    def register_command(self, name, handler):
        self.commands[name] = handler


def test_register_requires_trusted_profile_name(tmp_path):
    ctx = FakeContext("", str(tmp_path))
    with pytest.raises(RuntimeError):
        register(ctx)


def test_profile_identity_is_fixed_at_registration(tmp_path):
    a = FakeContext("design-team", str(tmp_path))
    b = FakeContext("invest-team", str(tmp_path))
    runtime_a = register(a)
    runtime_b = register(b)
    assert runtime_a.profile_name == "design-team"
    assert runtime_b.profile_name == "invest-team"
    assert runtime_a.engine.store.path != runtime_b.engine.store.path

    # Hook kwargs cannot forge the profile selected by the trusted context.
    a.hooks["pre_llm_call"]("anodized aluminum", session_id="s", profile_id="invest-team")
    a.hooks["post_llm_call"](
        session_id="s",
        user_message="anodized aluminum",
        assistant_response="ok",
        profile_id="invest-team",
    )
    assert "design-team" in runtime_a.engine.store.path


def test_feedback_is_not_registered_as_model_tool(tmp_path):
    ctx = FakeContext("design-team", str(tmp_path))
    register(ctx)
    assert "maces-feedback" in ctx.commands
    assert not hasattr(ctx, "tools")


def test_daily_decay_runs_only_once(tmp_path):
    ctx = FakeContext("design-team", str(tmp_path))
    runtime = register(ctx)
    first = runtime.engine.consolidate()
    second = runtime.engine.consolidate()
    assert first == {"changed": 0, "pruned": 0}
    assert second == {"changed": 0, "pruned": 0}
    rows = runtime.engine.store.list_table("journal")
    assert sum(row["event_type"] == "consolidation.decay" for row in rows) == 1


def test_pending_is_cleared_after_completed_turn(tmp_path):
    ctx = FakeContext("design-team", str(tmp_path))
    runtime = register(ctx)
    pre = ctx.hooks["pre_llm_call"]
    post = ctx.hooks["post_llm_call"]
    pre("anodized aluminum", session_id="s", turn_id="1")
    assert runtime.pending
    post(
        session_id="s",
        user_message="anodized aluminum",
        assistant_response="ok",
        turn_id="1",
    )
    assert runtime.pending == {}


def test_parallel_hooks_do_not_collide(tmp_path):
    ctx = FakeContext("design-team", str(tmp_path))
    runtime = register(ctx)

    def run_turn(index: int):
        kwargs = {"session_id": f"s-{index % 5}", "turn_id": str(index)}
        ctx.hooks["pre_llm_call"]("anodized aluminum", **kwargs)
        ctx.hooks["post_llm_call"](
            user_message="anodized aluminum", assistant_response="ok", **kwargs
        )

    with ThreadPoolExecutor(max_workers=10) as pool:
        list(pool.map(run_turn, range(50)))
    assert runtime.pending == {}
    with sqlite3.connect(runtime.engine.store.path) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_sensitive_feedback_never_reaches_raw_sqlite(tmp_path):
    ctx = FakeContext("design-team", str(tmp_path))
    runtime = register(ctx)
    ctx.commands["maces-feedback"](
        {
            "verdict": "confirmed",
            "concepts": [
                "api_key=sk-secret-value",
                "/Users/person/private.txt",
                "person@example.com",
                "anodized",
            ],
        }
    )
    raw = open(runtime.engine.store.path, "rb").read()
    assert b"sk-secret-value" not in raw
    assert b"/Users/person/private.txt" not in raw
    assert b"person@example.com" not in raw
