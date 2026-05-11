"""
Unit tests for execute_workflow.py.

Tests the local execution engine, context manager wiring, dry-run mode,
and Temporal error handling — all without live Qdrant, Temporal, or Claude.
"""
from __future__ import annotations

import json
import sys
import unittest.mock as mock
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
_RUNTIME_PATH = str(REPO_ROOT / "scripts" / "runtime")
if _RUNTIME_PATH not in sys.path:
    sys.path.insert(0, _RUNTIME_PATH)

from execute_workflow import execute_local, execute_temporal  # noqa: E402


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_plan(objective: str = "Test objective", skills: list[str] | None = None) -> dict:
    if skills is None:
        skills = ["requirements-analysis", "backend-engineering"]
    return {
        "plan_id": "TEST-PLAN-001",
        "objective": objective,
        "skill_chain": [
            {"step": i + 1, "skill": s, "phase": s}
            for i, s in enumerate(skills)
        ],
    }


def _mock_skill_result(success: bool = True, output: str = "skill output", requires_hitl: bool = False):
    result = mock.MagicMock()
    result.success = success
    result.output = output
    result.error = None if success else "skill failed"
    result.requires_hitl = requires_hitl
    result.hitl_reason = "approval required" if requires_hitl else ""
    return result


# ---------------------------------------------------------------------------
# Dry-run mode
# ---------------------------------------------------------------------------

class TestDryRun:
    def test_dry_run_returns_dry_run_status(self):
        plan = _make_plan()
        log = execute_local(plan, dry_run=True)
        assert log["status"] == "dry_run"

    def test_dry_run_produces_correct_step_count(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering", "qa"])
        log = execute_local(plan, dry_run=True)
        assert len(log["steps"]) == 3

    def test_dry_run_all_steps_marked_dry_run(self):
        plan = _make_plan()
        log = execute_local(plan, dry_run=True)
        for step in log["steps"]:
            assert step["status"] == "dry_run"

    def test_dry_run_preserves_objective(self):
        objective = "Deploy to production safely"
        plan = _make_plan(objective=objective)
        log = execute_local(plan, dry_run=True)
        assert log["objective"] == objective

    def test_dry_run_preserves_plan_id(self):
        plan = _make_plan()
        log = execute_local(plan, dry_run=True)
        assert log["plan_id"] == "TEST-PLAN-001"

    def test_dry_run_step_numbers_are_sequential(self):
        plan = _make_plan(skills=["a", "b", "c"])
        log = execute_local(plan, dry_run=True)
        assert [s["step"] for s in log["steps"]] == [1, 2, 3]

    def test_dry_run_total_steps_matches_plan(self):
        skills = ["requirements-analysis", "backend-engineering", "qa", "devsecops"]
        plan = _make_plan(skills=skills)
        log = execute_local(plan, dry_run=True)
        assert log["total_steps"] == 4

    def test_dry_run_does_not_call_context_manager(self):
        plan = _make_plan()
        with mock.patch("execute_workflow._make_context_manager") as mock_cm:
            execute_local(plan, dry_run=True)
            mock_cm.assert_not_called()


# ---------------------------------------------------------------------------
# Local execution — success path
# ---------------------------------------------------------------------------

class TestLocalExecutionSuccess:
    def test_completed_status_on_all_success(self):
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["status"] == "completed"

    def test_step_status_completed_on_success(self):
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["steps"][0]["status"] == "completed"

    def test_artifacts_accumulated_across_steps(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        # Both steps completed; verify 2 completed records
        assert sum(1 for s in log["steps"] if s["status"] == "completed") == 2

    def test_run_id_present_and_non_empty(self):
        plan = _make_plan()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["run_id"] and log["run_id"].startswith("RUN-")

    def test_mode_is_local(self):
        plan = _make_plan()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["mode"] == "local"


# ---------------------------------------------------------------------------
# Local execution — failure paths
# ---------------------------------------------------------------------------

class TestLocalExecutionFailure:
    def test_failed_status_when_skill_fails(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result(success=False)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["status"] == "failed"

    def test_failed_at_step_recorded(self):
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result(success=False)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["failed_at_step"] == 1

    def test_execution_stops_after_failure(self):
        """Subsequent steps should not run after a failure."""
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering", "qa"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result(success=False)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        # Only 1 step executed before stopping
        assert len(log["steps"]) == 1

    def test_exception_in_skill_sets_error_status(self):
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity", side_effect=RuntimeError("API down")), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["status"] == "failed"
        assert log["steps"][0]["status"] == "error"
        assert "API down" in log["steps"][0]["error"]


# ---------------------------------------------------------------------------
# HITL pause
# ---------------------------------------------------------------------------

class TestHITLPause:
    def test_paused_for_hitl_status(self):
        plan = _make_plan(skills=["devsecops", "cloud-deployment"])
        with mock.patch("execute_workflow.run_skill_activity",
                        return_value=_mock_skill_result(requires_hitl=True)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["status"] == "paused_for_hitl"

    def test_paused_at_step_recorded(self):
        plan = _make_plan(skills=["devsecops"])
        with mock.patch("execute_workflow.run_skill_activity",
                        return_value=_mock_skill_result(requires_hitl=True)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["paused_at_step"] == 1

    def test_hitl_step_has_pending_hitl_status(self):
        plan = _make_plan(skills=["devsecops"])
        with mock.patch("execute_workflow.run_skill_activity",
                        return_value=_mock_skill_result(requires_hitl=True)), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["steps"][0]["status"] == "pending_hitl"
        assert log["steps"][0]["hitl_required"] is True


# ---------------------------------------------------------------------------
# Context manager wiring
# ---------------------------------------------------------------------------

class TestContextManagerIntegration:
    def _make_cm_mock(self):
        cm = mock.MagicMock()
        cm.load.return_value = {
            "objective": "Test",
            "phase": "",
            "decisions": [],
            "constraints": [],
            "artifacts": [],
            "risks": [],
            "next_action": "",
        }
        cm.retrieve_relevant.return_value = []
        return cm

    def test_context_manager_load_called_once(self):
        plan = _make_plan(skills=["requirements-analysis"])
        cm = self._make_cm_mock()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)
        cm.load.assert_called_once()

    def test_save_step_called_for_each_success(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering"])
        cm = self._make_cm_mock()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)
        assert cm.save_step.call_count == 2

    def test_finalize_called_with_completed_on_success(self):
        plan = _make_plan(skills=["requirements-analysis"])
        cm = self._make_cm_mock()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)
        cm.finalize.assert_called_once_with("completed")

    def test_finalize_called_with_failed_on_error(self):
        plan = _make_plan(skills=["requirements-analysis"])
        cm = self._make_cm_mock()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result(success=False)), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)
        cm.finalize.assert_called_once_with("failed")

    def test_retrieve_relevant_called_per_step(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering"])
        cm = self._make_cm_mock()
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)
        assert cm.retrieve_relevant.call_count == 2

    def test_context_manager_none_does_not_crash(self):
        """If ContextManager is unavailable, execution continues without persistence."""
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity", return_value=_mock_skill_result()), \
             mock.patch("execute_workflow._make_context_manager", return_value=None):
            log = execute_local(plan)
        assert log["status"] == "completed"

    def test_memory_observations_appended_to_additional_context(self):
        """Relevant memory observations should be injected into the skill prompt."""
        plan = _make_plan(skills=["backend-engineering"])
        cm = self._make_cm_mock()
        cm.retrieve_relevant.return_value = [
            {"payload": {"skill": "requirements-analysis", "output_preview": "use PostgreSQL"}}
        ]
        captured_inputs = []

        def capture(inp):
            captured_inputs.append(inp)
            return _mock_skill_result()

        with mock.patch("execute_workflow.run_skill_activity", side_effect=capture), \
             mock.patch("execute_workflow._make_context_manager", return_value=cm):
            execute_local(plan)

        assert captured_inputs
        assert "use PostgreSQL" in captured_inputs[0].additional_context


# ---------------------------------------------------------------------------
# Temporal — import guard
# ---------------------------------------------------------------------------

class TestTemporalImportGuard:
    def test_raises_runtime_error_when_temporalio_missing(self):
        with mock.patch.dict("sys.modules", {"temporalio": None}):
            with pytest.raises((RuntimeError, ImportError)):
                execute_temporal(_make_plan())

class TestDryRunGovernanceAndDeterminism:
    def test_dry_run_never_calls_skill_activity(self):
        plan = _make_plan(skills=["requirements-analysis"])
        with mock.patch("execute_workflow.run_skill_activity") as run_skill:
            log = execute_local(plan, dry_run=True)
        run_skill.assert_not_called()
        assert log["status"] == "dry_run"

    def test_dry_run_is_deterministic_across_repeated_runs(self):
        plan = _make_plan(skills=["requirements-analysis", "backend-engineering"])
        first = execute_local(plan, dry_run=True)
        second = execute_local(plan, dry_run=True)
        assert first == second

    def test_governance_hitl_still_enforced_in_dry_run_classification(self):
        plan = _make_plan(skills=["devsecops"])
        log = execute_local(plan, dry_run=True)
        assert log["steps"][0]["side_effect_classification"] == "simulated-mutation"
