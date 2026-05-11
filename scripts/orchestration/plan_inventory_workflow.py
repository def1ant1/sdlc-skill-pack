#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE))
from planning_contract import run_planner_cli  # noqa: E402


if __name__ == "__main__":
    domain = Path(__file__).stem.replace("plan_", "").replace("_workflow", "").replace("_", "-")
    raise SystemExit(run_planner_cli(domain))
