from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
REPORTS_DIR = ROOT / "reports"
WORKFLOW_EXAMPLES_DIR = ROOT / "workflows" / "examples"
SCHEDULES_REGISTRY = ROOT / "schedules" / "registry.yaml"

PLANNER_SCRIPT_MAP: dict[str, Path] = {
    "business": ROOT / "scripts" / "orchestration" / "plan_business_workflow.py",
    "finance": ROOT / "scripts" / "orchestration" / "plan_finance_workflow.py",
    "gtm": ROOT / "scripts" / "orchestration" / "plan_gtm_workflow.py",
    "inventory": ROOT / "scripts" / "orchestration" / "plan_inventory_workflow.py",
    "legal": ROOT / "scripts" / "orchestration" / "plan_legal_workflow.py",
    "data-security": ROOT / "scripts" / "orchestration" / "plan_data_security_workflow.py",
    "customer": ROOT / "scripts" / "orchestration" / "plan_customer_workflow.py",
}


@dataclass
class ObjectivePlanResponse:
    planner: str
    objective: str
    ok: bool
    plan: dict[str, Any] | None = None
    stderr: str | None = None
    command: list[str] | None = None


def submit_objective(objective: str, planner: str) -> ObjectivePlanResponse:
    if planner not in PLANNER_SCRIPT_MAP:
        return ObjectivePlanResponse(planner=planner, objective=objective, ok=False, stderr="Unknown planner")

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=True) as tf:
        cmd = [
            "python",
            str(PLANNER_SCRIPT_MAP[planner]),
            "--objective",
            objective,
            "--dry-run",
            "--json",
            "--output",
            tf.name,
        ]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
        if proc.returncode != 0:
            return ObjectivePlanResponse(planner=planner, objective=objective, ok=False, stderr=proc.stderr, command=cmd)
        tf.seek(0)
        payload = json.load(tf)
        return ObjectivePlanResponse(planner=planner, objective=objective, ok=True, plan=payload, command=cmd)


def read_json_report(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "missing", "path": str(path.relative_to(ROOT))}
    return json.loads(path.read_text(encoding="utf-8"))


def get_app_health() -> dict[str, Any]:
    return read_json_report(REPORTS_DIR / "runtime_diagnostics.json")


def get_cost_status() -> dict[str, Any]:
    return read_json_report(REPORTS_DIR / "cost_dashboard.json")


def get_rate_limit_status() -> dict[str, Any]:
    return read_json_report(REPORTS_DIR / "rate_limit_report.json")


def get_schedule_registry() -> str:
    if not SCHEDULES_REGISTRY.exists():
        return "missing schedules/registry.yaml"
    return SCHEDULES_REGISTRY.read_text(encoding="utf-8")


def list_oldfarmtrucks_templates() -> list[str]:
    return sorted(p.name for p in WORKFLOW_EXAMPLES_DIR.glob("oldfarmtrucks-*.json"))


def load_oldfarmtrucks_template(template_name: str) -> dict[str, Any]:
    template_path = WORKFLOW_EXAMPLES_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(template_name)
    return json.loads(template_path.read_text(encoding="utf-8"))
