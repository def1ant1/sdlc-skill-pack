from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS = [
    "payroll-audit",
    "tax-planning-support",
    "hr-policy-guidance-support",
    "talent-risk-screening-support",
    "vendor-obligation-tracking",
    "procurement-kpi-optimization-support",
    "legal-intake-triage-support",
    "business-process-optimization",
    "hr-case-management-support",
    "vendor-procurement-risk-support",
    "legal-obligation-management-support",
    "process-optimization-governance-support",
    "entity-resolution",
    "golden-record-management",
    "data-quality-scoring",
]

def _manifest(skill: str) -> dict:
    return json.loads((REPO_ROOT / "skills" / skill / "manifest.v9.json").read_text())

def test_approval_thresholds_present_and_ordered():
    for skill in SKILLS:
        policy = _manifest(skill)["approval_policy"]
        assert policy["mandatory_review_if_gte"] < policy["auto_block_if_gte"]

def test_obligation_tracking_requires_key_fields():
    fields = set(["obligation_id", "owner", "due_date", "status", "evidence_link"])
    for skill in SKILLS:
        tracking = _manifest(skill)["obligation_tracking"]
        assert tracking["required"] is True
        assert fields.issubset(set(tracking["fields"]))

def test_kpi_recommendations_are_baseline_linked():
    for skill in SKILLS:
        kpi = _manifest(skill)["kpi_recommendation_policy"]
        assert kpi["link_to_baseline"] is True
        assert kpi["require_metric_owner"] is True
        assert kpi["forbid_unattributed_targets"] is True


def test_hr_and_legal_bias_safeguards_enabled():
    sensitive = [
        "hr-policy-guidance-support",
        "talent-risk-screening-support",
        "legal-intake-triage-support",
        "hr-case-management-support",
        "legal-obligation-management-support",
    ]
    for skill in sensitive:
        guardrails = _manifest(skill)["bias_guardrails"]
        assert guardrails["enabled"] is True
        assert guardrails["require_human_sensitive_review"] is True


def test_expert_review_boundaries_for_payroll_tax_compliance():
    expected = [
        "payroll-audit",
        "tax-planning-support",
        "legal-obligation-management-support",
    ]
    for skill in expected:
        boundaries = _manifest(skill)["expert_review_boundaries"]
        assert boundaries["required"] is True
        assert len(boundaries["required_reviewers"]) >= 1
        assert "final_determination" in boundaries["prohibited_actions_without_review"]
