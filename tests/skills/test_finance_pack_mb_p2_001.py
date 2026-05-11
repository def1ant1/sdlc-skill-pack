import json
from pathlib import Path

FINANCE_SKILLS = [
    "accounting-operations",
    "bookkeeping-automation",
    "chart-of-accounts-management",
    "journal-entry-review",
    "month-end-close-support",
    "reconciliation-automation",
    "accounts-payable-automation",
    "accounts-receivable-automation",
    "invoice-processing",
    "collections-prioritization",
    "payment-matching",
    "cash-management",
    "cash-flow-forecasting",
    "budget-planning",
    "budget-variance-analysis",
    "fpa-analysis",
    "financial-scenario-modeling",
    "runway-analysis",
    "revenue-leakage-detection",
    "working-capital-optimization",
    "unit-economics-analysis",
    "financial-control-monitoring",
    "expense-policy-compliance",
]


def test_finance_skill_docs_have_standard_sections() -> None:
    required_markers = [
        "## Canonical finance entities",
        "## Standardized financial output sections",
        "## Approval gates for high-risk actions",
        "## Governance-aware evaluation requirements",
    ]
    for skill in FINANCE_SKILLS:
        text = (Path("skills") / skill / "SKILL.md").read_text(encoding="utf-8")
        for marker in required_markers:
            assert marker in text, f"{skill} missing section: {marker}"


def test_finance_skill_evals_cover_calc_and_governance() -> None:
    for skill in FINANCE_SKILLS:
        eval_path = Path("skills") / skill / "eval.spec.json"
        payload = json.loads(eval_path.read_text(encoding="utf-8"))
        dataset_ids = {dataset["id"] for dataset in payload.get("datasets", [])}
        metric_names = {metric["name"] for metric in payload.get("metrics", [])}

        assert f"{skill}-calc-golden" in dataset_ids
        assert f"{skill}-governance-negative" in dataset_ids
        assert "calculation_correctness_rate" in metric_names
        assert "approval_gate_enforcement_rate" in metric_names


def test_finance_pack_integration_fixtures_exist() -> None:
    fixture_dir = Path("tests/fixtures/finance-pack")
    fixture_names = {
        "forecasting.integration.json",
        "close.integration.json",
        "reconciliation.integration.json",
        "controls.integration.json",
    }
    for fixture_name in fixture_names:
        fixture = json.loads((fixture_dir / fixture_name).read_text(encoding="utf-8"))
        assert "skills" in fixture and fixture["skills"], fixture_name
        assert "assertions" in fixture and fixture["assertions"], fixture_name
