#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(plan: dict) -> dict:
    steps = []
    for phase in plan.get("phases", []):
        for task in sorted(phase.get("tasks", []), key=lambda t: t.get("priority", 999)):
            if task.get("status") != "approved":
                continue
            steps.append(
                {
                    "id": task["id"],
                    "title": task["title"],
                    "phase": phase["id"],
                    "description": task.get("description", ""),
                    "depends_on": [],
                }
            )
    return {
        "id": f"workflow-{plan['id']}",
        "description": f"Approved workflow derived from {plan['id']}",
        "objectives": plan.get("objectives", []),
        "steps": steps,
        "required_skills": plan.get("required_skills", []),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Convert approved plan scope into workflow JSON")
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    plan = json.loads(a.plan.read_text(encoding="utf-8"))
    workflow = convert(plan)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(workflow, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(workflow, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
