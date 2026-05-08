"""
Tests for scripts/orchestration/plan_gtm_workflow.py

Validates GTM planner routing, skill name alignment, and output schema.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
GTM_PLANNER = REPO_ROOT / "scripts" / "orchestration" / "plan_gtm_workflow.py"

# GTM planner must route to these exact skill names (used as Temporal activity IDs)
EXPECTED_GTM_SKILLS = {
    "launch-planning",
    "seo-engineering",
    "content-marketing",
    "ai-search-optimization",
    "paid-acquisition",
    "analytics-intelligence",
    "customer-success",
    "revenue-optimization",
}


def gtm_plan(objective: str, extra_args: list[str] | None = None) -> dict:
    cmd = [sys.executable, str(GTM_PLANNER), objective] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"plan_gtm_workflow.py failed:\n{result.stderr}"
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestOutputSchema:
    def test_required_keys_present(self):
        out = gtm_plan("Launch a new SaaS product")
        for key in ("plan_id", "objective", "skill_chain"):
            assert key in out, f"Missing key: {key}"

    def test_skill_chain_nonempty(self):
        out = gtm_plan("Launch a new SaaS product")
        assert isinstance(out["skill_chain"], list)
        assert len(out["skill_chain"]) >= 1

    def test_each_step_has_skill_and_step_number(self):
        out = gtm_plan("GTM for developer tools")
        for step in out["skill_chain"]:
            assert "step" in step
            assert "skill" in step

    def test_step_numbers_sequential(self):
        out = gtm_plan("Launch B2B product")
        steps = [s["step"] for s in out["skill_chain"]]
        assert steps == list(range(1, len(steps) + 1))


# ---------------------------------------------------------------------------
# Routing correctness
# ---------------------------------------------------------------------------

class TestSkillNameAlignment:
    def test_all_routed_skills_are_known_gtm_skills(self):
        """Every skill in the GTM chain must be a registered GTM skill name."""
        out = gtm_plan("Full product launch")
        unknown = [
            s["skill"] for s in out["skill_chain"]
            if s["skill"] not in EXPECTED_GTM_SKILLS
        ]
        assert not unknown, f"Routed to unknown GTM skills: {unknown}"

    def test_gtm_skills_exist_on_disk(self):
        """Each GTM skill name must have a SKILL.md on disk."""
        for skill_name in EXPECTED_GTM_SKILLS:
            path = REPO_ROOT / "skills" / skill_name / "SKILL.md"
            assert path.exists(), f"GTM skill missing SKILL.md: {skill_name}"

    def test_launch_objective_includes_launch_planning(self):
        out = gtm_plan("Plan and execute product launch")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert "launch-planning" in skills

    def test_seo_objective_includes_seo_engineering(self):
        out = gtm_plan("Improve organic search visibility")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert "seo-engineering" in skills

    def test_revenue_objective_includes_revenue_optimization(self):
        out = gtm_plan("Optimize revenue and reduce churn")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert "revenue-optimization" in skills

    def test_analytics_objective_includes_analytics_intelligence(self):
        out = gtm_plan("Set up product analytics and attribution")
        skills = [s["skill"] for s in out["skill_chain"]]
        assert "analytics-intelligence" in skills


# ---------------------------------------------------------------------------
# No false positives from SDLC planner
# ---------------------------------------------------------------------------

class TestGTMVsSDLCSeparation:
    def test_gtm_plan_does_not_include_sdlc_skills(self):
        """GTM planner must not route to SDLC engineering skills."""
        sdlc_skills = {"backend", "frontend", "qa", "devsecops", "architecture"}
        out = gtm_plan("Launch product with full GTM motion")
        routed = {s["skill"] for s in out["skill_chain"]}
        overlap = routed & sdlc_skills
        assert not overlap, f"GTM plan incorrectly routed to SDLC skills: {overlap}"