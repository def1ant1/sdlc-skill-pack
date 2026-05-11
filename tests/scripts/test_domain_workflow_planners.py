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
    "legal": REPO_ROOT / "scripts" / "orchestration" / "plan_legal_workflow.py",
    "data-security": REPO_ROOT / "scripts" / "orchestration" / "plan_data_security_workflow.py",
}
VALIDATOR = REPO_ROOT / "scripts" / "validation" / "validate_workflow_plan.py"


def run_planner(script: Path, objective: str, output_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), objective, "--dry-run", "--json", "--output", str(output_path)],
        capture_output=True,
        text=True,
    )


@pytest.fixture(scope="module", autouse=True)
def build_reports() -> None:
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "generate_skill_inventory.py"), "--root", str(REPO_ROOT)], check=True)
    subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "skills" / "build_skill_graph.py")], check=True)


@pytest.mark.parametrize("domain", list(PLANNERS.keys()))
def test_planners_emit_schema_valid_plans(tmp_path: Path, domain: str):
    plan_file = tmp_path / f"{domain}.json"
    out = run_planner(PLANNERS[domain], f"Plan {domain} operations", plan_file)
    assert out.returncode == 0, out.stderr
    emitted = json.loads(out.stdout)
    assert emitted["dry_run_safety"]["enabled"] is True
    validate = subprocess.run([sys.executable, str(VALIDATOR), str(plan_file)], cwd=REPO_ROOT, capture_output=True, text=True)
    assert validate.returncode == 0, validate.stdout + validate.stderr


def test_missing_skill_diagnostics(tmp_path: Path):
    inv = tmp_path / "skill_inventory.json"
    graph = tmp_path / "skill_graph.json"
    inv.write_text("[]\n", encoding="utf-8")
    graph.write_text('{"nodes": []}\n', encoding="utf-8")
    out_file = tmp_path / "out.json"
    proc = subprocess.run(
        [
            sys.executable,
            str(PLANNERS["business"]),
            "Plan budget",
            "--dry-run",
            "--json",
            "--output",
            str(out_file),
            "--inventory",
            str(inv),
            "--graph",
            str(graph),
        ],
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    err = proc.stderr.lower()
    assert "required skills unavailable" in err
    assert "missing_in_inventory" in err
    assert "missing_in_graph" in err
