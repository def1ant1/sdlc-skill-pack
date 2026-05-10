#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    ["python", "scripts/validate_backlog_truth.py"],
    ["python", "scripts/validate_skill_contracts.py"],
    ["python", "scripts/check_context_budget.py"],
    ["python", "scripts/generate_skill_inventory.py"],
    ["python", "scripts/generate_dependency_graph.py"],
    ["python", "scripts/detect_skill_overlap.py"],
    ["python", "scripts/validate_skill_evals.py"],
    ["python", "scripts/validate_telemetry_events.py"],
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
