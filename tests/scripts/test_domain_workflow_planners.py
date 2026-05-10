"""Tests for business/finance/customer/inventory workflow planners."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
PLANNERS = {
    "business": REPO_ROOT / "scripts" / "orchestration" / "plan_business_workflow.py",
    "finance": REPO_ROOT / "scripts" / "orchestration" / "plan_finance_workflow.py",
    "customer": REPO_ROOT / "scripts" / "orchestration" / "plan_customer_workflow.py",
    "inventory": REPO_ROOT / "scripts" / "orchestration" / "plan_inventory_workflow.py",
}


def run_planner(script: Path, objective: str) -> dict:
    result = subprocess.run([sys.executable, str(script), objective], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


@pytest.mark.parametrize("domain", ["business", "finance", "customer", "inventory"])
def test_output_schema_and_hitl(domain: str):
    out = run_planner(PLANNERS[domain], "Improve customer retention and compliance reporting")
    for key in ["plan_id", "planner", "planning_contract", "skill_chain", "governance_checks", "hitl_checkpoints", "next_action"]:
        assert key in out
    assert out["planner"] == f"{domain}-workflow-planner"
    assert len(out["hitl_checkpoints"]) >= 2
    assert any(c["required"] for c in out["hitl_checkpoints"])


@pytest.mark.parametrize(
    "domain,objective,expected",
    [
        ("finance", "Optimize budget and vendor sourcing", {"finance-operations", "procurement-operations"}),
        ("customer", "Reduce churn and improve onboarding", {"customer-operations"}),
        ("inventory", "Fix warehouse stock replenishment", {"inventory-operations"}),
        ("business", "HR policy refresh and legal contract review", {"hr-operations", "legal-operations"}),
    ],
)
def test_route_objectives(domain: str, objective: str, expected: set[str]):
    out = run_planner(PLANNERS[domain], objective)
    routed = {s["skill"] for s in out["skill_chain"]}
    assert expected.issubset(routed)
