#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.runtime.error_envelope import build_error_envelope

SCHEMA_PATH = ROOT / "schemas" / "error-envelope.schema.json"
REQUIRED_BOUNDARY_PREFIXES = ("runtime", "planner", "scheduler", "connector:")


def _validate_schema(schema: dict, envelope: dict) -> list[str]:
    try:
        import jsonschema
    except ImportError:
        return []
    try:
        jsonschema.validate(instance=envelope, schema=schema)
        return []
    except Exception as exc:  # noqa: BLE001
        return [f"schema validation failed: {exc}"]


def _validate(envelope: dict) -> list[str]:
    errs = []
    if not str(envelope.get("remediation", "")).strip():
        errs.append("missing remediation")
    if envelope.get("user_action_required") and "remediation" not in envelope:
        errs.append("user_action_required error missing remediation")
    if envelope.get("skill", "").startswith("connector:") and envelope.get("retryable") and envelope.get("category") in {"auth", "validation", "config"}:
        errs.append("connector auth/validation/config errors must be non-retryable")
    return errs


def main() -> int:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    reps = [
        build_error_envelope(correlation_id="corr-runtime", workflow_run_id="RUN-1", skill="runtime", step=2, category="runtime", message="Runtime failure", remediation="Fix failing step and rerun.", source_exception="RuntimeError"),
        build_error_envelope(correlation_id="corr-planner", workflow_run_id="n/a", skill="planner", step="plan", category="validation", retryable=False, message="Planner objective invalid", remediation="Provide non-empty objective.", source_exception="ValueError"),
        build_error_envelope(correlation_id="corr-scheduler", schedule_run_id="sched-1", skill="scheduler", step="dispatch", category="schedule", retryable=False, message="Schedule misfire", remediation="Adjust schedule misfire policy.", source_exception="RuntimeError"),
        build_error_envelope(correlation_id="corr-connector", workflow_run_id="RUN-2", skill="connector:salesforce", step=3, category="auth", retryable=False, message="Auth failed", remediation="Rotate credentials and retry.", source_exception="HTTPError"),
    ]
    all_errs = []
    for i, envelope in enumerate(reps):
        if not envelope["skill"].startswith(REQUIRED_BOUNDARY_PREFIXES):
            all_errs.append(f"error[{i}] boundary skill missing prefix: {envelope['skill']}")
        for err in _validate_schema(schema, envelope) + _validate(envelope):
            all_errs.append(f"error[{i}] {err}")
    if all_errs:
        print("\n".join(all_errs))
        return 1
    print(json.dumps({"status": "ok", "validated": len(reps), "schema": str(SCHEMA_PATH.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
