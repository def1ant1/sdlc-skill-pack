#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_HISTORY = ROOT / "runtime" / "workflow_history"
SCHEDULE_HISTORY = ROOT / "runtime" / "schedule_history"
OUT_PATH = ROOT / "reports" / "local_ops_report.json"

RATE_PER_1K_TOKENS_USD = 0.003


def _load_json_files(root: Path) -> list[dict[str, Any]]:
    if not root.exists():
        return []
    records: list[dict[str, Any]] = []
    for p in sorted(root.rglob("*.json")):
        records.append(json.loads(p.read_text(encoding="utf-8")))
    return records


def _validate_run_artifact(rec: dict[str, Any], kind: str) -> list[str]:
    errs: list[str] = []
    for field in ("run_id",):
        if not rec.get(field):
            errs.append(f"{kind}: missing {field}")
    ts_field = "started_at" if kind == "workflow" else "executed_at"
    if not rec.get(ts_field):
        errs.append(f"{kind}: missing {ts_field}")
    return errs


def _token_cost_estimates(workflows: list[dict[str, Any]]) -> dict[str, Any]:
    total_tokens = 0
    for w in workflows:
        for step in w.get("steps", []):
            total_tokens += int(step.get("tokens_used", 0) or 0)
    return {
        "assumed_rate_usd_per_1k_tokens": RATE_PER_1K_TOKENS_USD,
        "total_tokens_estimated": total_tokens,
        "estimated_cost_usd": round((total_tokens / 1000) * RATE_PER_1K_TOKENS_USD, 6),
    }


def generate_report(workflow_history: Path, schedule_history: Path) -> dict[str, Any]:
    workflows = _load_json_files(workflow_history)
    schedules = _load_json_files(schedule_history)

    consistency_errors: list[str] = []
    for w in workflows:
        consistency_errors.extend(_validate_run_artifact(w, "workflow"))
    for s in schedules:
        consistency_errors.extend(_validate_run_artifact(s, "schedule"))

    pending = [
        {
            "run_id": w.get("run_id"),
            "step": step.get("step"),
            "skill": step.get("skill"),
        }
        for w in workflows
        for step in w.get("steps", [])
        if step.get("status") == "pending_hitl"
    ]

    return {
        "workflow_run_history": workflows,
        "schedule_history": schedules,
        "pending_governance_approvals": pending,
        "token_cost_estimates": _token_cost_estimates(workflows),
        "consistency_checks": {
            "passed": len(consistency_errors) == 0,
            "errors": consistency_errors,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow-history", type=Path, default=WORKFLOW_HISTORY)
    parser.add_argument("--schedule-history", type=Path, default=SCHEDULE_HISTORY)
    parser.add_argument("--output", type=Path, default=OUT_PATH)
    args = parser.parse_args()

    report = generate_report(args.workflow_history, args.schedule_history)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
