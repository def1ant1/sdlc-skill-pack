"""
Tests for scripts/orchestration/plan_workflow.py

Exercises the SDLC planner's routing logic and output schema.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PLANNER = REPO_ROOT / "scripts" / "orchestration" / "plan_workflow.py"


def plan(objective: str, extra_args: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(PLANNER), objective] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"plan_workflow.py failed:\n{result.stderr}"
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------

class TestOutputSchema:
    def test_required_top_level_keys(self):
        out = plan("Build a REST API")
        for key in ("plan_id", "objective", "skill_chain"):
            assert key in out, f"Missing key: {key}"

    def test_skill_chain_is_list(self):
        out = plan("Build a REST API")
        assert isinstance(out["skill_chain"], list)
        assert len(out["skill_chain"]) > 0

    def test_each_step_has_required_fields(self):
        out = plan("Build a REST API")
        for step in out["skill_chain"]:
            assert "step" in step, f"Step missing 'step': {step}"
            assert "skill" in step, f"Step missing 'skill': {step}"

    def test_step_numbers_are_sequential(self):
        out = plan("Build a REST API")
        steps = [s["step"] for s in out["skill_chain"]]
        assert steps == list(range(1, len(steps) + 1))

    def test_plan_id_is_nonempty_string(self):
        out = plan("Design a microservices architecture")
        assert isinstance(out["plan_id"], str)
        assert len(out["plan_id"]) > 0


# ---------------------------------------------------------------------------
# Routing correctness
# ---------------------------------------------------------------------------

class TestRouting:
    def test_security_objective_includes_devsecops(self):
        out = plan("Implement zero-trust security architecture")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert any("security" in sk or "devsec" in sk for sk in skills), (
            f"Expected a security skill in chain: {skills}"
        )

    def test_requirements_objective_starts_with_requirements(self):
        out = plan("Define requirements for a user authentication system")
        first_skill = out["skill_chain"][0]["skill"]
        assert "requirement" in first_skill.lower(), (
            f"Expected requirements skill first, got: {first_skill}"
        )

    def test_deployment_objective_includes_release(self):
        out = plan("Deploy the application to production")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert any("release" in sk or "deploy" in sk for sk in skills), (
            f"Expected a release/deploy skill: {skills}"
        )

    def test_all_skills_in_chain_are_strings(self):
        out = plan("Build and test a payment service")
        for step in out["skill_chain"]:
            assert isinstance(step["skill"], str)
            assert len(step["skill"]) > 0

    def test_objective_preserved_in_output(self):
        objective = "Implement a graph database integration"
        out = plan(objective)
        assert out["objective"] == objective


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_short_objective(self):
        out = plan("API")
        assert len(out["skill_chain"]) > 0

    def test_long_objective(self):
        objective = " ".join(["Build a scalable, secure, observable microservices platform"] * 5)
        out = plan(objective)
        assert len(out["skill_chain"]) > 0

    def test_output_is_valid_json(self):
        result = subprocess.run(
            [sys.executable, str(PLANNER), "Test objective"],
            capture_output=True, text=True,
        )
        assert result.returncode == 0
        parsed = json.loads(result.stdout)  # Raises if invalid JSON
        assert parsed is not None