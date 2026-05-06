"""
Tests for scripts/orchestration/validate_workflow_state.py

Covers: required fields, phase dependency order, gate blocking,
open question blocking, artifact readiness, and valid transitions.
"""
import json
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

SCRIPT = Path(__file__).parent.parent.parent / "scripts" / "orchestration" / "validate_workflow_state.py"


def _run(packet: dict, next_phase: str | None = None) -> tuple[dict, int]:
    cmd = [sys.executable, str(SCRIPT)]
    if next_phase:
        cmd += ["--next-phase", next_phase]
    result = subprocess.run(
        cmd,
        input=json.dumps(packet),
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout), result.returncode


# ---------------------------------------------------------------------------
# Minimal valid packet fixture
# ---------------------------------------------------------------------------

VALID_PACKET = {
    "packet_id": "MP-20260506-001",
    "version": "1.0",
    "created_at": "2026-05-06T09:00:00Z",
    "updated_at": "2026-05-06T12:00:00Z",
    "project": {
        "name": "Test Project",
        "objective": "Build a REST API",
        "complexity": "multi-phase",
    },
    "phase_status": {
        "architecture": "complete",
        "backend": "in_progress",
    },
    "current_phase": "backend",
    "decisions": {"accepted": [], "rejected": [], "pending": []},
    "constraints": {},
    "artifacts": [],
    "quality_gate_status": [
        {"gate_name": "architecture-approved", "transition": "architecture → backend", "status": "PASS"}
    ],
    "open_questions": [],
    "next_action": {
        "description": "Complete backend implementation.",
        "skill": "backend-engineering",
    },
}


# ---------------------------------------------------------------------------
# Happy path
# ---------------------------------------------------------------------------

class TestValidPacket:
    def test_valid_packet_returns_valid_true(self):
        result, code = _run(VALID_PACKET)
        assert result["valid"] is True
        assert code == 0

    def test_valid_packet_no_errors(self):
        result, _ = _run(VALID_PACKET)
        assert result["errors"] == []

    def test_valid_packet_all_checks_pass(self):
        result, _ = _run(VALID_PACKET)
        for check in result["checks"]:
            assert check["passed"], f"Check '{check['check']}' unexpectedly failed"

    def test_exit_code_zero_on_valid(self):
        _, code = _run(VALID_PACKET)
        assert code == 0


# ---------------------------------------------------------------------------
# Required field validation
# ---------------------------------------------------------------------------

class TestRequiredFields:
    def test_missing_packet_id(self):
        p = deepcopy(VALID_PACKET)
        del p["packet_id"]
        result, code = _run(p)
        assert not result["valid"]
        assert code == 1
        codes = [e["code"] for e in result["errors"]]
        assert "MISSING_FIELD" in codes or "EMPTY_FIELD" in codes

    def test_missing_objective(self):
        p = deepcopy(VALID_PACKET)
        p["project"]["objective"] = ""
        result, _ = _run(p)
        assert not result["valid"]

    def test_missing_current_phase(self):
        p = deepcopy(VALID_PACKET)
        del p["current_phase"]
        result, _ = _run(p)
        assert not result["valid"]

    def test_missing_next_action_skill(self):
        p = deepcopy(VALID_PACKET)
        del p["next_action"]["skill"]
        result, _ = _run(p)
        assert not result["valid"]

    def test_invalid_complexity_value(self):
        p = deepcopy(VALID_PACKET)
        p["project"]["complexity"] = "giant-sdlc"
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "INVALID_VALUE" in codes

    def test_invalid_phase_status_value(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"]["backend"] = "working"
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "INVALID_STATUS" in codes

    def test_current_phase_not_in_phase_status(self):
        p = deepcopy(VALID_PACKET)
        p["current_phase"] = "observability"  # not in phase_status
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "PHASE_MISMATCH" in codes

    def test_invalid_gate_status_value(self):
        p = deepcopy(VALID_PACKET)
        p["quality_gate_status"][0]["status"] = "MAYBE"
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "INVALID_GATE_STATUS" in codes


# ---------------------------------------------------------------------------
# Phase dependency order
# ---------------------------------------------------------------------------

class TestPhaseDependencyOrder:
    def test_downstream_active_before_upstream_complete(self):
        p = deepcopy(VALID_PACKET)
        # qa depends on backend; mark qa in_progress while backend is still pending
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "pending",
            "qa": "in_progress",
        }
        p["current_phase"] = "qa"
        result, code = _run(p)
        assert not result["valid"]
        assert code == 1
        codes = [e["code"] for e in result["errors"]]
        assert "DEPENDENCY_VIOLATION" in codes

    def test_frontend_active_before_backend_complete(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "in_progress",
            "frontend": "in_progress",
        }
        p["current_phase"] = "frontend"
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "DEPENDENCY_VIOLATION" in codes

    def test_release_active_before_qa_complete(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "complete",
            "security": "complete",
            "qa": "in_progress",
            "release": "in_progress",
        }
        p["current_phase"] = "release"
        result, _ = _run(p)
        assert not result["valid"]

    def test_valid_downstream_when_upstream_complete(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "complete",
            "security": "complete",
            "qa": "complete",
            "release": "in_progress",
        }
        p["current_phase"] = "release"
        p["quality_gate_status"] = [
            {"gate_name": "architecture-approved", "status": "PASS", "transition": "architecture → backend"},
            {"gate_name": "backend-implementation-ready", "status": "PASS", "transition": "backend → security"},
            {"gate_name": "security-review-passed", "status": "PASS", "transition": "security → qa"},
            {"gate_name": "test-strategy-accepted", "status": "PASS", "transition": "qa → release"},
        ]
        result, code = _run(p)
        assert result["valid"]
        assert code == 0


# ---------------------------------------------------------------------------
# Gate blocking
# ---------------------------------------------------------------------------

class TestGateBlocking:
    def test_phase_active_past_failed_gate(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "in_progress",
        }
        p["current_phase"] = "backend"
        # architecture-approved FAIL should block backend
        p["quality_gate_status"] = [
            {"gate_name": "architecture-approved", "status": "FAIL", "transition": "architecture → backend"}
        ]
        result, code = _run(p)
        assert not result["valid"]
        assert code == 1
        codes = [e["code"] for e in result["errors"]]
        assert "GATE_BLOCKING_VIOLATION" in codes

    def test_security_review_fail_blocks_qa(self):
        p = deepcopy(VALID_PACKET)
        p["phase_status"] = {
            "architecture": "complete",
            "backend": "complete",
            "security": "complete",
            "qa": "in_progress",
        }
        p["current_phase"] = "qa"
        p["quality_gate_status"] = [
            {"gate_name": "security-review-passed", "status": "FAIL", "transition": "security → qa"}
        ]
        result, _ = _run(p)
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "GATE_BLOCKING_VIOLATION" in codes

    def test_pass_with_warnings_does_not_block(self):
        p = deepcopy(VALID_PACKET)
        p["quality_gate_status"] = [
            {"gate_name": "architecture-approved", "status": "PASS_WITH_WARNINGS",
             "transition": "architecture → backend"}
        ]
        result, code = _run(p)
        assert result["valid"]
        assert code == 0

    def test_not_evaluated_gate_does_not_block_upstream_phase(self):
        # NOT_EVALUATED only matters for the target phase; upstream phase can still be complete
        p = deepcopy(VALID_PACKET)
        p["quality_gate_status"] = [
            {"gate_name": "architecture-approved", "status": "NOT_EVALUATED",
             "transition": "architecture → backend"}
        ]
        result, _ = _run(p)
        # architecture-approved is NOT_EVALUATED but backend is already in_progress
        # This is a violation — the gate must pass before backend starts
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        # Gate blocking only triggers on FAIL, not NOT_EVALUATED
        # But the packet itself is valid structure-wise; no gate blocking violation here
        assert "GATE_BLOCKING_VIOLATION" not in codes


# ---------------------------------------------------------------------------
# Open questions
# ---------------------------------------------------------------------------

class TestOpenQuestions:
    def test_blocking_open_question_on_current_phase(self):
        p = deepcopy(VALID_PACKET)
        p["open_questions"] = [
            {"id": "OQ-001", "question": "Queue tech?", "blocks": "backend", "owner": "user"}
        ]
        result, code = _run(p, next_phase="backend")
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "BLOCKING_OPEN_QUESTION" in codes

    def test_non_blocking_open_question_does_not_fail(self):
        p = deepcopy(VALID_PACKET)
        p["open_questions"] = [
            {"id": "OQ-001", "question": "Future concern?", "blocks": "observability", "owner": "user"}
        ]
        # Not blocking the current phase (backend) or next_phase if none given
        result, code = _run(p)
        assert result["valid"]

    def test_empty_open_questions_passes(self):
        p = deepcopy(VALID_PACKET)
        p["open_questions"] = []
        result, _ = _run(p)
        assert result["valid"]


# ---------------------------------------------------------------------------
# Artifact readiness
# ---------------------------------------------------------------------------

class TestArtifactReadiness:
    def test_incomplete_artifact_blocks_next_phase(self):
        p = deepcopy(VALID_PACKET)
        p["artifacts"] = [
            {
                "name": "OpenAPI Spec",
                "type": "spec",
                "phase": "backend",
                "location": "docs/api/openapi.yaml",
                "status": "draft",
                "consumed_by": ["security"],
            }
        ]
        result, code = _run(p, next_phase="security")
        assert not result["valid"]
        codes = [e["code"] for e in result["errors"]]
        assert "ARTIFACT_NOT_READY" in codes

    def test_complete_artifact_passes_check(self):
        p = deepcopy(VALID_PACKET)
        p["artifacts"] = [
            {
                "name": "OpenAPI Spec",
                "type": "spec",
                "phase": "backend",
                "location": "docs/api/openapi.yaml",
                "status": "complete",
                "consumed_by": ["security"],
            }
        ]
        result, _ = _run(p, next_phase="security")
        assert result["valid"]

    def test_artifact_for_different_phase_not_checked(self):
        p = deepcopy(VALID_PACKET)
        p["artifacts"] = [
            {
                "name": "Threat Model",
                "type": "document",
                "phase": "security",
                "location": "docs/security/threat-model.md",
                "status": "draft",
                "consumed_by": ["qa"],  # only needed for qa, not security
            }
        ]
        # next_phase is security — threat model consumed_by qa, not security
        result, _ = _run(p, next_phase="security")
        assert result["valid"]