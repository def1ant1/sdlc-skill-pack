import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts" / "orchestration" / "route_conversation_intent.py"


def run_router(payload: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--stdin"],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def test_high_confidence_request_routes_to_immediate_execution_or_draft():
    payload = {"message": "Analyze SEO for apotheon.ai and suggest improvements."}
    routed = run_router(payload)

    assert routed["intent"] == "draft_plan"
    assert routed["intent_confidence"] > 0.85
    assert routed["routing_mode"] == "execute_or_draft"
    assert routed["requires_clarification"] is False
    assert routed["state_updates"]["conversation_state"]["intent_confidence"] == routed["intent_confidence"]


def test_medium_confidence_allows_single_optional_clarification():
    payload = {"message": "Can you explain what this should include?"}
    routed = run_router(payload)

    assert 0.60 <= routed["intent_confidence"] <= 0.85
    assert routed["routing_mode"] == "optional_single_clarification"
    assert routed["requires_clarification"] is False
    assert "highest-impact missing datum" in routed["clarification_prompt_contract"].lower()


def test_policy_override_enforces_required_clarification_for_regulated_workflow():
    payload = {
        "message": "Analyze SEO for apotheon.ai and suggest improvements.",
        "policy": {"force_structured_clarification": True},
    }
    routed = run_router(payload)

    assert routed["intent_confidence"] > 0.85
    assert routed["policy_override_applied"] is True
    assert routed["routing_mode"] == "required_clarification"
    assert routed["requires_clarification"] is True


def test_explicit_task_request_auto_switches_to_execute_mode_and_records_reason():
    payload = {"message": "Please analyze website performance and tell me what to fix."}
    routed = run_router(payload)

    assert routed["assistant_mode"] == "execute"
    assert routed["mode_source"] == "inferred_intent"
    assert "analyze website" in routed["mode_reason"].lower()
    selector = routed["state_updates"]["workspace_state"]["mode_selector"]
    assert selector["selected_mode"] == "execute"
    assert "chat" in selector["available_modes"]
    timeline = routed["state_updates"]["workspace_state"]["timeline"]
    assert timeline[-1]["type"] == "assistant.mode.changed"
    assert timeline[-1]["reason"] == routed["mode_reason"]
    assert timeline[-1]["automatic"] is True


def test_user_override_takes_precedence_over_policy_and_inference():
    payload = {
        "message": "analyze website conversion funnel",
        "mode": "review",
        "policy": {"allowed_modes": ["chat", "review"]},
    }
    routed = run_router(payload)
    assert routed["assistant_mode"] == "review"
    assert routed["mode_source"] == "user_override"


def test_pinned_chat_prevents_auto_switching():
    payload = {
        "message": "analyze website conversion funnel",
        "workspace_state": {"pinned_mode": "chat", "assistant_mode": "chat", "timeline": []},
    }
    routed = run_router(payload)

    assert routed["assistant_mode"] == "chat"
    assert routed["mode_source"] == "user_override"
    assert routed["state_updates"]["workspace_state"]["timeline"] == []
