#!/usr/bin/env python3
"""
generate_skill_improvement_plan.py — Generate a prioritized skill improvement plan.

Reads gap output from detect_skill_gaps.py and produces a sprint-ready improvement
plan with prioritized items, recommended actions, and estimated complexity.

Usage:
    python scripts/skills/detect_skill_gaps.py --output json | \
        python scripts/skills/generate_skill_improvement_plan.py

    Or from file:
    python scripts/skills/generate_skill_improvement_plan.py --gaps gaps.json
"""

import json
import sys
from datetime import date, timedelta
from pathlib import Path


SEVERITY_PRIORITY = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
COMPLEXITY_BY_TYPE = {
    "MISSING": "L",
    "WEAK": "M",
    "BELOW_TARGET": "S",
    "STALE": "S",
    "MATURITY": "S",
    "MISSING_REFERENCE": "S",
    "DEPENDENCY": "S",
    "RESILIENCE": "M",
    "INVALID_FRONTMATTER": "S",
}

SPRINT_WEEKS = 2


def estimate_sprint(priority_index: int) -> str:
    """Assign items to sprints based on priority rank."""
    sprint_number = (priority_index // 5) + 1
    sprint_start = date.today() + timedelta(weeks=(sprint_number - 1) * SPRINT_WEEKS)
    return f"Sprint {sprint_number} (starts {sprint_start.strftime('%Y-%m-%d')})"


def generate_plan(gaps: list[dict]) -> dict:
    """Generate improvement plan from gap list."""
    # Sort by severity then type
    sorted_gaps = sorted(
        gaps,
        key=lambda g: (
            SEVERITY_PRIORITY.get(g.get("severity", "LOW"), 3),
            g.get("type", ""),
        ),
    )

    items = []
    for i, gap in enumerate(sorted_gaps):
        gap_type = gap.get("type", "UNKNOWN")
        complexity = COMPLEXITY_BY_TYPE.get(gap_type, "M")

        items.append({
            "rank": i + 1,
            "skill": gap.get("skill", "unknown"),
            "type": gap_type,
            "severity": gap.get("severity", "UNKNOWN"),
            "rule": gap.get("rule", ""),
            "description": gap.get("description", ""),
            "recommended_action": gap.get("recommended_action", ""),
            "complexity": complexity,
            "target_sprint": estimate_sprint(i),
            "status": "open",
        })

    # Group by sprint
    by_sprint: dict[str, list] = {}
    for item in items:
        sprint = item["target_sprint"]
        by_sprint.setdefault(sprint, []).append(item)

    return {
        "generated_at": date.today().isoformat(),
        "total_gaps": len(gaps),
        "critical": sum(1 for g in gaps if g.get("severity") == "CRITICAL"),
        "high": sum(1 for g in gaps if g.get("severity") == "HIGH"),
        "medium": sum(1 for g in gaps if g.get("severity") == "MEDIUM"),
        "items": items,
        "sprints": by_sprint,
    }


def print_plan(plan: dict) -> None:
    """Print improvement plan as readable text."""
    print(f"\n{'SKILL IMPROVEMENT PLAN':=<70}")
    print(f"Generated: {plan['generated_at']}")
    print(f"Total gaps: {plan['total_gaps']} "
          f"(CRITICAL: {plan['critical']}, HIGH: {plan['high']}, MEDIUM: {plan['medium']})")

    print()
    for sprint, items in plan["sprints"].items():
        total_complexity = {"S": 0, "M": 0, "L": 0}
        for item in items:
            total_complexity[item["complexity"]] += 1

        print(f"\n{sprint}")
        print(f"  Items: {len(items)} | "
              f"S: {total_complexity['S']} M: {total_complexity['M']} L: {total_complexity['L']}")
        print("  " + "-" * 60)
        for item in items:
            sev = f"[{item['severity']}]"
            print(f"  {item['rank']:>3}. {sev:<12} {item['skill']}")
            print(f"       Complexity: {item['complexity']} | {item['type']}")
            print(f"       {item['recommended_action']}")


def main() -> int:
    args = sys.argv[1:]
    gaps_file = None

    i = 0
    while i < len(args):
        if args[i] == "--gaps" and i + 1 < len(args):
            gaps_file = Path(args[i + 1])
            i += 2
        else:
            i += 1

    if gaps_file:
        if not gaps_file.exists():
            print(f"ERROR: Gaps file not found: {gaps_file}", file=sys.stderr)
            return 1
        gaps = json.loads(gaps_file.read_text())
    else:
        # Read from stdin
        try:
            gaps = json.loads(sys.stdin.read())
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON from stdin: {e}", file=sys.stderr)
            return 1

    if not isinstance(gaps, list):
        print("ERROR: Expected a JSON array of gap records", file=sys.stderr)
        return 1

    plan = generate_plan(gaps)
    print_plan(plan)

    return 0


if __name__ == "__main__":
    sys.exit(main())