"""Conservative, read-only Chinese feedback interpretation for operator review."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .validation import (
    is_valid_explicit_concept,
    normalize_text,
    reject_sensitive_candidate,
    scrub_text,
)

MAX_FEEDBACK_CHARS = 1024
MAX_FEEDBACK_CONCEPTS = 4
_FEEDBACK = re.compile(r"喜歡|偏好|不要|別用|改用|改成|採用|使用|(?:都|先)用|很好|照.*(?:做|樣)|更正")
_TEMPORARY = re.compile(r"這次|這一次|這一版|本次|今天|今日|暫時|先用|先使用|先改|僅限|只限")
_UNCERTAIN = re.compile(r"如果|假如|假設|例如|譬如|範例|也許|可能|是否|嗎|呢|[?？]")
_REFERENCE = re.compile(r"這樣|那樣|這個|那個|這種|那種|剛才|上次|一樣|照舊|它|他|她")
_QUOTED = re.compile(r'''[「」『』“”‘’"'`<>]|(?:客戶|有人|對方|別人).*(?:說|表示|喜歡|偏好)''')
_SENSITIVE_HINT = re.compile(r"密碼|金鑰|憑證|驗證碼|權杖|授權碼")
_FUTURE = re.compile(r"^(?:以後|往後|今後|之後|未來)(?:都)?(?:請)?")
_POSITIVE = re.compile(r"^(?:我)?(?:喜歡|偏好)[:：]?\s*(.+)$")
_NEGATIVE = re.compile(r"^(?:我)?(?:不喜歡|不偏好)[:：]?\s*(.+)$")
_USE = re.compile(r"^(?:使用|採用|用|改用|改成)[:：]?\s*(.+)$")
_AVOID = re.compile(r"^(?:不要再用|不要使用|不要用|別用|避免使用|不要)[:：]?\s*(.+)$")


@dataclass(frozen=True, slots=True)
class FeedbackAction:
    verdict: str
    concept: str


@dataclass(frozen=True, slots=True)
class FeedbackPreview:
    kind: str
    scope: str = "unknown"
    actions: tuple[FeedbackAction, ...] = ()
    reason: str = ""


def preview_feedback(text: str) -> FeedbackPreview:
    """Never writes state, resolves conversational references, or calls a model."""
    if not isinstance(text, str) or not text.strip() or len(text) > MAX_FEEDBACK_CHARS:
        return FeedbackPreview("rejected", reason="invalid_length")
    normalized = normalize_text(text)
    if len(normalized) > MAX_FEEDBACK_CHARS:
        return FeedbackPreview("rejected", reason="invalid_length")
    cleaned, scrubbed = scrub_text(normalized)
    if scrubbed or _SENSITIVE_HINT.search(normalized):
        return FeedbackPreview("rejected", reason="sensitive_content")
    if not _FEEDBACK.search(cleaned) and not _FUTURE.match(cleaned):
        return FeedbackPreview("unrecognized", reason="unsupported_sentence")
    if _QUOTED.search(cleaned) or _UNCERTAIN.search(cleaned):
        return FeedbackPreview("ambiguous", reason="quoted_or_uncertain")
    if _REFERENCE.search(cleaned):
        return FeedbackPreview("ambiguous", reason="unresolved_reference")
    if _TEMPORARY.search(cleaned):
        return FeedbackPreview("temporary", scope="one_off", reason="temporary_scope")

    clauses = [part.strip() for part in re.split(r"[，,。；;\n]+", normalized) if part.strip()]
    if len(clauses) > MAX_FEEDBACK_CONCEPTS:
        return FeedbackPreview("rejected", reason="too_many_concepts")
    persistent = bool(_FUTURE.match(clauses[0])) if clauses else False
    actions: list[FeedbackAction] = []
    for clause in clauses:
        body = _FUTURE.sub("", clause).strip()
        match = _NEGATIVE.fullmatch(body)
        verdict = "corrected"
        if match is None:
            match = _POSITIVE.fullmatch(body)
            verdict = "confirmed"
        if match is None and persistent:
            match = _AVOID.fullmatch(body)
            verdict = "corrected"
            if match is None:
                match = _USE.fullmatch(body)
                verdict = "confirmed"
        if match is None:
            return FeedbackPreview("ambiguous", reason="scope_or_sentence_unclear")
        for raw_concept in match.group(1).split("、"):
            concept = normalize_text(raw_concept).lower()
            # Do not turn another clause, qualification, or negation into a noun label.
            if (
                not is_valid_explicit_concept(concept)
                or reject_sensitive_candidate(concept)
                or re.search(r"不|但|而|除非|只有|只在|僅|限於|用於|針對|對於|的話|以及|也要|都要|其實|先", concept)
                or _FEEDBACK.search(concept)
            ):
                return FeedbackPreview("ambiguous", reason="concept_needs_clarification")
            item = FeedbackAction(verdict, concept)
            if any(old.concept == concept and old.verdict != verdict for old in actions):
                return FeedbackPreview("ambiguous", reason="conflicting_feedback")
            if item not in actions:
                actions.append(item)
            if len(actions) > MAX_FEEDBACK_CONCEPTS:
                return FeedbackPreview("rejected", reason="too_many_concepts")
    if not actions:
        return FeedbackPreview("unrecognized", reason="unsupported_sentence")
    kind = "mixed" if len({a.verdict for a in actions}) > 1 else actions[0].verdict
    return FeedbackPreview(kind, "profile_preference", tuple(actions))


def render_feedback_preview(preview: FeedbackPreview) -> str:
    heading = "MACES 中文回饋預覽（未寫入）"
    if preview.kind == "temporary":
        return heading + "\n這是單次或暫時要求，不作為長期偏好。"
    if preview.kind == "rejected":
        return heading + "\n無法安全解析；請提供不含敏感資訊的短句，最多四個明確概念。"
    if not preview.actions:
        return heading + "\n請明確說明喜歡或要撤回的概念，以及是單次要求還是長期偏好；不會猜測前文、引用或條件句。"
    lines = [heading, "範圍：目前 Profile 的偏好；下列為待你確認的解讀。"]
    for action in preview.actions:
        label = "肯定" if action.verdict == "confirmed" else "撤回舊推薦"
        lines.append(f"- {label}：{action.concept}")
        lines.append(f"  /maces-feedback {action.verdict} {action.concept}")
    if any(action.verdict == "corrected" for action in preview.actions):
        lines.append("撤回不等於永久禁止；持續性的禁止規則請交由 Hermes 原生指示或記憶管理。")
    return "\n".join(lines)
