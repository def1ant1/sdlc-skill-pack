#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root

    refs = json.loads(
        subprocess.run(
            [sys.executable, str(root / "scripts" / "extract_backlog_paths.py"), "--root", str(root)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
    )
    validation = subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_backlog_truth.py"), "--root", str(root)],
        capture_output=True,
        text=True,
    )

    missing = [ln[2:] for ln in validation.stdout.splitlines() if ln.startswith("- ")]
    report = {
        "status": "pass" if validation.returncode == 0 else "fail",
        "reference_count": len(refs),
        "missing_count": len(missing),
        "missing": missing,
    }

    reports_dir = root / "reports"
    reports_dir.mkdir(exist_ok=True)
    (reports_dir / "repo_truth_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )

    md = [
        "# Repo Truth Report",
        "",
        f"Status: **{report['status'].upper()}**",
        "",
        f"- Total references: {report['reference_count']}",
        f"- Missing references: {report['missing_count']}",
        "",
    ]
    if missing:
        md.extend(["## Missing Paths", ""])
        md.extend([f"- {item}" for item in missing])

    (reports_dir / "repo_truth_report.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("Generated reports/repo_truth_report.md and reports/repo_truth_report.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
