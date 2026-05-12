#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(plan: dict) -> list[dict]:
    items: list[dict] = []
    for phase in plan.get("phases", []):
        for task in sorted(phase.get("tasks", []), key=lambda t: t.get("priority", 999)):
            if task.get("status") != "approved":
                continue
            items.append(
                {
                    "id": task["id"],
                    "title": task["title"],
                    "phase": phase["id"],
                    "priority": task.get("priority", 999),
                    "status": "ready",
                    "approvals_required": task.get("approvals_required", []),
                }
            )
    return items


def main() -> int:
    p = argparse.ArgumentParser(description="Convert approved plan scope into executable task list")
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    tasks = convert(plan)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(tasks, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(tasks, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
