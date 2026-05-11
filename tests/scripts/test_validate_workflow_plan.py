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


def test_missing_skill_fails() -> None:
    result = run_validator("missing-skill.yaml")
    assert result.returncode != 0
    assert "missing prerequisite skill" in result.stdout


def test_unknown_governance_policy_fails() -> None:
    result = run_validator("unknown-policy.yaml")
    assert result.returncode != 0
    assert "unknown governance policy ref" in result.stdout


def test_circular_dependencies_fail() -> None:
    result = run_validator("circular-deps.yaml")
    assert result.returncode != 0
    assert "circular step dependencies detected" in result.stdout
