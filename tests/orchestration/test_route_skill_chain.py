"""
Tests for scripts/orchestration/route_skill_chain.py

Covers: single-phase, multi-phase, full-SDLC, dependency expansion,
dependency order, unknown skill detection, and parallel group detection.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "orchestration" / "route_skill_chain.py"


def route(skills: list[str], expand: bool = True) -> dict:
    """Call the script via subprocess and return parsed JSON output."""
    cmd = [sys.executable, str(SCRIPT)]
    if not expand:
        cmd.append("--no-expand")
    result = subprocess.run(
        cmd,
        input=json.dumps(skills),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Script failed: {result.stderr}"
    return json.loads(result.stdout)


def skill_order(chain: dict) -> list[str]:
    return [step["skill"] for step in chain["skill_chain"]]


# ---------------------------------------------------------------------------
# Single-phase
# ---------------------------------------------------------------------------

class TestSinglePhase:
    def test_single_skill_complexity(self):
        result = route(["code-review"])
        assert result["complexity"] == "single-phase"

    def test_single_skill_chain_length(self):
        result = route(["code-review"])
        assert len(result["skill_chain"]) == 1

    def test_standalone_skill_no_deps(self):
        result = route(["requirements-engineering"])
        assert result["skill_chain"][0]["depends_on"] == []

    def test_no_gate_on_last_step(self):
        result = route(["code-review"])
        assert result["skill_chain"][-1]["gate_before_next"] is None

    def test_executive_reporting_standalone(self):
        result = route(["executive-reporting"])
        assert result["complexity"] == "single-phase"
        assert result["skill_chain"][0]["depends_on"] == []


# ---------------------------------------------------------------------------
# Multi-phase
# ---------------------------------------------------------------------------

class TestMultiPhase:
    def test_multi_phase_complexity(self):
        result = route(["backend-engineering", "devsecops", "qa-automation"])
        assert result["complexity"] == "multi-phase"

    def test_dependency_order_arch_before_backend(self):
        # system-architecture must precede backend-engineering
        result = route(["backend-engineering", "devsecops"])
        order = skill_order(result)
        assert order.index("system-architecture") < order.index("backend-engineering")

    def test_dependency_order_backend_before_qa(self):
        result = route(["backend-engineering", "qa-automation"])
        order = skill_order(result)
        assert order.index("backend-engineering") < order.index("qa-automation")

    def test_dependency_order_devsecops_before_release(self):
        result = route(["devsecops", "release-management"])
        order = skill_order(result)
        assert order.index("devsecops") < order.index("release-management")

    def test_dependency_order_qa_before_release(self):
        result = route(["qa-automation", "release-management"])
        order = skill_order(result)
        assert order.index("qa-automation") < order.index("release-management")

    def test_dependency_order_release_before_observability(self):
        result = route(["release-management", "observability"])
        order = skill_order(result)
        assert order.index("release-management") < order.index("observability")

    def test_gate_present_between_phases(self):
        result = route(["system-architecture", "backend-engineering"])
        arch_step = next(s for s in result["skill_chain"] if s["skill"] == "system-architecture")
        assert arch_step["gate_before_next"] == "architecture-approved"

    def test_gate_absent_on_final_step(self):
        result = route(["system-architecture", "backend-engineering"])
        assert result["skill_chain"][-1]["gate_before_next"] is None

    def test_ai_and_backend_parallel_possible(self):
        result = route(["system-architecture", "ai-engineering", "backend-engineering"])
        # Both ai-engineering and backend-engineering depend on system-architecture
        # and are listed as parallel_with each other
        groups = result["execution_groups"]
        parallel_group = next((g for g in groups if len(g["skills"]) > 1), None)
        # At least one parallel group should exist
        assert parallel_group is not None
        members = parallel_group["skills"]
        assert "ai-engineering" in members or "backend-engineering" in members


# ---------------------------------------------------------------------------
# Full SDLC
# ---------------------------------------------------------------------------

class TestFullSDLC:
    def test_full_sdlc_flag(self):
        cmd = [sys.executable, str(SCRIPT), "--full-sdlc"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        assert result.returncode == 0
        data = json.loads(result.stdout)
        assert data["complexity"] == "full-sdlc"

    def test_full_sdlc_all_skills_present(self):
        cmd = [sys.executable, str(SCRIPT), "--full-sdlc"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        names = skill_order(data)
        expected = [
            "requirements-engineering", "system-architecture", "backend-engineering",
            "devsecops", "qa-automation", "release-management", "observability",
        ]
        for skill in expected:
            assert skill in names

    def test_full_sdlc_steps_are_numbered_sequentially(self):
        cmd = [sys.executable, str(SCRIPT), "--full-sdlc"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        steps = [s["step"] for s in data["skill_chain"]]
        assert steps == list(range(1, len(steps) + 1))

    def test_full_sdlc_requirements_is_first(self):
        cmd = [sys.executable, str(SCRIPT), "--full-sdlc"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        data = json.loads(result.stdout)
        assert data["skill_chain"][0]["skill"] == "requirements-engineering"


# ---------------------------------------------------------------------------
# Dependency expansion
# ---------------------------------------------------------------------------

class TestDependencyExpansion:
    def test_backend_expands_to_include_architecture(self):
        result = route(["backend-engineering"])
        names = skill_order(result)
        assert "system-architecture" in names

    def test_release_expands_to_include_qa_and_security(self):
        result = route(["release-management"])
        names = skill_order(result)
        assert "qa-automation" in names
        assert "devsecops" in names

    def test_no_expand_flag_skips_expansion(self):
        result = route(["backend-engineering"], expand=False)
        names = skill_order(result)
        assert "system-architecture" not in names

    def test_dependency_additions_field_populated(self):
        result = route(["backend-engineering"])
        assert "system-architecture" in result["dependency_additions"]

    def test_no_duplicate_skills_after_expansion(self):
        result = route(["backend-engineering", "system-architecture"])
        names = skill_order(result)
        assert len(names) == len(set(names))


# ---------------------------------------------------------------------------
# Unknown skill detection
# ---------------------------------------------------------------------------

class TestUnknownSkills:
    def test_unknown_skill_reported(self):
        result = route(["not-a-real-skill"])
        assert "not-a-real-skill" in result["unknown_skills"]

    def test_unknown_skill_excluded_from_chain(self):
        result = route(["not-a-real-skill"])
        names = skill_order(result)
        assert "not-a-real-skill" not in names

    def test_warning_emitted_for_unknown(self):
        result = route(["not-a-real-skill"])
        assert "warnings" in result
        assert any("not-a-real-skill" in w for w in result["warnings"])

    def test_known_skills_still_routed_alongside_unknown(self):
        result = route(["code-review", "unknown-skill-xyz"])
        names = skill_order(result)
        assert "code-review" in names

    def test_all_unknown_returns_empty_chain(self):
        result = route(["not-a-skill", "also-not-a-skill"])
        assert result["skill_chain"] == []


# ---------------------------------------------------------------------------
# Dependency order invariants
# ---------------------------------------------------------------------------

class TestDependencyOrderInvariants:
    def test_architecture_always_before_ai_engineering(self):
        result = route(["ai-engineering"])
        order = skill_order(result)
        assert order.index("system-architecture") < order.index("ai-engineering")

    def test_architecture_always_before_frontend(self):
        result = route(["frontend-engineering"])
        order = skill_order(result)
        assert order.index("system-architecture") < order.index("frontend-engineering")

    def test_backend_before_frontend(self):
        result = route(["frontend-engineering"])
        order = skill_order(result)
        assert order.index("backend-engineering") < order.index("frontend-engineering")

    def test_observability_after_release(self):
        result = route(["observability"])
        order = skill_order(result)
        assert order.index("release-management") < order.index("observability")

    def test_sre_after_observability(self):
        result = route(["sre-incident-response"])
        order = skill_order(result)
        assert order.index("observability") < order.index("sre-incident-response")

    def test_compliance_after_devsecops_and_qa(self):
        result = route(["compliance-governance"])
        order = skill_order(result)
        assert order.index("devsecops") < order.index("compliance-governance")
        assert order.index("qa-automation") < order.index("compliance-governance")