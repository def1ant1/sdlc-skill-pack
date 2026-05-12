#!/usr/bin/env python3
"""Route a user conversation message to an intent class."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INTENTS = {
    "answer_only",
    "brainstorm",
    "draft_plan",
    "create_task",
    "create_schedule",
    "curate_knowledge",
    "create_skill",
    "create_workflow",
    "run_workflow",
    "ask_clarifying_question",
}

SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "conversation-intent.schema.json"

HIGH_CONFIDENCE_THRESHOLD = 0.85
MID_CONFIDENCE_THRESHOLD = 0.60
HIGH_RISK_WORKFLOW_PATTERNS = [
    r"\b(hipaa|phi|medical records?)\b",
    r"\b(finra|sec filing|sox|basel|aml|kyc)\b",
    r"\b(gdpr|pci|soc\s?2|iso\s?27001)\b",
    r"\b(legal hold|litigation|regulator)\b",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", help="User message text.")
    parser.add_argument("--state", help="Conversation state JSON string (expects last_user_message or messages).")
    parser.add_argument("--state-file", help="Path to a JSON state file.")
    parser.add_argument("--stdin", action="store_true", help="Read JSON state from stdin.")
    return parser.parse_args()


def _load_payload(args: argparse.Namespace) -> dict:
    if args.message:
        return {"message": args.message}
    if args.state:
        return json.loads(args.state)
    if args.state_file:
        return json.loads(Path(args.state_file).read_text(encoding="utf-8"))
    if args.stdin:
        return json.loads(sys.stdin.read())
    raise ValueError("Provide --message, --state, --state-file, or --stdin")


def _extract_message(payload: dict) -> str:
    if isinstance(payload.get("message"), str):
        return payload["message"]
    if isinstance(payload.get("last_user_message"), str):
        return payload["last_user_message"]
    messages = payload.get("messages")
    if isinstance(messages, list):
        for msg in reversed(messages):
            if msg.get("role") == "user" and isinstance(msg.get("content"), str):
                return msg["content"]
    return ""


def _route_intent(message: str) -> tuple[str, float, str]:
    txt = message.lower().strip()
    if not txt:
        return "ask_clarifying_question", 0.55, "No actionable message content detected."

    rules: list[tuple[str, str, float, str]] = [
        (r"\b(run|execute|start)\b.*\b(workflow|plan|pipeline)\b", "run_workflow", 0.95, "User explicitly requested execution."),
        (r"\b(create|build|design|generate)\b.*\bworkflow\b", "create_workflow", 0.94, "User explicitly requested workflow creation."),
        (r"\b(create|make|add)\b.*\b(task|todo|to-do)\b", "create_task", 0.91, "Task creation intent detected."),
        (r"\b(schedule|calendar|timeline|roadmap)\b", "create_schedule", 0.88, "Scheduling/timeline intent detected."),
        (r"\b(brainstorm|ideas|options|alternatives)\b", "brainstorm", 0.86, "Brainstorming language detected."),
        (r"\b(draft|outline|analy[sz]e|review)\b.*\b(plan|strategy|seo|improvements?)\b", "draft_plan", 0.89, "Analysis/drafting language detected with concrete objective."),
        (r"\b(curate|organi[sz]e|summari[sz]e|knowledge base|kb)\b", "curate_knowledge", 0.83, "Knowledge curation intent detected."),
        (r"\b(create|build|author)\b.*\bskill\b", "create_skill", 0.9, "Skill creation intent detected."),
        (r"\b\?\s*$|\b(what|how|why|explain)\b", "answer_only", 0.72, "Question-like request best handled as direct response."),
    ]
    for pattern, intent, confidence, reason in rules:
        if re.search(pattern, txt):
            return intent, confidence, reason
    return "ask_clarifying_question", 0.62, "Intent unclear from message; request clarification."


def _requires_policy_override(payload: dict, message: str) -> tuple[bool, str | None]:
    policy = payload.get("policy") if isinstance(payload.get("policy"), dict) else {}
    if policy.get("force_structured_clarification") is True:
        return True, "Policy explicitly requires structured clarification."

    state = payload.get("conversation_state") if isinstance(payload.get("conversation_state"), dict) else {}
    risk_profile = (state.get("risk_profile") or payload.get("risk_profile") or "").lower()
    if risk_profile in {"regulated", "high-risk", "high_risk", "critical"}:
        return True, f"Risk profile '{risk_profile}' requires structured clarification."

    txt = message.lower()
    for pattern in HIGH_RISK_WORKFLOW_PATTERNS:
        if re.search(pattern, txt):
            return True, "Regulated/high-risk workflow signal detected."
    return False, None


def _compute_routing_mode(confidence: float, force_structured_clarification: bool) -> tuple[str, bool, str]:
    if force_structured_clarification:
        return (
            "required_clarification",
            True,
            "Policy override active: structured clarification remains mandatory for highest-impact missing datum.",
        )
    if confidence > HIGH_CONFIDENCE_THRESHOLD:
        return "execute_or_draft", False, "High confidence intent (>0.85): execute/draft immediately."
    if MID_CONFIDENCE_THRESHOLD <= confidence <= HIGH_CONFIDENCE_THRESHOLD:
        return "optional_single_clarification", False, "Medium confidence intent (0.60-0.85): optional single clarification for highest-impact missing datum."
    return "required_clarification", True, "Low confidence intent (<0.60): clarification is required before execution."


def _build_state_updates(payload: dict, confidence: float, routing_mode: str, routing_rationale: str, requires_clarification: bool) -> dict:
    conversation_state = payload.get("conversation_state") if isinstance(payload.get("conversation_state"), dict) else {}
    workspace_state = payload.get("workspace_state") if isinstance(payload.get("workspace_state"), dict) else {}

    return {
        "conversation_state": {
            **conversation_state,
            "intent_confidence": confidence,
            "routing_mode": routing_mode,
            "routing_rationale": routing_rationale,
            "requires_clarification": requires_clarification,
            "clarification_contract": "optional and limited to highest-impact missing datum" if routing_mode == "optional_single_clarification" else "highest-impact missing datum only",
        },
        "workspace_state": {
            **workspace_state,
            "intent_confidence": confidence,
            "routing_mode": routing_mode,
            "routing_rationale": routing_rationale,
        },
    }


def _validate(result: dict) -> None:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = schema.get("required", [])
    for field in required:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    if result["intent"] not in schema["properties"]["intent"]["enum"]:
        raise ValueError(f"Invalid intent '{result['intent']}'")
    conf = result.get("confidence")
    if not isinstance(conf, (int, float)) or conf < 0 or conf > 1:
        raise ValueError("confidence must be numeric in [0, 1]")


def main() -> int:
    args = parse_args()
    payload = _load_payload(args)
    message = _extract_message(payload)
    intent, confidence, reason = _route_intent(message)
    force_override, override_reason = _requires_policy_override(payload, message)
    routing_mode, requires_clarification, routing_rationale = _compute_routing_mode(confidence, force_override)
    if override_reason:
        routing_rationale = f"{routing_rationale} {override_reason}"
    state_updates = _build_state_updates(payload, confidence, routing_mode, routing_rationale, requires_clarification)

    routed = {
        "intent": intent,
        "confidence": confidence,
        "intent_confidence": confidence,
        "rationale": reason,
        "routing_mode": routing_mode,
        "requires_clarification": requires_clarification,
        "clarification_prompt_contract": "Clarifications are optional and limited to the highest-impact missing datum unless policy override requires structured clarification.",
        "routing_rationale": routing_rationale,
        "policy_override_applied": force_override,
        "policy_override_reason": override_reason,
        "state_updates": state_updates,
        "message_excerpt": message[:240],
    }
    _validate(routed)
    print(json.dumps(routed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
