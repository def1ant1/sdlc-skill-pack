#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from planning_contract import build_domain_plan  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a domain workflow plan")
    parser.add_argument("objective", nargs="?", help="Objective text")
    parser.add_argument("--stdin", action="store_true", help="Read objective from stdin")
    args = parser.parse_args()

    objective = sys.stdin.read().strip() if args.stdin or not args.objective else args.objective
    if not objective:
        print("Error: objective is required", file=sys.stderr)
        return 1

    domain = Path(__file__).stem.replace("plan_", "").replace("_workflow", "")
    print(json.dumps(build_domain_plan(objective, domain), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
