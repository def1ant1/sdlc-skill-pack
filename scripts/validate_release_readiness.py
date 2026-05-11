#!/usr/bin/env python3
from __future__ import annotations

import json
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
    Check("release_reports", "Release report generation", [sys.executable, "scripts/generate_release_reports.py"]),
    Check("release_artifacts", "Version/changelog/release-notes consistency", [sys.executable, "scripts/validate_release_artifacts.py"]),
    Check("governance", "Section 15 governance gates", [sys.executable, "scripts/validate_section15_release_gates.py"]),
    Check("smoke", "Offline smoke test", [sys.executable, "scripts/smoke_test_release.py", "--dry-run", "--offline"]),
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


def build_release_status(check_rows: list[dict[str, Any]]) -> tuple[dict[str, Any], list[str]]:
    failures = [f"{row['key']}: failed with rc={row['returncode']}" for row in check_rows if not row["passed"]]
    status = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "checks": check_rows,
        "criteria": {
            "all_release_checks_pass": len(failures) == 0,
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
