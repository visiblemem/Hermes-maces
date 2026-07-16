from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from .engine import MacesEngine
from .models import CognitiveEvent
from .store import CognitiveStore

log = logging.getLogger("hermes-maces")
_HOME = Path.home() / ".hermes" / "plugins" / "hermes-maces"
_ENGINE: MacesEngine | None = None
_PENDING: dict[str, list[str]] = {}


def _engine() -> MacesEngine:
    global _ENGINE
    if _ENGINE is None:
        data = _HOME / "data"
        data.mkdir(parents=True, exist_ok=True)
        _ENGINE = MacesEngine(CognitiveStore(data / "subconscious.db"))
    return _ENGINE


def _concepts(text: str, limit: int = 8) -> list[str]:
    words = [w.strip(".,:;!?()[]{}\"'").lower() for w in text.split()]
    return list(dict.fromkeys(w for w in words if len(w) >= 4))[:limit]


def pre_llm_call(user_message: str, session_id: str = "", **kwargs: Any):
    del kwargs
    concepts = _concepts(user_message)
    _PENDING[session_id] = concepts
    signal = _engine().influence(concepts)
    rendered = signal.render()
    return {"context": rendered} if rendered else None


def post_llm_call(session_id: str, user_message: str, assistant_response: str, **kwargs: Any):
    del kwargs
    concepts = _PENDING.pop(session_id, None) or _concepts(user_message)
    _engine().observe(CognitiveEvent(
        kind="task.completed",
        source="hermes-runtime",
        subject=" ".join(concepts[:3]) or None,
        payload={"concepts": concepts, "operator_driven": True},
    ))
    # A successful turn is weak evidence only; explicit confirmations/corrections
    # can be submitted through the maces_feedback tool.
    log.debug("absorbed turn (%d chars)", len(assistant_response or ""))


def post_tool_call(tool_name: str, args: dict, result: str, **kwargs: Any):
    del kwargs
    concepts = _concepts(" ".join([tool_name, json.dumps(args, ensure_ascii=False)]))
    _engine().observe(CognitiveEvent(
        kind="retrieval.used",
        source="hermes-tool",
        subject=tool_name,
        payload={"concepts": concepts, "operator_driven": True, "result_size": len(result or "")},
    ))


def feedback_tool(params: dict, **kwargs: Any) -> str:
    del kwargs
    verdict = str(params.get("verdict", "")).strip().lower()
    concepts = [str(x).strip().lower() for x in params.get("concepts", []) if str(x).strip()]
    if verdict not in {"confirmed", "corrected"}:
        return json.dumps({"success": False, "error": "verdict must be confirmed or corrected"})
    event = CognitiveEvent(
        kind=f"answer.{verdict}",
        source="operator-feedback",
        payload={"concepts": concepts, "operator_driven": True},
    )
    output = _engine().observe(event)
    return json.dumps({"success": True, **output})


def register(ctx):
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
    ctx.register_hook("post_tool_call", post_tool_call)
    ctx.register_tool(
        name="maces_feedback",
        toolset="maces",
        description="Submit explicit operator confirmation or correction to Hermes subconscious learning.",
        schema={
            "name": "maces_feedback",
            "description": "Record explicit confirmed/corrected feedback for concepts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "verdict": {"type": "string", "enum": ["confirmed", "corrected"]},
                    "concepts": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["verdict", "concepts"],
            },
        },
        handler=feedback_tool,
    )
