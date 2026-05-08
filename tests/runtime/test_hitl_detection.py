"""
Tests for the three-layer HITL gate detection in skill_activity.py.

Covers: structured marker, risk-list, phrase fallback, and their priorities.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_RUNTIME = str(Path(__file__).parent.parent.parent / "scripts" / "runtime")
if _RUNTIME not in sys.path:
    sys.path.insert(0, _RUNTIME)

from skill_activity import detect_hitl  # noqa: E402


class TestStructuredMarker:
    def test_valid_l3_marker_detected(self):
        output = '<!-- HITL_GATE: {"required": true, "level": "L3", "reason": "prod deploy"} -->'
        required, reason = detect_hitl("some-skill", output)
        assert required is True
        assert "prod deploy" in reason
        assert "L3" in reason

    def test_marker_with_false_required_not_triggered(self):
        output = '<!-- HITL_GATE: {"required": false, "level": "L3", "reason": "no block"} -->'
        required, _ = detect_hitl("some-skill", output)
        assert required is False

    def test_marker_embedded_in_longer_output(self):
        output = (
            "Here is my deployment plan.\n\n"
            "Step 1: build image\nStep 2: push to ECR\n\n"
            '<!-- HITL_GATE: {"required": true, "level": "L3", "reason": "ECR push"} -->'
        )
        required, reason = detect_hitl("cloud-deployment", output)
        assert required is True
        assert "ECR push" in reason

    def test_malformed_marker_falls_through_to_risk_list(self):
        # Malformed JSON in marker — should fall through to risk-list check
        output = "<!-- HITL_GATE: {bad json} -->"
        required, reason = detect_hitl("cloud-deployment", output)
        # cloud-deployment is in the risk list, so still True
        assert required is True
        assert "high-risk" in reason.lower() or "cloud-deployment" in reason

    def test_marker_without_required_field_defaults_to_false(self):
        output = '<!-- HITL_GATE: {"level": "L3", "reason": "test"} -->'
        required, _ = detect_hitl("safe-skill", output)
        assert required is False

    def test_marker_case_insensitive(self):
        output = '<!-- hitl_gate: {"required": true, "level": "L2", "reason": "sec review"} -->'
        required, _ = detect_hitl("some-skill", output)
        assert required is True


class TestRiskList:
    def test_cloud_deployment_always_hitl(self):
        required, reason = detect_hitl("cloud-deployment", "All clear, deploying.")
        assert required is True
        assert "cloud-deployment" in reason or "high-risk" in reason.lower()

    def test_release_management_always_hitl(self):
        required, _ = detect_hitl("release-management", "Release notes generated.")
        assert required is True

    def test_devsecops_always_hitl(self):
        required, _ = detect_hitl("devsecops", "Security scan passed.")
        assert required is True

    def test_sre_always_hitl(self):
        required, _ = detect_hitl("sre", "On-call runbook ready.")
        assert required is True

    def test_requirements_analysis_not_hitl_by_default(self):
        required, _ = detect_hitl("requirements-analysis", "Requirements documented.")
        assert required is False

    def test_backend_engineering_not_hitl_by_default(self):
        required, _ = detect_hitl("backend-engineering", "API implementation complete.")
        assert required is False


class TestPhraseFallback:
    def test_requires_approval_phrase(self):
        required, reason = detect_hitl("qa", "This change requires approval before merging.")
        assert required is True
        assert "requires approval" in reason

    def test_human_approval_phrase(self):
        required, reason = detect_hitl("qa", "Human approval is needed for this step.")
        assert required is True
        assert "human approval" in reason

    def test_hitl_gate_phrase(self):
        required, reason = detect_hitl("frontend-engineering", "Triggering hitl gate for this deploy.")
        assert required is True

    def test_level_3_approval_phrase(self):
        required, reason = detect_hitl("code-review", "Level-3 approval required by policy.")
        assert required is True

    def test_clean_output_not_hitl(self):
        required, _ = detect_hitl("frontend-engineering", "Component library updated successfully.")
        assert required is False

    def test_partial_phrase_not_triggered(self):
        # "approval" alone should not trigger — must be "requires approval" or similar phrase
        required, _ = detect_hitl("qa", "The approval workflow is documented here.")
        assert required is False


class TestPriority:
    def test_structured_marker_takes_priority_over_risk_list(self):
        """A skill in the risk list with required=false marker should NOT trigger."""
        output = '<!-- HITL_GATE: {"required": false, "level": "L3", "reason": "safe"} -->'
        # cloud-deployment is in risk list, but valid marker says required=false
        required, _ = detect_hitl("cloud-deployment", output)
        # Marker says false → should not trigger (marker wins over risk list)
        assert required is False

    def test_risk_list_takes_priority_over_clean_phrases(self):
        """Risk-list check fires even when no phrases match."""
        required, reason = detect_hitl("sre", "Runbook created. No special gates needed.")
        assert required is True
        assert "sre" in reason or "high-risk" in reason.lower()

    def test_empty_output_with_risky_skill_still_triggers(self):
        required, _ = detect_hitl("incident-response", "")
        assert required is True

    def test_empty_output_with_safe_skill_does_not_trigger(self):
        required, _ = detect_hitl("ai-engineering", "")
        assert required is False