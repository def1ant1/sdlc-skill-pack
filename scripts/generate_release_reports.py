#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys

COMMANDS = [
    ["python", "scripts/generate_repo_truth_report.py"],
    ["python", "scripts/generate_skill_inventory.py"],
    ["python", "scripts/generate_dependency_graph.py"],
    ["python", "scripts/detect_skill_overlap.py"],
]


def main() -> int:
    for cmd in COMMANDS:
        print(f"$ {' '.join(cmd)}")
        result = subprocess.run(cmd)
        if result.returncode != 0:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
