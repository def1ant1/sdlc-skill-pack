import json
from pathlib import Path
import importlib.util

ORCHESTRATOR_PATH = Path(__file__).resolve().parents[2] / "core" / "conversation-orchestrator" / "orchestrator.py"
SPEC = importlib.util.spec_from_file_location("conversation_orchestrator", ORCHESTRATOR_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


def test_user_answers_clarification_then_execute_next_step():
    fixture_path = Path(__file__).resolve().parents[1] / "fixtures" / "conversation-state" / "clarification_to_execution.json"
    fixture = json.loads(fixture_path.read_text())

    result = MODULE.orchestrate_conversation(fixture["prior_state"], fixture["turn_input"])
    state = result["conversation_state"]

    assert state["workflow_stage"] == "execution"
    assert state["clarification_resolved"] is True
    assert "capture_requirements" in state["completed_steps"]
    assert "confirm_schema" in state["completed_steps"]
    assert "implement_next_step" in state["pending_steps"]
    assert state["version"] >= 2
    assert result["next_safe_action"] == "propose_plan"
    assert state["workflow_complete"] is False


def test_workflow_not_complete_on_clarification_alone():
    prior = {
        "workflow_stage": "clarification",
        "execution_status": "ready_to_execute",
        "clarification_resolved": False,
    }
    turn = {"user_message": "yes, that makes sense", "goal": "ship report"}

    state = MODULE.orchestrate_conversation(prior, turn)["conversation_state"]

    assert state["clarification_resolved"] is True
    assert state["workflow_complete"] is False
    assert "missing" in state["completion_reason"]


def test_terminal_failure_marks_done_when_delivered_with_explanation():
    prior = {"goal": "deploy change"}
    turn = {
        "user_message": "execution failed because dependency is unavailable",
        "execution_status": "failed_terminal",
        "workflow_stage": "execution",
        "final_response_synthesized": True,
        "delivery_status": "delivered",
    }

    state = MODULE.orchestrate_conversation(prior, turn)["conversation_state"]

    assert state["workflow_complete"] is True
    assert state["execution_status"] == "failed_terminal"
    assert state["delivery_status"] == "delivered"


def test_recoverable_failure_retry_then_successful_delivery():
    prior = {"goal": "build artifact"}
    failed_turn = {
        "user_message": "run execution",
        "execution_status": "failed_recoverable",
        "workflow_stage": "execution",
        "delivery_status": "awaiting_approval",
    }
    failed_state = MODULE.orchestrate_conversation(prior, failed_turn)["conversation_state"]
    assert failed_state["workflow_complete"] is False

    retry_turn = {
        "user_message": "retry now",
        "execution_status": "success",
        "workflow_stage": "execution",
        "artifact_generated": True,
        "delivery_status": "delivered",
    }
    success_state = MODULE.orchestrate_conversation(failed_state, retry_turn)["conversation_state"]

    assert success_state["workflow_complete"] is True
    assert success_state["execution_status"] == "success"
    assert success_state["delivery_status"] == "delivered"
