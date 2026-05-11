from __future__ import annotations

import os
import sys
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "runtime"))

from skill_activity import load_skill_contract, detect_hitl  # noqa: E402


def test_missing_skill_contract_isolated_failure():
    with mock.patch.dict(os.environ, {}, clear=False):
        try:
            load_skill_contract("definitely-missing-skill")
            assert False
        except FileNotFoundError as exc:
            assert "SKILL.md not found" in str(exc)


def test_malformed_model_output_does_not_false_positive_hitl():
    malformed = "<!-- HITL_GATE: { required: true bad json } -->"
    needs_hitl, reason = detect_hitl("backend-engineering", malformed)
    assert needs_hitl is False
    assert reason == ""
