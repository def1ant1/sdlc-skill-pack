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
