"""Intent classification and next-safe-action routing for adaptive intake."""

from __future__ import annotations

from typing import Any
import re

from core.workspace import ConversationStateManager


SAFE_DEFAULT_INTENT = "general_question"
PLAN_ADJUSTMENT_CHIPS = ("seo_audit", "technical", "content", "performance")


def classify_intent(user_message: str) -> dict[str, Any]:
    text = (user_message or "").strip().lower()
    rules: tuple[tuple[str, tuple[str, ...], str, str, tuple[str, ...]], ...] = (
        ("high_risk_advice", (r"medical|legal advice|investment|lawsuit|diagnosis|prescription",), "high", "request_handoff", ("jurisdiction", "facts")),
        ("account_or_billing", (r"billing|invoice|subscription|payment|refund",), "medium", "request_confirmation", ("account_id",)),
        ("task_execution", (r"run|execute|create|implement|write|deploy|fix",), "medium", "propose_plan", ("goal",)),
        ("general_question", (r"\?|explain|what|how|why",), "low", "answer_directly", ()),
    )
    for intent, patterns, risk_level, default_action, required_fields in rules:
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns):
            return {
                "intent": intent,
                "confidence": 0.78,
                "risk_level": risk_level,
                "default_action": default_action,
                "required_fields": list(required_fields),
            }

    return {
        "intent": SAFE_DEFAULT_INTENT,
        "confidence": 0.45,
        "risk_level": "low",
        "default_action": "answer_directly",
        "required_fields": [],
    }


def _compute_missing(required_fields: list[str], facts: dict[str, Any]) -> list[str]:
    return [field for field in required_fields if not facts.get(field)]


def _is_cached_answer_valid(answer_record: dict[str, Any], turn_count: int, scope: str) -> bool:
    if not isinstance(answer_record, dict) or answer_record.get("valid") is False:
        return False
    cached_scope = (answer_record.get("scope") or "global").strip().lower()
    if cached_scope not in {"global", scope}:
        return False
    expires_at_turn = answer_record.get("expires_at_turn")
    return not isinstance(expires_at_turn, int) or turn_count <= expires_at_turn


def _reconcile_turn_state(prior_state: dict[str, Any], turn_patch: dict[str, Any]) -> dict[str, Any]:
    completed_prior = set(prior_state.get("completed_steps", []))
    completed_turn = set(turn_patch.get("completed_steps", []))
    merged_completed = sorted(completed_prior | completed_turn)

    pending_prior = [s for s in prior_state.get("pending_steps", []) if s not in merged_completed]
    pending_turn = [s for s in turn_patch.get("pending_steps", []) if s not in merged_completed]

    merged_pending: list[str] = []
    for step in [*pending_prior, *pending_turn]:
        if step not in merged_pending:
            merged_pending.append(step)

    return {
        **turn_patch,
        "completed_steps": merged_completed,
        "pending_steps": merged_pending,
        "clarification_status": turn_patch.get("clarification_status") or prior_state.get("clarification_status", "not_started"),
    }


def _build_plan_preview(goal: str, pending_steps: list[str], next_action: str) -> dict[str, Any]:
    return {
        "current_objective": goal,
        "planned_steps": pending_steps[:6],
        "next_action": next_action,
    }


def _build_memory_summary(state: dict[str, Any]) -> str:
    completed = ", ".join(state.get("completed_steps", [])[-3:]) or "none"
    pending = ", ".join(state.get("pending_steps", [])[:3]) or "none"
    return f"Goal: {state.get('active_goal', '')}. Completed: {completed}. Pending: {pending}."


def _extract_plan_delta(incoming: dict[str, Any], turn_number: int) -> dict[str, Any] | None:
    adjustment = incoming.get("plan_adjustment")
    if not isinstance(adjustment, dict):
        return None
    chip = adjustment.get("chip")
    if chip not in PLAN_ADJUSTMENT_CHIPS:
        return None
    return {
        "turn": turn_number,
        "chip": chip,
        "instruction": adjustment.get("instruction", ""),
        "delta_type": "user_adjustment",
    }


def route_next_safe_action(state: dict[str, Any]) -> dict[str, Any]:
    facts = dict(state.get("facts", {}))
    missing = _compute_missing(state.get("required_fields", []), facts)
    turn_count = int(state.get("turn_count", 0)) + 1
    clarification_answer_map = state.get("clarification_answer_map") if isinstance(state.get("clarification_answer_map"), dict) else {}
    prohibit_reasking = bool(state.get("prohibit_reasking", False))
    scope = (state.get("active_goal") or "").strip().lower() or "global"
    reask_allowed_reasons = {"contradiction_detected", "scope_changed", "answer_invalid", "clarification_expired"}
    reask_context = state.get("reask_context") if isinstance(state.get("reask_context"), dict) else {}
    reask_reason = (reask_context.get("reason") or "").strip().lower()

    cached_answered = [f for f in missing if _is_cached_answer_valid(clarification_answer_map.get(f, {}), turn_count, scope)]
    missing = [f for f in missing if f not in cached_answered]

    unresolved = [{"field": f, "reason": "Missing and no assumption mode enabled."} for f in missing]
    is_high_risk = state.get("risk_level") == "high" or bool(state.get("policy", {}).get("high_risk", False))
    allow_clarifying = is_high_risk or state.get("clarifying_questions_asked", 0) < 1
    if prohibit_reasking and missing and reask_reason not in reask_allowed_reasons:
        allow_clarifying = False

    if missing and allow_clarifying:
        next_action = "ask_clarifying_question"
        questions = missing if is_high_risk else missing[:1]
        routing_event = "ask"
        routing_event_reason = "missing_required_fields"
    elif missing:
        next_action = "defer_execution"
        questions = []
        routing_event = "reask_block" if prohibit_reasking else "answer"
        routing_event_reason = "prohibit_reasking_enforced" if prohibit_reasking else "clarification_budget_exhausted"
    else:
        next_action = state.get("default_action", "answer_directly")
        questions = []
        routing_event = "answer"
        routing_event_reason = "all_required_fields_resolved"

    return {
        "intent": state["intent"],
        "intent_confidence": state.get("confidence", 0.0),
        "risk_level": state.get("risk_level", "low"),
        "next_safe_action": next_action,
        "facts": facts,
        "open_questions": unresolved,
        "clarifying_questions_to_ask": questions,
        "routing_event": routing_event,
        "routing_event_reason": routing_event_reason,
        "cached_clarification_answers_used": cached_answered,
    }


def orchestrate_conversation(conversation_state: dict[str, Any], session_state: dict[str, Any] | None = None) -> dict[str, Any]:
    manager = ConversationStateManager()
    prior = manager.read(conversation_state)
    incoming = session_state or {}
    classification = classify_intent(incoming.get("user_message", ""))
    routing_input = {**prior, **incoming, **classification}
    routing_input["memory_summary"] = prior.get("memory_summary", "")
    routing = route_next_safe_action(routing_input)
    turn_count = int(prior.get("turn_count", 0)) + 1

    turn_patch = {
        "active_goal": incoming.get("goal", prior.get("active_goal", "")),
        "intent": routing["intent"],
        "intent_confidence": routing["intent_confidence"],
        "workflow_stage": "execution" if routing["next_safe_action"] != "ask_clarifying_question" else "clarification",
        "clarification_status": "answered" if routing["next_safe_action"] != "ask_clarifying_question" else "asked",
        "completed_steps": incoming.get("completed_steps", []),
        "pending_steps": incoming.get("pending_steps", prior.get("pending_steps", [])),
        "execution_status": routing["next_safe_action"],

        "memory_summary": incoming.get("memory_summary", prior.get("memory_summary", "")),
        "turn_count": turn_count,
        "user_message": incoming.get("user_message", ""),
        "prohibit_reasking": bool(incoming.get("prohibit_reasking", prior.get("prohibit_reasking", False))),
    }
    reconciled_patch = _reconcile_turn_state(prior, turn_patch)
    preview = _build_plan_preview(reconciled_patch["active_goal"], reconciled_patch["pending_steps"], routing["next_safe_action"])
    reconciled_patch["plan_preview"] = preview
    reconciled_patch["plan_confirmation"] = {
        "status": incoming.get("plan_confirmation", "pending"),
        "prompt": "Confirm or adjust plan focus.",
        "chips": list(PLAN_ADJUSTMENT_CHIPS),
    }
    interval = int(prior.get("rolling_memory_turn_interval", 3))
    if turn_count % max(interval, 1) == 0:
        summary = _build_memory_summary(reconciled_patch)
        history = list(prior.get("rolling_memory_history", []))
        history.append({"turn": turn_count, "summary": summary})
        reconciled_patch["memory_summary"] = summary
        reconciled_patch["rolling_memory_history"] = history[-10:]

    delta = _extract_plan_delta(incoming, turn_count)
    if delta:
        deltas = list(prior.get("plan_deltas", []))
        deltas.append(delta)
        reconciled_patch["plan_deltas"] = deltas

    clarification_answer_map = dict(prior.get("clarification_answer_map", {}))
    if isinstance(incoming.get("clarification_answer_map"), dict):
        clarification_answer_map.update(incoming["clarification_answer_map"])
    for field in routing.get("cached_clarification_answers_used", []):
        clarification_answer_map.setdefault(field, {"answer": "", "valid": True, "scope": "global"})
    reconciled_patch["clarification_answer_map"] = clarification_answer_map

    history = list(prior.get("clarification_history", []))
    question_key = (routing.get("clarifying_questions_to_ask") or ["none"])[0]
    history.append(
        {
            "turn": turn_count,
            "event": routing.get("routing_event"),
            "question_key": question_key,
            "reason": routing.get("routing_event_reason"),
        }
    )
    reconciled_patch["clarification_history"] = history[-100:]
    next_state = manager.write(prior, reconciled_patch)
    return {**routing, "conversation_state": next_state}
