from __future__ import annotations

import json
import logging
import os
import re
import shutil
import threading
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from .engine import MacesEngine
from .models import CognitiveEvent
from .policy import MacesPolicy
from .secure_store import CognitiveStore
from .validation import is_valid_pattern_label, reject_sensitive_candidate, sanitize_profile_id, scrub_text

log = logging.getLogger("hermes-maces")
_PLUGIN_ROOT = Path(__file__).resolve().parents[2]


def _extract_concepts(text: str, limit: int = 8) -> tuple[list[str], int]:
    scrubbed_text, scrubbed = scrub_text(text)
    latin = re.findall(r"[A-Za-z0-9][A-Za-z0-9-]{3,31}", scrubbed_text.lower())
    concepts: list[str] = []
    for candidate in latin:
        if reject_sensitive_candidate(candidate) or not is_valid_pattern_label(candidate):
            scrubbed += 1
            continue
        if candidate not in concepts:
            concepts.append(candidate)
        if len(concepts) >= limit:
            break
    return concepts, scrubbed


def _concepts(text: str, limit: int = 8) -> list[str]:
    return _extract_concepts(text, limit)[0]


def _trusted_profile_name(ctx: Any) -> str:
    raw = getattr(ctx, "profile_name", None)
    if raw in (None, ""):
        raise RuntimeError("Hermes MACES requires ctx.profile_name; no shared default profile is allowed")
    return sanitize_profile_id(raw)


def _profile_data_dir(ctx: Any, profile_name: str) -> Path:
    explicit = getattr(ctx, "plugin_data_dir", None)
    if explicit:
        root = Path(explicit).expanduser().resolve()
    else:
        hermes_home = getattr(ctx, "hermes_home", None) or os.environ.get("HERMES_HOME")
        if hermes_home:
            root = (Path(hermes_home).expanduser().resolve() / "plugins" / "hermes-maces")
        else:
            root = (_PLUGIN_ROOT / "data").resolve()
    profile_dir = (root / profile_name).resolve()
    if root != profile_dir and root not in profile_dir.parents:
        raise ValueError("profile database path escaped the MACES data directory")
    profile_dir.mkdir(parents=True, exist_ok=True)
    return profile_dir


def _migrate_legacy_database(profile_dir: Path, profile_name: str) -> None:
    legacy = (_PLUGIN_ROOT / "data" / "subconscious.db").resolve()
    destination = profile_dir / "subconscious.db"
    if not legacy.exists() or destination.exists():
        return
    shutil.move(str(legacy), str(destination))
    store = CognitiveStore(destination)
    store.journal("store.migrated", profile_name, {"from": "legacy-single-store"})


@dataclass(slots=True)
class ProfileRuntime:
    profile_name: str
    engine: MacesEngine
    policy: MacesPolicy
    pending: dict[tuple[str, str, str], list[str]] = field(default_factory=dict)
    lock: threading.RLock = field(default_factory=threading.RLock)

    def _turn_key(self, session_id: str, kwargs: dict[str, Any]) -> tuple[str, str, str]:
        turn_id = str(kwargs.get("turn_id") or kwargs.get("request_id") or session_id or "turn")
        return self.profile_name, str(session_id or "session"), turn_id

    def _journal_scrubbed(self, count: int) -> None:
        if count:
            self.engine.store.journal(
                "candidates.scrubbed", None, {"scrubbed_candidates": int(count)}
            )

    def pre_llm_call(self, user_message: str, session_id: str = "", **kwargs: Any):
        key = self._turn_key(session_id, kwargs)
        concepts, scrubbed = _extract_concepts(user_message)
        with self.lock:
            self.pending[key] = concepts
        self._journal_scrubbed(scrubbed)
        try:
            rendered = self.engine.influence(concepts).render()
            return {"context": rendered} if rendered else None
        except Exception:
            log.exception("MACES influence failed; continuing without advisory context")
            return None

    def post_llm_call(
        self, session_id: str, user_message: str, assistant_response: str, **kwargs: Any
    ):
        key = self._turn_key(session_id, kwargs)
        try:
            with self.lock:
                concepts = self.pending.pop(key, None)
            if concepts is None:
                concepts, scrubbed = _extract_concepts(user_message)
                self._journal_scrubbed(scrubbed)
            self.engine.observe(
                CognitiveEvent(
                    kind="task.completed",
                    source="hermes-runtime",
                    subject=" ".join(concepts[:3]) or None,
                    payload={"concepts": concepts, "operator_driven": True},
                )
            )
        except Exception:
            log.exception("MACES turn absorption failed; Hermes response is unaffected")
        finally:
            with self.lock:
                self.pending.pop(key, None)
        log.debug("absorbed completed turn (%d chars)", len(assistant_response or ""))

    def post_tool_call(self, tool_name: str, args: dict, result: str, **kwargs: Any):
        try:
            fields = self.policy.learnable_fields_for(tool_name)
            if not fields or kwargs.get("success") is False:
                return
            values = [args.get(field) for field in fields]
            text = " ".join(value for value in values if isinstance(value, str))
            concepts, scrubbed = _extract_concepts(text)
            self._journal_scrubbed(scrubbed)
            if not concepts:
                return
            self.engine.observe(
                CognitiveEvent(
                    kind="retrieval.used",
                    source="hermes-tool",
                    subject=tool_name,
                    payload={
                        "concepts": concepts,
                        "operator_driven": True,
                        "result_size": len(result or ""),
                    },
                )
            )
        except Exception:
            log.exception("MACES tool absorption failed; tool result is unaffected")

    def on_session_end(self, session_id: str = "", **kwargs: Any):
        try:
            with self.lock:
                prefix = (self.profile_name, str(session_id or "session"))
                stale = [key for key in self.pending if key[:2] == prefix]
                for key in stale:
                    self.pending.pop(key, None)
            self.engine.consolidate()
        except Exception:
            log.exception("MACES session cleanup failed; Hermes lifecycle is unaffected")

    def explicit_feedback(self, params: dict, **kwargs: Any) -> str:
        """Trusted command/PWA entrypoint. Never registered as an LLM tool."""
        verdict = str(params.get("verdict", "")).strip().lower()
        if verdict not in {"confirmed", "corrected"}:
            return json.dumps({"success": False, "error": "invalid verdict"})
        concepts: list[str] = []
        scrubbed = 0
        for raw in params.get("concepts", []):
            extracted, count = _extract_concepts(str(raw), limit=16)
            concepts.extend(extracted)
            scrubbed += count
        concepts = list(dict.fromkeys(concepts))[:16]
        self._journal_scrubbed(scrubbed)
        output = self.engine.observe(
            CognitiveEvent(
                kind=f"answer.{verdict}",
                source="trusted-operator-feedback",
                payload={"concepts": concepts, "operator_driven": True},
            )
        )
        return json.dumps({"success": True, **output})


def register(ctx):
    profile_name = _trusted_profile_name(ctx)
    profile_dir = _profile_data_dir(ctx, profile_name)
    _migrate_legacy_database(profile_dir, profile_name)
    policy = MacesPolicy()
    runtime = ProfileRuntime(
        profile_name=profile_name,
        engine=MacesEngine(CognitiveStore(profile_dir / "subconscious.db"), policy),
        policy=policy,
    )
    ctx.register_hook("pre_llm_call", runtime.pre_llm_call)
    ctx.register_hook("post_llm_call", runtime.post_llm_call)
    ctx.register_hook("post_tool_call", runtime.post_tool_call)
    ctx.register_hook("on_session_end", runtime.on_session_end)
    if hasattr(ctx, "register_command"):
        ctx.register_command("maces-feedback", runtime.explicit_feedback)
    return runtime
