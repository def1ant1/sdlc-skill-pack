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
    parser.add_argument("--json-out", type=Path, default=Path("reports/repo_truth_report.json"))
    parser.add_argument("--md-out", type=Path, default=Path("reports/repo_truth_report.md"))
    parser.add_argument("--readiness-out", type=Path, default=Path("reports/release_readiness.md"))
    args = parser.parse_args()
    root = args.root

    truth_out = root / "reports" / "repo_truth_details.json"
    validation = subprocess.run(
        [sys.executable, str(root / "scripts" / "validate_backlog_truth.py"), "--root", str(root), "--json-out", str(truth_out.relative_to(root))],
        capture_output=True,
        text=True,
    )

    truth = json.loads(truth_out.read_text(encoding="utf-8"))
    report = {
        "status": truth["status"],
        "generated_at": truth["generated_at"],
        "reference_count": truth["reference_count"],
        "phase_count": truth["phase_count"],
        "phase_completion_count": truth["phase_completion_count"],
        "existing_count": truth["existing_count"],
        "missing_count": truth["missing_count"],
        "stale_claim_count": truth["stale_claim_count"],
        "missing": [f"{r['path']} ({r['backlog_file']}:{r['line']}, {r['phase']})" for r in truth["missing"]],
    }

    json_path = root / args.json_out
    md_path = root / args.md_out
    readiness_path = root / args.readiness_out
    for p in [json_path, md_path, readiness_path]:
        p.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    md = ["# Repo Truth Report", "", f"Generated: `{report['generated_at']}`", "", f"Status: **{report['status'].upper()}**", "", f"- Total references: {report['reference_count']}", f"- Existing references: {report['existing_count']}", f"- Missing references: {report['missing_count']}", f"- Stale completion claims: {report['stale_claim_count']}", f"- Phase completion: {report['phase_completion_count']}/{report['phase_count']}", ""]
    if report["missing"]:
        md.extend(["## Missing Paths", ""])
        md.extend([f"- {item}" for item in report["missing"]])
    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")

    readiness = [
        "# Release Readiness (Canonical)",
        "",
        "This file is the canonical release-time status source of truth.",
        "",
        f"Generated: `{report['generated_at']}`",
        f"Status: **{report['status'].upper()}**",
        "",
        "## Repo Truth Summary",
        f"- References checked: **{report['reference_count']}**",
        f"- Existing deliverables: **{report['existing_count']}**",
        f"- Missing deliverables: **{report['missing_count']}**",
        f"- Stale completion claims: **{report['stale_claim_count']}**",
        f"- Phase completion: **{report['phase_completion_count']}/{report['phase_count']}**",
    ]
    readiness_path.write_text("\n".join(readiness) + "\n", encoding="utf-8")

    print(f"Generated {md_path}, {json_path}, and {readiness_path}")
    return 0 if validation.returncode == 0 else validation.returncode


if __name__ == "__main__":
    raise SystemExit(main())
