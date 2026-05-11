#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.runtime.error_envelope import build_error_envelope

REQUIRED = {"error_id","correlation_id","workflow_run_id","schedule_run_id","skill","step","severity","category","retryable","user_action_required","message","technical_detail","root_cause_hint","remediation","source_exception","created_at"}


def _validate(e: dict) -> list[str]:
    errs = []
    missing = REQUIRED - set(e)
    if missing:
        errs.append(f"missing fields: {sorted(missing)}")
    if not str(e.get("remediation", "")).strip():
        errs.append("missing remediation")
    return errs


def main() -> int:
    reps = [
        build_error_envelope(correlation_id="corr-runtime", workflow_run_id="RUN-1", skill="runtime", step=2, category="runtime", message="Runtime failure", remediation="Fix failing step and rerun.", source_exception="RuntimeError"),
        build_error_envelope(correlation_id="corr-planner", workflow_run_id="n/a", skill="planner", step="plan", category="validation", message="Planner objective invalid", remediation="Provide non-empty objective.", source_exception="ValueError"),
        build_error_envelope(correlation_id="corr-scheduler", schedule_run_id="sched-1", skill="scheduler", step="dispatch", category="schedule", message="Schedule misfire", remediation="Adjust schedule misfire policy.", source_exception="RuntimeError"),
        build_error_envelope(correlation_id="corr-connector", workflow_run_id="RUN-2", skill="connector:salesforce", step=3, category="auth", message="Auth failed", remediation="Rotate credentials and retry.", source_exception="HTTPError"),
    ]
    all_errs = []
    for i, e in enumerate(reps):
        for err in _validate(e):
            all_errs.append(f"error[{i}] {err}")
    if all_errs:
        print("\n".join(all_errs))
        return 1
    print(json.dumps({"status":"ok","validated":len(reps)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
