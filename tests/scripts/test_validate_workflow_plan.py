from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent
VALIDATOR = REPO_ROOT / "scripts" / "validation" / "validate_workflow_plan.py"
FIXTURES = REPO_ROOT / "tests" / "fixtures" / "workflow-plans"


def run_validator(plan_name: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), str(FIXTURES / plan_name), "--root", str(REPO_ROOT)],
        capture_output=True,
        text=True,
    )


def test_valid_plan_passes() -> None:
    result = run_validator("valid-plan.yaml")
    assert result.returncode == 0, result.stdout


def test_invalid_skill_reference_fails() -> None:
    result = run_validator("missing-skill.yaml")
    assert result.returncode != 0
    assert "missing prerequisite skill" in result.stdout


def test_missing_step_policies_fail() -> None:
    result = run_validator("missing-step-policies.yaml")
    assert result.returncode != 0
    assert "must include governance_policy_refs" in result.stdout


def test_duplicate_step_order_fails() -> None:
    result = run_validator("duplicate-order.yaml")
    assert result.returncode != 0
    assert "duplicate step order values detected" in result.stdout


def test_circular_dependencies_fail() -> None:
    result = run_validator("circular-deps.yaml")
    assert result.returncode != 0
    assert "circular step dependencies detected" in result.stdout
