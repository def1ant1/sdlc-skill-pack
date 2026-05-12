"""Intent classification and next-safe-action routing for adaptive intake."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import re


@dataclass(frozen=True)
class IntentRule:
    intent: str
    patterns: tuple[str, ...]
    risk_level: str
    default_action: str
    required_fields: tuple[str, ...] = ()


INTENT_RULES: tuple[IntentRule, ...] = (
    IntentRule(
        "high_risk_advice",
        (r"medical|legal advice|investment|lawsuit|diagnosis|prescription",),
        "high",
        "request_handoff",
        ("jurisdiction", "facts"),
    ),
    IntentRule(
        "account_or_billing",
        (r"billing|invoice|subscription|payment|refund",),
        "medium",
        "request_confirmation",
        ("account_id",),
    ),
    IntentRule(
        "task_execution",
        (r"run|execute|create|implement|write|deploy|fix",),
        "medium",
        "propose_plan",
        ("goal",),
    ),
    IntentRule("general_question", (r"\?|explain|what|how|why",), "low", "answer_directly"),
)

SAFE_DEFAULT_INTENT = "general_question"


def classify_intent(user_message: str) -> dict[str, Any]:
    text = (user_message or "").strip().lower()
    for rule in INTENT_RULES:
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in rule.patterns):
            return {
                "intent": rule.intent,
                "confidence": 0.78,
                "risk_level": rule.risk_level,
                "default_action": rule.default_action,
                "required_fields": list(rule.required_fields),
            }

    fallback = next(rule for rule in INTENT_RULES if rule.intent == SAFE_DEFAULT_INTENT)
    return {
        "intent": fallback.intent,
        "confidence": 0.45,
        "risk_level": fallback.risk_level,
        "default_action": fallback.default_action,
        "required_fields": list(fallback.required_fields),
    }


def _compute_missing(required_fields: list[str], facts: dict[str, Any]) -> list[str]:
    return [field for field in required_fields if not facts.get(field)]


def _use_best_assumptions(missing: list[str], assumptions: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, str]]]:
    updates: dict[str, Any] = {}
    open_questions: list[dict[str, str]] = []
    for field in missing:
        assumed = assumptions.get(field)
        if assumed is not None:
            updates[field] = assumed
        else:
            open_questions.append(
                {
                    "field": field,
                    "reason": "Required for safe execution and not provided.",
                }
            )
    return updates, open_questions


def route_next_safe_action(state: dict[str, Any]) -> dict[str, Any]:
    intent = state["intent"]
    facts = dict(state.get("facts", {}))
    missing = _compute_missing(state.get("required_fields", []), facts)

    use_best_assumptions = state.get("use_best_assumptions", False)
    assumption_updates, unresolved = ({}, [])
    if use_best_assumptions:
        assumption_updates, unresolved = _use_best_assumptions(
            missing,
            assumptions=state.get("assumptions_catalog", {}),
        )
        facts.update(assumption_updates)
    else:
        unresolved = [
            {"field": field, "reason": "Missing and no assumption mode enabled."}
            for field in missing
        ]
    missing_after_assumptions = _compute_missing(state.get("required_fields", []), facts)

    policy_high_risk = bool(state.get("policy", {}).get("high_risk", False))
    is_high_risk = state.get("risk_level") == "high" or policy_high_risk
    allow_clarifying = is_high_risk or state.get("clarifying_questions_asked", 0) < 1

    if missing_after_assumptions and allow_clarifying:
        next_action = "ask_clarifying_question"
        questions_to_ask = missing_after_assumptions if is_high_risk else missing_after_assumptions[:1]
    elif missing_after_assumptions:
        next_action = "defer_execution"
        questions_to_ask = []
    else:
        next_action = state.get("default_action", "answer_directly")
        questions_to_ask = []

    return {
        "intent": intent,
        "risk_level": state.get("risk_level", "low"),
        "next_safe_action": next_action,
        "facts": facts,
        "assumptions_used": assumption_updates,
        "open_questions": unresolved,
        "clarifying_questions_to_ask": questions_to_ask,
    }


def orchestrate_conversation(session_state: dict[str, Any]) -> dict[str, Any]:
    classification = classify_intent(session_state.get("user_message", ""))
    merged_state = {
        **session_state,
        **classification,
    }
    return route_next_safe_action(merged_state)
