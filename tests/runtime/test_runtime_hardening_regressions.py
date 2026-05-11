from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "runtime"))

from execute_workflow import execute_local
from skill_activity import SkillActivityInput, run_skill_activity


def test_dry_run_never_calls_external_provider():
    plan = {"plan_id": "p", "objective": "o", "skill_chain": [{"step": 1, "skill": "backend-engineering"}]}
    with mock.patch("execute_workflow.run_skill_activity") as run_skill:
        out = execute_local(plan, dry_run=True)
    run_skill.assert_not_called()
    assert out["status"] == "dry_run"


def test_structured_output_required_in_live_mode():
    inp = SkillActivityInput("backend-engineering", "build api")
    with mock.patch.dict(os.environ, {"APOTHEON_PROVIDER": "local", "APOTHEON_DRY_RUN": "0"}), \
         mock.patch("skill_activity.load_skill_contract", return_value="contract"), \
         mock.patch("skill_activity.call_claude", return_value=("not-json", 5, 5)):
        result = run_skill_activity(inp)
    assert result.success is False
    assert "valid JSON" in result.error


def test_dry_run_local_stub_produces_structured_output():
    inp = SkillActivityInput("backend-engineering", "build api")
    with mock.patch.dict(os.environ, {"APOTHEON_DRY_RUN": "1"}), \
         mock.patch("skill_activity.load_skill_contract", return_value="contract"):
        result = run_skill_activity(inp)
    assert result.success is True
    assert result.structured_output["status"] == "dry_run"
