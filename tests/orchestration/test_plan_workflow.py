"""
Tests for scripts/orchestration/plan_workflow.py

Covers: intent classification, skill chain assembly, output schema,
complexity detection, token budget, quality gates, and edge cases.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "orchestration" / "plan_workflow.py"


def run_plan(objective: str, extra_args: list | None = None) -> dict:
    cmd = [sys.executable, str(SCRIPT), objective] + (extra_args or [])
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, f"Script failed:\n{result.stderr}"
    return json.loads(result.stdout)


# ---------------------------------------------------------------------------
# Backwards-compatible test (Phase 0 contract — must keep passing)
# ---------------------------------------------------------------------------

def test_plan_workflow_ai_security():
    """Original Phase 0 test: AI + security + QA all detected for this prompt."""
    data = run_plan("Build a secure AI API with tests")
    # New schema uses skill_chain instead of required_skills
    skill_names = [s["skill"] for s in data["skill_chain"]]
    assert "ai-engineering" in skill_names
    assert "devsecops" in skill_names
    assert "qa-automation" in skill_names


# ---------------------------------------------------------------------------
# Schema completeness
# ---------------------------------------------------------------------------

class TestOutputSchema:
    REQUIRED_FIELDS = [
        "plan_id", "created", "objective", "complexity",
        "classification_confidence", "detected_phases", "skill_chain",
        "execution_groups", "quality_gates", "memory_strategy",
        "token_budget", "next_action",
    ]

    def test_all_required_fields_present(self):
        data = run_plan("Build a secure REST API with tests")
        for field in self.REQUIRED_FIELDS:
            assert field in data, f"Missing field: {field}"

    def test_plan_id_format(self):
        data = run_plan("Design a payment service")
        assert data["plan_id"].startswith("WP-")
        parts = data["plan_id"].split("-")
        assert len(parts) == 3 and len(parts[1]) == 8  # YYYYMMDD

    def test_objective_preserved_verbatim(self):
        obj = "Build an AI-enabled document processing API"
        data = run_plan(obj)
        assert data["objective"] == obj

    def test_next_action_has_skill(self):
        data = run_plan("Design a system architecture")
        assert data["next_action"]["skill"]

    def test_token_budget_allocation_keys(self):
        data = run_plan("Write unit tests for auth service")
        alloc = data["token_budget"]["allocation"]
        for key in ["planning", "source_context", "reasoning", "output", "buffer"]:
            assert key in alloc

    def test_memory_strategy_sections(self):
        data = run_plan("Build a backend service")
        ms = data["memory_strategy"]
        assert ms["preserve"] and ms["compress_after"]

    def test_skill_chain_steps_sequential(self):
        data = run_plan("Build a secure AI API with tests")
        steps = [s["step"] for s in data["skill_chain"]]
        assert steps == list(range(1, len(steps) + 1))

    def test_each_step_has_required_fields(self):
        data = run_plan("Design and build a microservice")
        for step in data["skill_chain"]:
            for field in ["step", "skill", "phase", "depends_on"]:
                assert field in step


# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

class TestIntentClassification:
    def test_ai_objective(self):
        data = run_plan("Design an LLM-based document extraction pipeline")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "ai-engineering" in phases

    def test_security_objective(self):
        data = run_plan("Perform a threat model and OWASP security review")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "security" in phases

    def test_test_objective(self):
        data = run_plan("Write a comprehensive test strategy and automation plan")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "qa" in phases

    def test_release_objective(self):
        data = run_plan("Create a deployment plan and rollback strategy for v2.0")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "release" in phases

    def test_code_review_objective(self):
        data = run_plan("Review this pull request for maintainability and readability")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "code-review" in phases

    def test_incident_objective(self):
        data = run_plan("Triage this production outage and write a postmortem")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "operations" in phases

    def test_reporting_objective(self):
        data = run_plan("Write an executive summary of delivery health for the board")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "reporting" in phases

    def test_multi_phase_ai_security_qa(self):
        data = run_plan("Build a secure AI API with tests")
        phases = [d["phase"] for d in data["detected_phases"]]
        assert "ai-engineering" in phases
        assert "security" in phases
        assert "qa" in phases

    def test_full_sdlc_complexity(self):
        data = run_plan(
            "Build a production-grade AI-enabled document processing API with "
            "architecture, backend, security review, tests, CI/CD deployment, "
            "monitoring dashboards, and compliance reporting"
        )
        assert data["complexity"] == "full-sdlc"


# ---------------------------------------------------------------------------
# Dependency expansion
# ---------------------------------------------------------------------------

class TestDependencyExpansion:
    def test_backend_plan_includes_architecture(self):
        data = run_plan("Implement a REST API for user management")
        names = [s["skill"] for s in data["skill_chain"]]
        assert "system-architecture" in names

    def test_release_plan_includes_qa_and_security(self):
        data = run_plan("Create a release plan and deployment strategy")
        names = [s["skill"] for s in data["skill_chain"]]
        assert "qa-automation" in names and "devsecops" in names

    def test_no_expand_skips_additions(self):
        data = run_plan("Write unit tests", extra_args=["--no-expand"])
        assert data["dependency_additions"] == []

    def test_dependency_order_arch_before_backend(self):
        data = run_plan("Build a REST API service")
        names = [s["skill"] for s in data["skill_chain"]]
        if "system-architecture" in names and "backend-engineering" in names:
            assert names.index("system-architecture") < names.index("backend-engineering")


# ---------------------------------------------------------------------------
# Quality gates
# ---------------------------------------------------------------------------

class TestQualityGates:
    def test_gates_list_present(self):
        data = run_plan("Design and build a backend service with security review")
        assert isinstance(data["quality_gates"], list)

    def test_gate_fields(self):
        data = run_plan("Build a secure API with tests and deployment")
        for gate in data["quality_gates"]:
            assert "gate_name" in gate and "transition" in gate and "fail_action" in gate

    def test_architecture_gate_when_arch_detected(self):
        data = run_plan("Design a system architecture for a payment platform")
        gate_names = [g["gate_name"] for g in data["quality_gates"]]
        assert "architecture-approved" in gate_names

    def test_no_gate_on_final_skill(self):
        data = run_plan("Build a REST API service")
        assert data["skill_chain"][-1].get("gate_before_next") is None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_vague_input_falls_back_gracefully(self):
        data = run_plan("help me with my project")
        assert len(data["skill_chain"]) >= 1

    def test_single_word_input(self):
        data = run_plan("API")
        assert "skill_chain" in data