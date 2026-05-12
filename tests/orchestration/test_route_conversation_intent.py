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
