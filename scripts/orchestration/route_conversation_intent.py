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
        (r"\b(draft|outline)\b.*\b(plan|strategy)\b", "draft_plan", 0.87, "Plan drafting language detected."),
        (r"\b(curate|organi[sz]e|summari[sz]e|knowledge base|kb)\b", "curate_knowledge", 0.83, "Knowledge curation intent detected."),
        (r"\b(create|build|author)\b.*\bskill\b", "create_skill", 0.9, "Skill creation intent detected."),
        (r"\b\?\s*$|\b(what|how|why|explain)\b", "answer_only", 0.72, "Question-like request best handled as direct response."),
    ]
    for pattern, intent, confidence, reason in rules:
        if re.search(pattern, txt):
            return intent, confidence, reason
    return "ask_clarifying_question", 0.62, "Intent unclear from message; request clarification."


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
    routed = {
        "intent": intent,
        "confidence": confidence,
        "rationale": reason,
        "message_excerpt": message[:240],
    }
    _validate(routed)
    print(json.dumps(routed, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
