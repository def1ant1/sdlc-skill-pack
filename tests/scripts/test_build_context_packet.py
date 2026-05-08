"""
Tests for scripts/memory/build_context_packet.py

Validates context packet construction, schema, and field coercion.
"""
from __future__ import annotations

import json
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
BUILDER = REPO_ROOT / "scripts" / "memory" / "build_context_packet.py"


def build(input_json: dict) -> dict:
    result = subprocess.run(
        [sys.executable, str(BUILDER)],
        input=json.dumps(input_json),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"build_context_packet.py failed:\n{result.stderr}"
    return json.loads(result.stdout)


MINIMAL_INPUT = {
    "objective": "Build a REST API",
    "phase": "architecture",
}

FULL_INPUT = {
    "objective": "Deploy to production",
    "phase": "release",
    "decisions": ["Use blue-green deployment", "Enable feature flags"],
    "constraints": ["zero-downtime", "rollback within 5 minutes"],
    "artifacts": ["api-spec.yaml", "terraform.tfplan"],
    "risks": ["database migration may cause latency spike"],
    "next_action": "Run smoke tests",
}


# ---------------------------------------------------------------------------
# Schema tests
# ---------------------------------------------------------------------------

class TestOutputSchema:
    def test_required_fields_present(self):
        out = build(MINIMAL_INPUT)
        for field in ("objective", "phase", "decisions", "constraints", "artifacts", "risks"):
            assert field in out, f"Missing field: {field}"

    def test_objective_preserved(self):
        out = build(MINIMAL_INPUT)
        assert out["objective"] == MINIMAL_INPUT["objective"]

    def test_phase_preserved(self):
        out = build(MINIMAL_INPUT)
        assert out["phase"] == MINIMAL_INPUT["phase"]

    def test_list_fields_default_to_empty_list(self):
        out = build(MINIMAL_INPUT)
        for field in ("decisions", "constraints", "artifacts", "risks"):
            assert isinstance(out[field], list), f"{field} should be a list"

    def test_full_input_preserved(self):
        out = build(FULL_INPUT)
        assert out["decisions"] == FULL_INPUT["decisions"]
        assert out["constraints"] == FULL_INPUT["constraints"]
        assert out["artifacts"] == FULL_INPUT["artifacts"]
        assert out["risks"] == FULL_INPUT["risks"]
        assert out["next_action"] == FULL_INPUT["next_action"]

    def test_output_is_valid_json(self):
        result = subprocess.run(
            [sys.executable, str(BUILDER)],
            input=json.dumps(MINIMAL_INPUT),
            capture_output=True,
            text=True,
        )
        parsed = json.loads(result.stdout)
        assert parsed is not None


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------

class TestEdgeCases:
    def test_empty_objective_handled(self):
        out = build({"objective": "", "phase": "planning"})
        assert "objective" in out

    def test_extra_fields_not_in_output(self):
        out = build({**MINIMAL_INPUT, "unexpected_field": "ignored"})
        assert "unexpected_field" not in out

    def test_missing_phase_defaults(self):
        out = build({"objective": "Test"})
        assert "phase" in out  # Should default gracefully

    def test_invalid_json_input_exits_nonzero(self):
        result = subprocess.run(
            [sys.executable, str(BUILDER)],
            input="this is not json",
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0