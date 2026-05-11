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
    for key in ["plan_id", "created", "planner", "planning_contract", "skill_chain", "governance_checks", "hitl_checkpoints", "next_action"]:
        assert key in out
    assert out["planner"] == f"{domain}-workflow-planner"
    assert out["planning_contract"]["schema"] == "workflow-plan@1.0"
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


@pytest.mark.parametrize("domain", ["business", "finance", "customer", "inventory"])
def test_output_structure_is_deterministic(domain: str):
    objective = "Improve compliance posture and vendor governance"
    first = run_planner(PLANNERS[domain], objective)
    second = run_planner(PLANNERS[domain], objective)

    assert list(first.keys()) == list(second.keys())
    assert first["planner"] == second["planner"]
    assert first["objective"] == second["objective"]
    assert first["planning_contract"] == second["planning_contract"]
    assert first["governance_checks"] == second["governance_checks"]
    assert first["hitl_checkpoints"] == second["hitl_checkpoints"]
    assert first["next_action"] == second["next_action"]

    first_chain_shape = [{k: step[k] for k in ("step", "skill", "phase", "depends_on", "governance")} for step in first["skill_chain"]]
    second_chain_shape = [{k: step[k] for k in ("step", "skill", "phase", "depends_on", "governance")} for step in second["skill_chain"]]
    assert first_chain_shape == second_chain_shape


@pytest.mark.parametrize("domain", ["business", "finance", "customer", "inventory"])
def test_governance_annotations_present(domain: str):
    out = run_planner(PLANNERS[domain], "Review contracts, budget controls, and workforce policy")

    approval_steps = []
    for step in out["skill_chain"]:
        gov = step["governance"]
        assert set(gov.keys()) == {"approval_required", "approver_role", "policy_tags", "reason"}
        assert isinstance(gov["approval_required"], bool)
        assert isinstance(gov["policy_tags"], list)
        if gov["approval_required"]:
            assert isinstance(gov["approver_role"], str)
            assert gov["approver_role"]
            assert len(gov["policy_tags"]) > 0
            approval_steps.append(step["skill"])

    assert approval_steps, "Expected at least one approval-requiring step in governance-heavy objectives"
