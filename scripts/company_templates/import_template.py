#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_TEMPLATE = ROOT / "company_templates" / "oldfarmtrucks" / "template.json"
SCHEMA = ROOT / "schemas" / "company-template.schema.json"
DEFAULT_OUTPUT = ROOT / "reports" / "company_templates" / "oldfarmtrucks-import.json"


def _validate_schema(payload: dict[str, Any]) -> None:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema  # type: ignore

        jsonschema.validate(payload, schema)
    except ModuleNotFoundError:
        required = schema.get("required", [])
        missing = [k for k in required if k not in payload]
        if missing:
            raise ValueError(f"Template missing required keys: {missing}")


def _run_dry(plan_path: str) -> dict[str, Any]:
    cmd = [
        "python",
        "scripts/runtime/execute_workflow.py",
        "--plan",
        plan_path,
        "--dry-run",
    ]
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    body: dict[str, Any] = {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "stderr": proc.stderr.strip(),
    }
    if proc.stdout.strip():
        try:
            body["result"] = json.loads(proc.stdout)
        except json.JSONDecodeError:
            body["stdout"] = proc.stdout.strip()
    return body


def main() -> int:
    ap = argparse.ArgumentParser(description="Import a company template into local reports for provisioning preview.")
    ap.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    ap.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--validate-workflows", action="store_true", help="Run dry-run validation for short-term and long-term workflows.")
    args = ap.parse_args()

    payload = json.loads(args.template.read_text(encoding="utf-8"))
    _validate_schema(payload)

    report: dict[str, Any] = {
        "template_id": payload["template_id"],
        "template_path": str(args.template.relative_to(ROOT)),
        "provisioned": {
            "workflows": payload["workflows"],
            "schedules": payload["schedules"],
            "dashboards": payload["dashboards"],
            "connectors": payload["connectors"],
            "approvals": payload["approvals"],
            "budgets": payload["budgets"],
            "sample_data": payload["sample_data"],
        },
        "mode": "dry-run" if args.dry_run else "apply",
    }

    if args.validate_workflows:
        report["workflow_validation"] = {
            "short_term": _run_dry(payload["workflows"]["short_term"][0]["plan_path"]),
            "long_term": _run_dry(payload["workflows"]["long_term"][0]["plan_path"]),
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": True, "output": str(args.output.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
