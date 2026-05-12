#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def convert(plan: dict) -> dict:
    steps: list[dict] = []
    for phase in plan.get("phases", []):
        for task in sorted(phase.get("tasks", []), key=lambda t: t.get("priority", 999)):
            if task.get("status", "approved") != "approved":
                continue
            steps.append({
                "id": task["id"],
                "title": task.get("title", "Untitled task"),
                "phase": phase.get("id", "unknown-phase"),
                "description": task.get("description", ""),
                "skills": task.get("skills", []),
                "gates": task.get("gates", []),
                "depends_on": task.get("depends_on", []),
                "cost_assumptions": task.get("cost_assumptions", plan.get("cost_assumptions", {})),
            })

    return {
        "id": f"workflow-{plan.get('id', 'unknown-plan')}",
        "description": f"Workflow derived from plan {plan.get('id', 'unknown-plan')}",
        "objectives": plan.get("objectives", []),
        "steps": steps,
        "preview": {
            "skills": sorted({s for st in steps for s in st.get("skills", [])}),
            "gates": [g for st in steps for g in st.get("gates", [])],
            "dependencies": {st["id"]: st.get("depends_on", []) for st in steps},
            "cost_assumptions": plan.get("cost_assumptions", {}),
        },
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Convert plan into workflow artifact")
    p.add_argument("--plan", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args()

    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    converted = convert(plan)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(converted, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(converted, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
