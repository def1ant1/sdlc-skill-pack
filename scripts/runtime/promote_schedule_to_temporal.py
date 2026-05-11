#!/usr/bin/env python3
"""Promote due schedules into deterministic Temporal submission payloads."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
from pathlib import Path
from typing import Any

from scripts.scheduling.preview_schedule import REGISTRY_PATH, _parse_iso, compute_due_runs, load_registry

PROMOTION_DIR = Path(__file__).resolve().parents[2] / "runtime" / "temporal_promotions"
REQUIRED_SCHEDULE_FIELDS = ("schedule_id", "planner_target", "owner", "risk_tier")
REQUIRED_PLAN_FIELDS = ("plan_id", "objective", "planner", "planning_contract", "skill_chain")


def _validate_schedule(schedule: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_SCHEDULE_FIELDS:
        if not schedule.get(field):
            errors.append(f"schedule '{schedule.get('schedule_id', '<unknown>')}' missing required field '{field}'")
    if schedule.get("mode") == "interval" and not schedule.get("interval_minutes"):
        errors.append(f"schedule '{schedule.get('schedule_id')}' interval mode missing interval_minutes")
    if schedule.get("mode") == "cron" and not schedule.get("cron"):
        errors.append(f"schedule '{schedule.get('schedule_id')}' cron mode missing cron")
    return errors


def _validate_workflow_plan_contract(plan: dict[str, Any], schedule: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_PLAN_FIELDS:
        if not plan.get(field):
            errors.append(f"workflow plan missing required field '{field}'")

    contract = plan.get("planning_contract") or {}
    if not isinstance(contract, dict) or contract.get("schema") != "workflow-plan@1.0":
        errors.append("workflow plan planning_contract.schema must equal 'workflow-plan@1.0'")

    if not isinstance(plan.get("skill_chain", []), list) or not plan.get("skill_chain"):
        errors.append("workflow plan skill_chain must be a non-empty list")

    planner_target = str(schedule.get("planner_target", ""))
    planner_name = str(plan.get("planner", ""))
    if planner_target and planner_name and planner_name.split("-")[0] not in planner_target:
        errors.append(
            f"workflow planner '{planner_name}' does not align with schedule planner_target '{planner_target}'"
        )

    return errors


def build_promotion_payload(schedule: dict[str, Any], run_at: dt.datetime, as_of: dt.datetime, workflow_plan: dict[str, Any]) -> dict[str, Any]:
    metadata = copy.deepcopy(schedule.get("metadata", {}))
    return {
        "schedule_id": schedule["schedule_id"],
        "run_at": run_at.isoformat(),
        "promoted_at": as_of.isoformat(),
        "target": {
            "temporal_namespace": "apotheon-dev",
            "task_queue": "apotheon-sdlc",
            "entrypoint": schedule["planner_target"],
        },
        "metadata": {
            "owner": schedule["owner"],
            "risk_tier": schedule["risk_tier"],
            "governance_tags": metadata.get("governance_tags", []),
            "lineage_ids": metadata.get("lineage_ids", []),
            "description": metadata.get("description"),
        },
        "workflow_plan": workflow_plan,
    }


def promote_due_schedules(
    as_of: dt.datetime,
    registry_path: Path,
    workflow_plan_path: Path,
    promotion_dir: Path,
    *,
    lookback_minutes: int = 60,
    dry_run: bool = False,
) -> dict[str, Any]:
    workflow_plan = json.loads(workflow_plan_path.read_text(encoding="utf-8"))
    promotion_dir.mkdir(parents=True, exist_ok=True)

    promoted: list[dict[str, Any]] = []
    validation_errors: list[str] = []

    for schedule in load_registry(registry_path):
        if not schedule.get("enabled", False):
            continue

        validation_errors.extend(_validate_schedule(schedule))
        validation_errors.extend(_validate_workflow_plan_contract(workflow_plan, schedule))
        if validation_errors:
            continue

        for run_at in compute_due_runs(schedule, as_of, lookback_minutes=lookback_minutes):
            payload = build_promotion_payload(schedule, run_at, as_of, workflow_plan)
            dest = promotion_dir / schedule["schedule_id"] / f"{run_at.strftime('%Y%m%dT%H%M%SZ')}.json"
            if dry_run:
                promoted.append({"schedule_id": schedule["schedule_id"], "run_at": run_at.isoformat(), "status": "dry_run", "payload": payload})
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".tmp")
            tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            tmp.replace(dest)
            promoted.append({"schedule_id": schedule["schedule_id"], "run_at": run_at.isoformat(), "status": "promoted", "payload_path": str(dest)})

    return {"as_of": as_of.isoformat(), "dry_run": dry_run, "promotions": promoted, "validation_errors": validation_errors, "valid": not validation_errors}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--workflow-plan", type=Path, required=True)
    parser.add_argument("--promotion-dir", type=Path, default=PROMOTION_DIR)
    parser.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).isoformat())
    parser.add_argument("--lookback-minutes", type=int, default=60)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    result = promote_due_schedules(
        _parse_iso(args.as_of),
        args.registry,
        args.workflow_plan,
        args.promotion_dir,
        lookback_minutes=args.lookback_minutes,
        dry_run=args.dry_run,
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["validation_errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
