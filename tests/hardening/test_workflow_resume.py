from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "runtime"))

from execute_workflow import execute_local  # noqa: E402


def _plan():
    return {
        "plan_id": "p1",
        "objective": "resume path",
        "skill_chain": [
            {"step": 1, "skill": "requirements-analysis"},
            {"step": 2, "skill": "backend-engineering"},
            {"step": 3, "skill": "qa"},
        ],
    }


def test_failed_middle_step_stops_and_records_failed_step():
    ok = mock.MagicMock(success=True, output="ok", error=None, requires_hitl=False, hitl_reason="")
    bad = RuntimeError("middle step failure")
    with mock.patch("execute_workflow._make_context_manager", return_value=None), \
         mock.patch("execute_workflow.run_skill_activity", side_effect=[ok, bad, ok]):
        log = execute_local(_plan())
    assert log["status"] == "failed"
    assert log["failed_at_step"] == 2
    assert len(log["steps"]) == 2
    assert log["steps"][1]["status"] == "error"
