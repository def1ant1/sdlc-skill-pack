#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    ["python", "scripts/docs/validate_doc_uniqueness.py"],
    ["python", "scripts/docs/check_backlog_changelog_sync.py"],
    ["python", "scripts/docs/enforce_doc_freshness.py"],
    ["python", "scripts/validate_backlog_truth.py"],
    ["python", "scripts/validate_skill_contracts.py"],
    ["python", "scripts/check_context_budget.py"],
    ["python", "scripts/generate_skill_inventory.py"],
    ["python", "scripts/generate_dependency_graph.py"],
    ["python", "scripts/detect_skill_overlap.py"],
    ["python", "scripts/validate_skill_evals.py"],
    ["python", "scripts/validate_telemetry_events.py"],
    ["python", "scripts/validate_hitl_coverage.py"],
    ["python", "scripts/grade_skill_maturity.py"],
]


def main() -> int:
    failures = 0
    for cmd in COMMANDS:
        print(f"\n$ {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            failures += 1
    if failures:
        print(f"\nPre-merge checks failed: {failures} command(s) returned non-zero.")
        return 1
    print("\nAll pre-merge checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
