#!/usr/bin/env python3
"""Release smoke test runner for offline/dry-run validation."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


class SmokeFailure(RuntimeError):
    """Raised when a smoke check fails."""


def _run(cmd: list[str], stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        input=stdin,
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )


def _run_json(cmd: list[str], stdin: str | None = None) -> dict:
    result = _run(cmd, stdin)
    if result.returncode != 0:
        raise SmokeFailure(f"Command failed: {' '.join(cmd)}\n{result.stderr.strip()}")
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise SmokeFailure(f"Invalid JSON from {' '.join(cmd)}: {exc}") from exc


def _assert_report_files_exist() -> list[str]:
    expected = [
        REPORTS / "skill_inventory.json",
        REPORTS / "skill_inventory.csv",
        REPORTS / "skill_inventory.md",
        REPORTS / "release_readiness.json",
        REPORTS / "release_readiness.md",
        REPORTS / "repo_truth_report.json",
        REPORTS / "repo_truth_report.md",
    ]
    missing = [str(p.relative_to(ROOT)) for p in expected if not p.exists()]
    if missing:
        raise SmokeFailure(f"Missing expected reports: {missing}")
    return [str(p.relative_to(ROOT)) for p in expected]


def run_smoke_test(*, dry_run: bool, offline: bool) -> dict:
    if not (dry_run and offline):
        raise SmokeFailure("Smoke pass only supports --dry-run --offline mode.")

    checks: dict[str, dict] = {}

    inventory_cmd = [sys.executable, str(ROOT / "scripts" / "generate_skill_inventory.py"), "--root", str(ROOT)]
    inventory_result = _run(inventory_cmd)
    if inventory_result.returncode != 0:
        raise SmokeFailure(f"Skill inventory load failed: {inventory_result.stderr.strip()}")
    checks["skill_inventory_load"] = {"ok": True, "message": inventory_result.stdout.strip()}

    sdlc_plan = _run_json(
        [sys.executable, str(ROOT / "scripts" / "orchestration" / "plan_workflow.py"), "Build a secure API release"],
    )
    checks["sdlc_workflow_plan"] = {"ok": bool(sdlc_plan.get("skill_chain")), "plan_id": sdlc_plan.get("plan_id")}
    if not checks["sdlc_workflow_plan"]["ok"]:
        raise SmokeFailure("SDLC workflow plan returned empty skill_chain")

    gtm_plan = _run_json(
        [sys.executable, str(ROOT / "scripts" / "orchestration" / "plan_gtm_workflow.py"), "Launch product and improve SEO"],
    )
    checks["gtm_workflow_plan"] = {"ok": bool(gtm_plan.get("skill_chain")), "plan_id": gtm_plan.get("plan_id")}
    if not checks["gtm_workflow_plan"]["ok"]:
        raise SmokeFailure("GTM workflow plan returned empty skill_chain")

    business_route = _run_json(
        [sys.executable, str(ROOT / "scripts" / "business" / "route_business_task.py"), "--task", "Process invoice from Acme Corp"],
    )
    checks["business_workflow_plan"] = {
        "ok": bool(business_route.get("workflow", {}).get("steps")),
        "skill": business_route.get("routing", {}).get("skill"),
    }
    if not checks["business_workflow_plan"]["ok"]:
        raise SmokeFailure("Business workflow plan returned no steps")

    context_packet = _run_json(
        [sys.executable, str(ROOT / "scripts" / "memory" / "build_context_packet.py")],
        stdin=json.dumps({"objective": "Release smoke test", "phase": "release"}),
    )
    required_fields = {"objective", "phase", "decisions", "constraints", "artifacts", "risks", "next_action"}
    checks["context_packet_build"] = {"ok": required_fields.issubset(context_packet.keys())}
    if not checks["context_packet_build"]["ok"]:
        raise SmokeFailure("Context packet missing required fields")

    schema_paths = [
        ROOT / "schemas" / "skill-manifest-v9.schema.json",
        ROOT / "schemas" / "telemetry-event.schema.json",
        ROOT / "schemas" / "hitl-gate.schema.json",
        ROOT / "schemas" / "context-loading.schema.json",
    ]
    missing_schemas = [str(p.relative_to(ROOT)) for p in schema_paths if not p.exists()]
    checks["required_schemas_load"] = {"ok": not missing_schemas, "missing": missing_schemas}
    if missing_schemas:
        raise SmokeFailure(f"Required schemas missing: {missing_schemas}")

    _run([sys.executable, str(ROOT / "scripts" / "generate_release_reports.py")])
    report_files = _assert_report_files_exist()
    checks["expected_reports_exist"] = {"ok": True, "files": report_files}

    return {
        "mode": {"dry_run": dry_run, "offline": offline},
        "external_api_calls_required": False,
        "checks": checks,
        "status": "pass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release smoke tests in offline mode")
    parser.add_argument("--dry-run", action="store_true", help="Run without publishing side effects")
    parser.add_argument("--offline", action="store_true", help="Assert no network/API dependencies")
    args = parser.parse_args()

    try:
        result = run_smoke_test(dry_run=args.dry_run, offline=args.offline)
    except SmokeFailure as exc:
        print(json.dumps({"status": "fail", "error": str(exc)}, indent=2))
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
