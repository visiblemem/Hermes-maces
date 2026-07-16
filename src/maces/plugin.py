from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from .engine import MacesEngine
from .models import CognitiveEvent
from .store import CognitiveStore

log = logging.getLogger("hermes-maces")
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]
_ENGINE: MacesEngine | None = None
_PENDING: dict[str, list[str]] = {}


def _engine() -> MacesEngine:
    global _ENGINE
    if _ENGINE is None:
        data = _PLUGIN_ROOT / "data"
        data.mkdir(parents=True, exist_ok=True)
        _ENGINE = MacesEngine(CognitiveStore(data / "subconscious.db"))
    return _ENGINE


def _concepts(text: str, limit: int = 8) -> list[str]:
    latin = re.findall(r"[A-Za-z0-9][A-Za-z0-9_-]{3,}", text.lower())
    cjk = re.findall(r"[\u3400-\u9fff]{2,8}", text)
    return list(dict.fromkeys(latin + cjk))[:limit]


def pre_llm_call(user_message: str, session_id: str = "", **kwargs: Any):
    del kwargs
    concepts = _concepts(user_message)
    _PENDING[session_id] = concepts
    rendered = _engine().influence(concepts).render()
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
    log.debug("absorbed completed turn (%d chars)", len(assistant_response or ""))


def post_tool_call(tool_name: str, args: dict, result: str, **kwargs: Any):
    del kwargs
    concepts = _concepts(" ".join([tool_name, json.dumps(args, ensure_ascii=False)]))
    _engine().observe(CognitiveEvent(
        kind="retrieval.used",
        source="hermes-tool",
        subject=tool_name,
        payload={"concepts": concepts, "operator_driven": True, "result_size": len(result or "")},
    ))


def on_session_end(**kwargs: Any):
    del kwargs
    _engine().consolidate()


def feedback_tool(params: dict, **kwargs: Any) -> str:
    del kwargs
    verdict = str(params.get("verdict", "")).strip().lower()
    concepts = [str(x).strip().lower() for x in params.get("concepts", []) if str(x).strip()]
    if verdict not in {"confirmed", "corrected"}:
        return json.dumps({"success": False, "error": "verdict must be confirmed or corrected"})
    output = _engine().observe(CognitiveEvent(
        kind=f"answer.{verdict}",
        source="operator-feedback",
        payload={"concepts": concepts, "operator_driven": True},
    ))
    return json.dumps({"success": True, **output})


def register(ctx):
    ctx.register_hook("pre_llm_call", pre_llm_call)
    ctx.register_hook("post_llm_call", post_llm_call)
    ctx.register_hook("post_tool_call", post_tool_call)
    ctx.register_hook("on_session_end", on_session_end)
    ctx.register_tool(
        name="maces_feedback",
        toolset="maces",
        description="Record explicit operator confirmation or correction for subconscious concepts.",
        schema={
            "name": "maces_feedback",
            "description": "Record explicit confirmed/corrected operator feedback for concepts.",
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
