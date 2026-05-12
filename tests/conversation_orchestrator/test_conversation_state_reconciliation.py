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


def test_orchestrator_adds_plan_preview_and_confirmation_chips():
    prior = {"active_goal": "Improve site", "pending_steps": ["crawl", "fix"]}
    turn = {"user_message": "please execute", "goal": "Improve site"}
    state = MODULE.orchestrate_conversation(prior, turn)["conversation_state"]

    assert state["plan_preview"]["current_objective"] == "Improve site"
    assert state["plan_preview"]["next_action"] == "ask_clarifying_question"
    assert "seo_audit" in state["plan_confirmation"]["chips"]


def test_rolling_summary_and_plan_delta_are_persisted():
    prior = {"turn_count": 2, "rolling_memory_turn_interval": 3, "pending_steps": ["step-a"]}
    turn = {"user_message": "create content plan", "plan_adjustment": {"chip": "content", "instruction": "prioritize blog refresh"}}
    state = MODULE.orchestrate_conversation(prior, turn)["conversation_state"]

    assert state["turn_count"] == 3
    assert len(state["rolling_memory_history"]) == 1
    assert "Goal:" in state["memory_summary"]
    assert state["plan_deltas"][-1]["chip"] == "content"
