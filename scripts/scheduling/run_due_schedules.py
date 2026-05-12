#!/usr/bin/env python3
"""Run due schedules and persist run artifacts."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any

from scripts.runtime.error_envelope import build_error_envelope

from scripts.scheduling.preview_schedule import REGISTRY_PATH, _parse_iso, compute_due_runs, load_registry
from scripts.scheduling.task_scheduler_runtime import create_task_from_schedule_run

HISTORY_DIR = Path(__file__).resolve().parents[2] / "runtime" / "schedule_history"


def _stable_run_id(schedule_id: str, run_at: dt.datetime) -> str:
    raw = f"{schedule_id}:{run_at.isoformat()}".encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _artifact_path(schedule_id: str, run_id: str, history_dir: Path) -> Path:
    return history_dir / schedule_id / f"{run_id}.json"


def _validate_schedule_artifact(payload: dict[str, Any]) -> None:
    required = ("run_id", "schedule_id", "run_at", "executed_at", "status")
    for field in required:
        if not payload.get(field):
            envelope = build_error_envelope(correlation_id=payload.get("run_id", "corr-schedule"), workflow_run_id="n/a", schedule_run_id=payload.get("run_id", "n/a"), skill="scheduler", step="artifact_validation", category="schedule", retryable=False, user_action_required=True, message="Schedule artifact validation failed.", technical_detail=f"schedule artifact missing {field}", root_cause_hint="Internal scheduler payload bug", remediation="Regenerate schedule run artifact with all required fields.", source_exception="ValueError")
            raise ValueError(json.dumps(envelope, sort_keys=True))



def execute_due(as_of: dt.datetime, registry_path: Path, history_dir: Path, lookback_minutes: int = 60, task_dir: Path | None = None) -> dict[str, Any]:
    history_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    for schedule in load_registry(registry_path):
        if not schedule.get("enabled", False):
            continue
        for run_at in compute_due_runs(schedule, as_of, lookback_minutes=lookback_minutes):
            run_id = _stable_run_id(schedule["schedule_id"], run_at)
            artifact = _artifact_path(schedule["schedule_id"], run_id, history_dir)
            artifact.parent.mkdir(parents=True, exist_ok=True)
            if artifact.exists():
                status = "skipped_existing"
            else:
                payload = {
                    "run_id": run_id,
                    "schedule_id": schedule["schedule_id"],
                    "planner_target": schedule["planner_target"],
                    "owner": schedule["owner"],
                    "risk_tier": schedule["risk_tier"],
                    "run_at": run_at.isoformat(),
                    "executed_at": as_of.isoformat(),
                    "status": "completed"
                }
                _validate_schedule_artifact(payload)
                artifact.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
                status = "executed"
            result={"schedule_id": schedule["schedule_id"], "run_id": run_id, "run_at": run_at.isoformat(), "status": status}
            if status=="executed" and task_dir is not None:
                task_path=create_task_from_schedule_run({"schedule_id":schedule["schedule_id"],"run_id":run_id}, schedule, task_dir)
                if task_path is not None:
                    result["generated_task"]=str(task_path)
            results.append(result)
    return {"as_of": as_of.isoformat(), "runs": results}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=REGISTRY_PATH)
    parser.add_argument("--history-dir", type=Path, default=HISTORY_DIR)
    parser.add_argument("--as-of", default=dt.datetime.now(dt.timezone.utc).isoformat())
    parser.add_argument("--lookback-minutes", type=int, default=60)
    parser.add_argument("--task-dir", type=Path, default=Path("runtime/tasks"))
    args = parser.parse_args()

    as_of = _parse_iso(args.as_of)
    report = execute_due(as_of, args.registry, args.history_dir, args.lookback_minutes, args.task_dir)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
