#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"


@dataclass(frozen=True)
class Check:
    key: str
    label: str
    command: list[str]


CHECKS: tuple[Check, ...] = (
    Check("contracts", "Contracts", [sys.executable, "scripts/validate_skill_contracts.py"]),
    Check("context_budget", "Context budget", [sys.executable, "scripts/check_context_budget.py"]),
    Check("eval_telemetry", "Eval and telemetry coverage", [sys.executable, "scripts/validate_skill_evals.py"]),
    Check("hitl", "HITL coverage", [sys.executable, "scripts/validate_hitl_coverage.py"]),
    Check("backlog_staleness", "Backlog staleness", [sys.executable, "scripts/check_work_tasks_snapshot_freshness.py"]),
    Check("report_freshness", "Report freshness", [sys.executable, "scripts/docs/enforce_doc_freshness.py"]),
    Check("secret_scan", "Secret scan", [sys.executable, "scripts/security/scan_for_secrets.py"]),
    Check("policy_coverage", "Policy coverage", [sys.executable, "scripts/validate_backlog_truth.py"]),
    Check("maturity", "Maturity thresholds", [sys.executable, "scripts/grade_skill_maturity.py"]),
    Check("readme_claims", "README claim verification", [sys.executable, "scripts/docs/validate_readme_claims.py"]),
    Check("routing_collisions", "Routing collisions/cycles", [sys.executable, "scripts/detect_skill_overlap.py"]),
)


def run_check(check: Check) -> dict[str, Any]:
    proc = subprocess.run(check.command, cwd=ROOT, capture_output=True, text=True)
    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    return {
        "key": check.key,
        "label": check.label,
        "command": " ".join(check.command),
        "returncode": proc.returncode,
        "passed": proc.returncode == 0,
        "stdout_tail": "\n".join(stdout.splitlines()[-20:]),
        "stderr_tail": "\n".join(stderr.splitlines()[-20:]),
    }


def parse_hitl_metrics(check_results: dict[str, dict[str, Any]]) -> dict[str, Any]:
    result = check_results.get("hitl") or {}
    payload = {"critical_ratio": None, "high_risk_ratio": None, "domain_failures": []}
    text = ((result.get("stdout_tail") or "") + "\n" + (result.get("stderr_tail") or "")).strip()
    if not text:
        return payload
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return payload
    payload["critical_ratio"] = data.get("l3_ratio")
    payload["high_risk_ratio"] = data.get("l2_ratio")
    payload["domain_failures"] = data.get("domain_failures") or []
    return payload


def parse_p0_maturity() -> dict[str, Any]:
    maturity_report = REPORTS / "skill_maturity_report.md"
    out: dict[str, Any] = {"p0_min_level": None, "violations": []}
    if not maturity_report.exists():
        return out

    p0_min: int | None = None
    violations: list[str] = []
    for line in maturity_report.read_text(encoding="utf-8").splitlines():
        if "|" not in line or "`" not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 5:
            continue
        skill_col, level_col, tags_col = parts[1], parts[2], parts[3]
        if "P0" not in tags_col:
            continue
        m = re.search(r"`([^`]+)`", skill_col)
        if not m:
            continue
        skill_id = m.group(1)
        try:
            level = int(level_col)
        except ValueError:
            continue
        p0_min = level if p0_min is None else min(p0_min, level)
        if level < 4:
            violations.append(f"{skill_id}:{level}")

    out["p0_min_level"] = p0_min
    out["violations"] = violations
    return out


def parse_collision_summary() -> dict[str, int | None]:
    report = REPORTS / "routing_collision_report.md"
    summary: dict[str, int | None] = {"trigger_overlaps": None, "dependency_cycles": None}
    if not report.exists():
        return summary
    for line in report.read_text(encoding="utf-8").splitlines():
        if line.startswith("- Trigger overlaps:"):
            try:
                summary["trigger_overlaps"] = int(line.rsplit(":", 1)[1].strip())
            except ValueError:
                pass
        if line.startswith("- Dependency cycles:"):
            try:
                summary["dependency_cycles"] = int(line.rsplit(":", 1)[1].strip())
            except ValueError:
                pass
    return summary


def build_release_status(check_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    check_map = {row["key"]: row for row in check_rows}
    failures: list[str] = []

    p0_failures = [row["key"] for row in check_rows if not row["passed"]]
    if p0_failures:
        failures.append(f"P0 gate failures present: {', '.join(sorted(p0_failures))}")

    hitl = parse_hitl_metrics(check_map)
    critical_ratio = hitl.get("critical_ratio")
    high_ratio = hitl.get("high_risk_ratio")
    if critical_ratio is None or critical_ratio < 100.0:
        failures.append(f"critical HITL coverage must be 100% (actual: {critical_ratio})")
    if high_ratio is None or high_ratio < 95.0:
        failures.append(f"high-risk HITL coverage must be >=95% (actual: {high_ratio})")

    maturity = parse_p0_maturity()
    if maturity["p0_min_level"] is None or maturity["p0_min_level"] < 4:
        failures.append(f"P0 maturity min level must be >=4 (actual: {maturity['p0_min_level']})")
    if maturity["violations"]:
        failures.append("P0 maturity violations: " + ", ".join(maturity["violations"]))

    collisions = parse_collision_summary()
    if (collisions.get("trigger_overlaps") or 0) > 0:
        failures.append(f"unresolved routing collisions: {collisions.get('trigger_overlaps')}")
    if (collisions.get("dependency_cycles") or 0) > 0:
        failures.append(f"unresolved routing cycles: {collisions.get('dependency_cycles')}")

    status = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": check_rows,
        "criteria": {
            "p0_failures_must_equal_zero": len(p0_failures) == 0,
            "critical_hitl_100": critical_ratio is not None and critical_ratio >= 100.0,
            "high_risk_hitl_gte_95": high_ratio is not None and high_ratio >= 95.0,
            "p0_maturity_gte_4": maturity["p0_min_level"] is not None and maturity["p0_min_level"] >= 4 and not maturity["violations"],
            "no_unresolved_p0_p1_routing_collisions": (collisions.get("trigger_overlaps") or 0) == 0,
            "no_unresolved_p0_p1_routing_cycles": (collisions.get("dependency_cycles") or 0) == 0,
        },
        "metrics": {
            "hitl": hitl,
            "maturity": maturity,
            "routing": collisions,
            "p0_failure_count": len(p0_failures),
        },
        "ready_for_release": len(failures) == 0,
        "failure_reasons": failures,
    }
    return status, failures


def write_reports(status: dict[str, Any]) -> None:
    REPORTS.mkdir(parents=True, exist_ok=True)
    (REPORTS / "release_readiness.json").write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Release Readiness",
        "",
        f"- Generated at (UTC): **{status['generated_at_utc']}**",
        f"- Ready for release: **{'YES' if status['ready_for_release'] else 'NO'}**",
        "",
        "## Criteria",
    ]
    for key, passed in status["criteria"].items():
        lines.append(f"- {'✅' if passed else '❌'} `{key}`")

    lines += ["", "## Checks"]
    for row in status["checks"]:
        lines.append(f"- {'✅' if row['passed'] else '❌'} **{row['label']}** (`{row['command']}`)")

    if status["failure_reasons"]:
        lines += ["", "## Failure Reasons"]
        lines.extend([f"- {reason}" for reason in status["failure_reasons"]])

    (REPORTS / "release_readiness.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    rows = [run_check(check) for check in CHECKS]
    status, failures = build_release_status(rows)
    write_reports(status)
    print(f"Wrote {REPORTS / 'release_readiness.md'} and {REPORTS / 'release_readiness.json'}")
    if failures:
        print("Release readiness failed:")
        for reason in failures:
            print(f"- {reason}")
        return 1
    print("Release readiness passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
