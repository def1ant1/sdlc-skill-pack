#!/usr/bin/env python3
"""Route conversation intent into policy-safe planning/execution actions.

Input contract (JSON):
{
  "message": {"id": "m1", "text": "...", "timestamp": "...", "user_id": "..."},
  "context": {
    "conversation_id": "c1",
    "history": [{"role": "user|assistant|system", "text": "..."}],
    "governance": {"allow_execution": false, "require_approval": true},
    "memory": {"enabled": true}
  }
}
"""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from plan_workflow import plan as plan_sdlc  # noqa: E402
from plan_gtm_workflow import build_plan as plan_gtm  # noqa: E402
from detect_skill_gaps import detect_gaps  # noqa: E402
sys.path.insert(0, str(_HERE.parent / "memory"))
from retrieve_context import retrieve  # noqa: E402

INTENTS = [
    "q_and_a", "brainstorm", "create_plan_workflow_skill", "run_skill", "schedule_task",
    "curate_retrieve_knowledge", "clarifying_question", "request_approval", "governed_execution",
]

def _classify(text: str) -> tuple[str, float]:
    t = text.lower()
    rules = [
        ("request_approval", ["approve", "approval", "permission", "sign off"]),
        ("governed_execution", ["execute", "run now", "deploy", "apply changes"]),
        ("schedule_task", ["schedule", "remind", "cron", "later", "tomorrow"]),
        ("run_skill", ["run skill", "invoke skill", "execute skill"]),
        ("create_plan_workflow_skill", ["plan", "workflow", "roadmap", "create skill"]),
        ("curate_retrieve_knowledge", ["retrieve", "knowledge", "memory", "context", "what did we"]),
        ("clarifying_question", ["can you clarify", "what do you mean", "question"]),
        ("brainstorm", ["brainstorm", "ideas", "options"]),
        ("q_and_a", ["what", "how", "why", "?", "explain"]),
    ]
    for label, sigs in rules:
        if any(s in t for s in sigs):
            return label, 0.85
    return "q_and_a", 0.55


def route(payload: dict[str, Any]) -> dict[str, Any]:
    msg = payload.get("message", {})
    ctx = payload.get("context", {})
    text = str(msg.get("text", "")).strip()
    if not text:
        raise ValueError("message.text is required")

    intent, confidence = _classify(text)
    missing = []
    if intent in {"governed_execution", "run_skill", "schedule_task"} and not ctx.get("conversation_id"):
        missing.append("context.conversation_id")

    requires_question = bool(missing) or (intent == "clarifying_question")
    skills = ["requirements-engineering", "gtm-orchestration", "sdlc-memory-token-management"]
    knowledge_actions: list[dict[str, Any]] = []
    dispatch: dict[str, Any] = {"action": "respond"}

    gov = ctx.get("governance", {}) or {}
    allow_execution = bool(gov.get("allow_execution", False))
    require_approval = bool(gov.get("require_approval", True))

    if intent == "create_plan_workflow_skill":
        planner = "gtm" if "gtm" in text.lower() or "go-to-market" in text.lower() else "sdlc"
        dispatch = {"action": "plan", "planner": planner, "result": (plan_gtm(text) if planner == "gtm" else plan_sdlc(text))}
    elif intent == "governed_execution":
        if allow_execution and not require_approval:
            dispatch = {"action": "execute", "executor": "scripts/runtime/execute_workflow.py", "policy_safe": True}
        else:
            dispatch = {"action": "blocked", "reason": "approval_required_or_execution_disabled", "policy_safe": True}
    elif intent == "curate_retrieve_knowledge":
        knowledge_actions.append({"action": "retrieve_context", "query": text, "path": "scripts/memory/retrieve_context.py"})
        try:
            knowledge_actions.append({"action": "retrieve_result", "result": retrieve(text, top_k=3, min_score=0.6)})
        except Exception as exc:
            knowledge_actions.append({"action": "retrieve_error", "error": str(exc)})
        gap = detect_gaps(Path(".").resolve())
        knowledge_actions.append({"action": "detect_skill_gaps", "result": gap})
        dispatch = {"action": "knowledge"}

    return {
        "input_contract_version": "conversation-intent-router.v1",
        "supported_intents": INTENTS,
        "intent": intent,
        "confidence": round(confidence, 2),
        "requires_question": requires_question,
        "missing_information": missing,
        "candidate_skills_workflows": skills,
        "knowledge_actions": knowledge_actions,
        "dispatch": dispatch,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", help="JSON payload path. Reads stdin if omitted.")
    args = parser.parse_args()
    raw = Path(args.input).read_text(encoding="utf-8") if args.input else sys.stdin.read()
    payload = json.loads(raw)
    print(json.dumps(route(payload), indent=2, sort_keys=True))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
