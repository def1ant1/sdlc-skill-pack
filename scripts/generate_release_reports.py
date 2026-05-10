#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path.cwd()
REPORTS = ROOT / "reports"

COMMANDS = [
    [sys.executable, "scripts/generate_repo_truth_report.py"],
    [sys.executable, "scripts/generate_skill_inventory.py"],
    [sys.executable, "scripts/generate_dependency_graph.py"],
    [sys.executable, "scripts/detect_skill_overlap.py"],
]


def _run(cmd: list[str], allow_failure: bool = False) -> None:
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd)
    if result.returncode != 0 and not allow_failure:
        raise SystemExit(result.returncode)


def _skill_rows() -> list[dict]:
    return json.loads((REPORTS / "skill_inventory.json").read_text(encoding="utf-8"))


def _pytest_collect() -> dict:
    cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q"]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    collected = 0
    for line in (proc.stdout + "\n" + proc.stderr).splitlines():
        if " test" in line and "collected" in line:
            # Example: "190 tests collected"
            token = line.strip().split()[0]
            if token.isdigit():
                collected = int(token)
                break
    return {
        "command": " ".join(cmd),
        "returncode": proc.returncode,
        "collected_tests": collected,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-10:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-10:]),
    }


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def generate_derived_reports() -> None:
    rows = _skill_rows()
    counts = Counter(r["category"] for r in rows)
    total = len(rows)
    with_hitl = sum(1 for r in rows if (r.get("hitl_gates") or 0) > 0)

    # Business coverage heuristic from filesystem categories.
    business_ids = sorted(
        r["id"] for r in rows if r["category"] == "skills" and any(x in r["id"] for x in ["finance", "hr", "sales", "marketing", "procurement", "inventory", "forecast", "customer", "vendor", "invoice", "accounting", "revenue", "pricing", "budget"])
    )

    test_info = _pytest_collect()

    readiness = {
        "generated_from": {
            "skill_inventory": "reports/skill_inventory.json",
            "repo_truth": "reports/repo_truth_report.json",
            "pytest_collect": test_info["command"],
        },
        "totals": {
            "skills_total": total,
            "core_total": counts.get("core", 0),
            "skills_pack_total": counts.get("skills", 0),
            "agents_total": counts.get("agents", 0),
            "skills_with_hitl_markers": with_hitl,
            "business_skill_total": len(business_ids),
            "tests_collected": test_info["collected_tests"],
        },
    }
    _write(REPORTS / "release_readiness.json", json.dumps(readiness, indent=2) + "\n")

    _write(
        REPORTS / "release_readiness.md",
        "\n".join([
            "# Release Readiness",
            "",
            "All numeric claims here are generated from repository state and test collection output.",
            "",
            f"- Total skills indexed: **{total}**",
            f"- Core skills: **{counts.get('core', 0)}**",
            f"- Domain skills: **{counts.get('skills', 0)}**",
            f"- Agent packs: **{counts.get('agents', 0)}**",
            f"- Skills with HITL markers: **{with_hitl}**",
            f"- Tests collected (`pytest --collect-only -q`): **{test_info['collected_tests']}**",
            "",
            "Sources: `reports/skill_inventory.json`, `reports/release_readiness.json`.",
        ]) + "\n",
    )

    _write(
        REPORTS / "hitl_coverage_report.md",
        "\n".join([
            "# HITL Coverage Report",
            "",
            f"- Skills with HITL markers: **{with_hitl}**",
            f"- Total indexed skills: **{total}**",
            f"- Coverage ratio: **{(with_hitl / total * 100) if total else 0:.2f}%**",
            "",
            "Derived from `reports/skill_inventory.json`.",
        ]) + "\n",
    )

    _write(
        REPORTS / "test_summary.md",
        "\n".join([
            "# Test Summary",
            "",
            f"- Command: `{test_info['command']}`",
            f"- Return code: **{test_info['returncode']}**",
            f"- Collected tests: **{test_info['collected_tests']}**",
            "",
            "## Collected output tail",
            "```",
            test_info["stdout_tail"] or "(no stdout)",
            "```",
            "",
            "## Stderr tail",
            "```",
            test_info["stderr_tail"] or "(no stderr)",
            "```",
        ]) + "\n",
    )

    _write(
        REPORTS / "business_skill_coverage.md",
        "\n".join([
            "# Business Skill Coverage",
            "",
            f"- Business-oriented skills detected: **{len(business_ids)}**",
            "",
            "## Detected skill IDs",
            *[f"- `{sid}`" for sid in business_ids],
            "",
            "Derived from `reports/skill_inventory.json` using ID taxonomy matching.",
        ]) + "\n",
    )


if __name__ == "__main__":
    for idx, command in enumerate(COMMANDS):
        _run(command, allow_failure=(idx == 0))
    generate_derived_reports()
    print("Generated release readiness, HITL, test, and business coverage reports")
