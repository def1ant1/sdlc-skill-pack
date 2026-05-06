"""
Orchestration regression suite — P1-014

Tests the full orchestration pipeline end-to-end:
  plan_workflow → route_skill_chain → validate_workflow_state

Also runs the benchmark prompt set (P1-013) to verify classification
accuracy meets the >90% target defined in P1-003.
"""
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.parent
PLAN_SCRIPT = ROOT / "scripts" / "orchestration" / "plan_workflow.py"
ROUTE_SCRIPT = ROOT / "scripts" / "orchestration" / "route_skill_chain.py"
VALIDATE_SCRIPT = ROOT / "scripts" / "orchestration" / "validate_workflow_state.py"
FIXTURES = ROOT / "tests" / "fixtures" / "orchestration-prompts.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def run(script: Path, stdin: str | None = None, args: list | None = None) -> tuple[str, int]:
    cmd = [sys.executable, str(script)] + (args or [])
    result = subprocess.run(cmd, input=stdin, capture_output=True, text=True)
    return result.stdout, result.returncode


def plan(objective: str) -> dict:
    out, code = run(PLAN_SCRIPT, args=[objective])
    assert code == 0, f"plan_workflow failed: {out}"
    return json.loads(out)


def route(skills: list[str]) -> dict:
    out, code = run(ROUTE_SCRIPT, stdin=json.dumps(skills))
    assert code == 0, f"route_skill_chain failed: {out}"
    return json.loads(out)


def validate(packet: dict, next_phase: str | None = None) -> tuple[dict, int]:
    args = ["--next-phase", next_phase] if next_phase else []
    out, code = run(VALIDATE_SCRIPT, stdin=json.dumps(packet), args=args)
    return json.loads(out), code


# ---------------------------------------------------------------------------
# Minimal valid packet builder
# ---------------------------------------------------------------------------

def make_packet(**overrides) -> dict:
    base = {
        "packet_id": "MP-20260506-001",
        "version": "1.0",
        "created_at": "2026-05-06T09:00:00Z",
        "updated_at": "2026-05-06T12:00:00Z",
        "project": {
            "name": "Regression Test",
            "objective": "Test the orchestration pipeline",
            "complexity": "multi-phase",
        },
        "phase_status": {"architecture": "complete", "backend": "in_progress"},
        "current_phase": "backend",
        "artifacts": [],
        "quality_gate_status": [
            {"gate_name": "architecture-approved",
             "transition": "architecture → backend",
             "status": "PASS"}
        ],
        "open_questions": [],
        "next_action": {
            "description": "Complete backend phase.",
            "skill": "backend-engineering",
        },
    }
    base.update(overrides)
    return base


# ---------------------------------------------------------------------------
# Pipeline integration — plan → validate
# ---------------------------------------------------------------------------

class TestPipelineIntegration:
    """End-to-end: plan_workflow output feeds validate_workflow_state."""

    def test_plan_produces_valid_schema(self):
        data = plan("Build a secure REST API with tests")
        assert "skill_chain" in data
        assert "quality_gates" in data
        assert "next_action" in data

    def test_plan_next_action_skill_is_in_chain(self):
        data = plan("Design and implement a payment service")
        chain_skills = {s["skill"] for s in data["skill_chain"]}
        assert data["next_action"]["skill"] in chain_skills

    def test_plan_detected_phases_match_chain(self):
        data = plan("Build a secure AI API with tests")
        chain_skills = {s["skill"] for s in data["skill_chain"]}
        detected_skills = {d["skill"] for d in data["detected_phases"]}
        # Every detected skill should appear in the chain
        assert detected_skills <= chain_skills

    def test_plan_then_validate_passing_packet(self):
        """A well-formed packet built from plan output validates successfully."""
        data = plan("Build a REST API")
        first_skill = data["skill_chain"][0]["skill"]
        first_phase = data["skill_chain"][0]["phase"]
        packet = make_packet(
            phase_status={first_phase: "in_progress"},
            current_phase=first_phase,
            quality_gate_status=[],
            next_action={"description": "Start.", "skill": first_skill},
        )
        result, code = validate(packet)
        assert result["valid"], f"Pipeline packet failed validation: {result['errors']}"
        assert code == 0

    def test_plan_gate_names_match_validator_expectations(self):
        """Gate names in plan output must be recognised by the validator."""
        data = plan("Build a secure API with QA and release")
        # Extract gate names from plan
        gate_names = {g["gate_name"] for g in data["quality_gates"]}
        # Build a packet with one of those gates as FAIL and verify validator catches it
        if not gate_names:
            pytest.skip("No gates produced for this objective")
        gate_name = next(iter(gate_names))
        packet = make_packet(
            quality_gate_status=[
                {"gate_name": gate_name, "transition": "architecture → backend", "status": "FAIL"}
            ]
        )
        result, code = validate(packet)
        # Should fail due to gate blocking (backend is in_progress but gate FAIL)
        gate_codes = [e["code"] for e in result["errors"]]
        assert "GATE_BLOCKING_VIOLATION" in gate_codes or not result["valid"]

    def test_full_sdlc_plan_has_multiple_gates(self):
        data = plan(
            "Build a production AI API with architecture, security review, tests, and deployment"
        )
        assert len(data["quality_gates"]) >= 3

    def test_route_output_compatible_with_plan_output(self):
        """route_skill_chain and plan_workflow agree on dependency order."""
        obj = "Implement a backend service with security review"
        plan_data = plan(obj)
        plan_skills = [s["skill"] for s in plan_data["skill_chain"]]

        route_data = route(plan_skills)
        route_skills = [s["skill"] for s in route_data["skill_chain"]]

        # Both must produce the same ordered set of skills
        assert plan_skills == route_skills


# ---------------------------------------------------------------------------
# Benchmark prompt classification accuracy (P1-003 target: >90%)
# ---------------------------------------------------------------------------

class TestBenchmarkAccuracy:
    @pytest.fixture(scope="class")
    def benchmark_prompts(self):
        return json.loads(FIXTURES.read_text(encoding="utf-8"))["prompts"]

    def test_fixture_file_exists(self):
        assert FIXTURES.exists(), f"Benchmark fixture missing: {FIXTURES}"

    def test_fixture_has_minimum_prompts(self, benchmark_prompts):
        assert len(benchmark_prompts) >= 25, (
            f"Expected >=25 prompts, got {len(benchmark_prompts)}"
        )

    def test_fixture_covers_all_sdlc_phases(self, benchmark_prompts):
        all_expected = set()
        for p in benchmark_prompts:
            all_expected.update(p.get("expected_phases", []))
        required_phases = {
            "requirements", "architecture", "ai-engineering", "backend",
            "security", "qa", "release", "observability", "operations",
            "compliance", "reporting",
        }
        missing = required_phases - all_expected
        assert not missing, f"Fixture missing coverage for phases: {missing}"

    def test_fixture_has_multi_phase_prompts(self, benchmark_prompts):
        multi = [p for p in benchmark_prompts if p["category"] == "multi-phase"]
        assert len(multi) >= 5

    def test_fixture_has_ambiguous_prompts(self, benchmark_prompts):
        ambiguous = [p for p in benchmark_prompts if p["category"] == "ambiguous"]
        assert len(ambiguous) >= 1

    def test_classification_accuracy_above_threshold(self, benchmark_prompts):
        """
        For every non-ambiguous prompt with at least one expected phase,
        the plan_workflow classifier must detect at least one of the expected
        phases. Threshold: >90%.
        """
        candidates = [
            p for p in benchmark_prompts
            if p["category"] != "ambiguous" and p.get("expected_phases")
        ]
        if not candidates:
            pytest.skip("No evaluable prompts found")

        hits = 0
        misses = []
        for prompt_entry in candidates:
            data = plan(prompt_entry["prompt"])
            detected = {d["phase"] for d in data["detected_phases"]}
            expected = set(prompt_entry["expected_phases"])
            if detected & expected:
                hits += 1
            else:
                misses.append({
                    "id": prompt_entry["id"],
                    "prompt": prompt_entry["prompt"][:60],
                    "expected": list(expected),
                    "detected": list(detected),
                })

        accuracy = hits / len(candidates)
        assert accuracy > 0.90, (
            f"Classification accuracy {accuracy:.1%} below 90% threshold.\n"
            f"Misses ({len(misses)}):\n"
            + "\n".join(f"  {m['id']}: expected {m['expected']}, got {m['detected']}" for m in misses)
        )

    def test_single_phase_prompts_dont_inflate_complexity(self, benchmark_prompts):
        """Single-phase prompts should not produce full-sdlc complexity."""
        single_phase = [p for p in benchmark_prompts if p["category"] == "single-phase"]
        failures = []
        for prompt_entry in single_phase:
            data = plan(prompt_entry["prompt"])
            # Allow multi-phase due to dep expansion, but not full-sdlc
            if data["complexity"] == "full-sdlc":
                failures.append(prompt_entry["id"])
        assert not failures, f"Single-phase prompts classified as full-sdlc: {failures}"


# ---------------------------------------------------------------------------
# Validate: success paths
# ---------------------------------------------------------------------------

class TestValidationSuccessPaths:
    def test_complete_single_phase_packet(self):
        packet = make_packet(
            phase_status={"architecture": "complete"},
            current_phase="architecture",
            quality_gate_status=[],
            next_action={"description": "Done.", "skill": "system-architecture"},
        )
        result, code = validate(packet)
        assert result["valid"] and code == 0

    def test_sequential_phases_all_complete(self):
        packet = make_packet(
            phase_status={
                "architecture": "complete",
                "backend": "complete",
                "security": "complete",
                "qa": "complete",
                "release": "in_progress",
            },
            current_phase="release",
            quality_gate_status=[
                {"gate_name": "architecture-approved", "status": "PASS",
                 "transition": "architecture → backend"},
                {"gate_name": "backend-implementation-ready", "status": "PASS",
                 "transition": "backend → security"},
                {"gate_name": "security-review-passed", "status": "PASS",
                 "transition": "security → qa"},
                {"gate_name": "test-strategy-accepted", "status": "PASS",
                 "transition": "qa → release"},
            ],
            next_action={"description": "Release.", "skill": "release-management"},
        )
        result, code = validate(packet)
        assert result["valid"] and code == 0

    def test_pass_with_warnings_does_not_block(self):
        packet = make_packet(
            quality_gate_status=[
                {"gate_name": "architecture-approved",
                 "transition": "architecture → backend",
                 "status": "PASS_WITH_WARNINGS"}
            ]
        )
        result, _ = validate(packet)
        assert result["valid"]

    def test_artifacts_complete_for_next_phase(self):
        packet = make_packet(
            artifacts=[{
                "name": "OpenAPI Spec", "type": "spec", "phase": "backend",
                "location": "docs/api.yaml", "status": "complete",
                "consumed_by": ["security"],
            }]
        )
        result, _ = validate(packet, next_phase="security")
        assert result["valid"]


# ---------------------------------------------------------------------------
# Validate: failure paths
# ---------------------------------------------------------------------------

class TestValidationFailurePaths:
    def test_fail_gate_blocks_target_phase(self):
        packet = make_packet(
            quality_gate_status=[
                {"gate_name": "architecture-approved",
                 "transition": "architecture → backend",
                 "status": "FAIL"}
            ]
        )
        result, code = validate(packet)
        assert not result["valid"] and code == 1
        assert any(e["code"] == "GATE_BLOCKING_VIOLATION" for e in result["errors"])

    def test_dependency_violation_detected(self):
        packet = make_packet(
            phase_status={"architecture": "complete", "backend": "pending", "qa": "in_progress"},
            current_phase="qa",
            next_action={"description": "QA.", "skill": "qa-automation"},
        )
        result, code = validate(packet)
        assert not result["valid"] and code == 1
        assert any(e["code"] == "DEPENDENCY_VIOLATION" for e in result["errors"])

    def test_blocking_open_question_fails(self):
        packet = make_packet(
            open_questions=[{
                "id": "OQ-001",
                "question": "Queue technology?",
                "blocks": "backend",
                "owner": "user",
            }]
        )
        result, code = validate(packet, next_phase="backend")
        assert not result["valid"] and code == 1
        assert any(e["code"] == "BLOCKING_OPEN_QUESTION" for e in result["errors"])

    def test_incomplete_artifact_blocks_next_phase(self):
        packet = make_packet(
            artifacts=[{
                "name": "Threat Model", "type": "document", "phase": "security",
                "location": "docs/threat.md", "status": "draft",
                "consumed_by": ["qa"],
            }]
        )
        result, code = validate(packet, next_phase="qa")
        assert not result["valid"] and code == 1
        assert any(e["code"] == "ARTIFACT_NOT_READY" for e in result["errors"])

    def test_missing_required_field_fails(self):
        packet = make_packet()
        del packet["packet_id"]
        result, code = validate(packet)
        assert not result["valid"] and code == 1

    def test_invalid_complexity_fails(self):
        packet = make_packet()
        packet["project"]["complexity"] = "mega-phase"
        result, code = validate(packet)
        assert not result["valid"]

    def test_invalid_phase_status_fails(self):
        packet = make_packet()
        packet["phase_status"]["backend"] = "running"
        result, code = validate(packet)
        assert not result["valid"]

    def test_current_phase_not_in_phase_status_fails(self):
        packet = make_packet(current_phase="observability")
        result, code = validate(packet)
        assert not result["valid"]
        assert any(e["code"] == "PHASE_MISMATCH" for e in result["errors"])

    def test_multiple_errors_all_reported(self):
        """All failures must be surfaced, not just the first one."""
        packet = make_packet(current_phase="observability")  # PHASE_MISMATCH
        del packet["packet_id"]                               # MISSING_FIELD
        result, _ = validate(packet)
        assert len(result["errors"]) >= 2


# ---------------------------------------------------------------------------
# Route: regression invariants
# ---------------------------------------------------------------------------

class TestRouteRegressionInvariants:
    """Key ordering invariants that must hold across code changes."""

    ORDERING_CASES = [
        (["backend-engineering"], "system-architecture", "backend-engineering"),
        (["qa-automation"], "backend-engineering", "qa-automation"),
        (["release-management"], "qa-automation", "release-management"),
        (["release-management"], "devsecops", "release-management"),
        (["observability"], "release-management", "observability"),
        (["sre-incident-response"], "observability", "sre-incident-response"),
        (["compliance-governance"], "devsecops", "compliance-governance"),
        (["compliance-governance"], "qa-automation", "compliance-governance"),
        (["frontend-engineering"], "backend-engineering", "frontend-engineering"),
        (["ai-engineering"], "system-architecture", "ai-engineering"),
    ]

    @pytest.mark.parametrize("skills,upstream,downstream", ORDERING_CASES)
    def test_dependency_order(self, skills, upstream, downstream):
        data = route(skills)
        names = [s["skill"] for s in data["skill_chain"]]
        assert upstream in names, f"{upstream} missing from chain {names}"
        assert downstream in names, f"{downstream} missing from chain {names}"
        assert names.index(upstream) < names.index(downstream), (
            f"Expected {upstream} before {downstream}, got {names}"
        )

    def test_full_sdlc_produces_all_thirteen_skills(self):
        out, code = run(ROUTE_SCRIPT, args=["--full-sdlc"])
        data = json.loads(out)
        assert len(data["skill_chain"]) == 13

    def test_no_duplicates_in_any_chain(self):
        for skills in [
            ["backend-engineering", "qa-automation", "release-management"],
            ["ai-engineering", "devsecops", "compliance-governance"],
            ["frontend-engineering", "code-review"],
        ]:
            data = route(skills)
            names = [s["skill"] for s in data["skill_chain"]]
            assert len(names) == len(set(names)), f"Duplicates in chain: {names}"

    def test_unknown_skill_never_appears_in_chain(self):
        data = route(["not-a-skill", "backend-engineering"])
        names = [s["skill"] for s in data["skill_chain"]]
        assert "not-a-skill" not in names