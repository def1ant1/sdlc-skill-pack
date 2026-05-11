#!/usr/bin/env python3
"""Generate PR-ready skill improvement proposals from failed workflow evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HIGH_RISK_AREAS = {"governance", "security", "legal", "payments", "deployment"}


def load_failures(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data.get("failures", [])
    return data


def classify_risk(item: dict) -> str:
    text = " ".join(
        str(item.get(k, ""))
        for k in ("domain", "category", "workflow", "failure_reason")
    ).lower()
    return "high" if any(token in text for token in HIGH_RISK_AREAS) else "medium"


def build_proposal(item: dict) -> dict:
    risk = classify_risk(item)
    return {
        "workflow": item.get("workflow", "unknown"),
        "skill": item.get("skill", "unknown"),
        "failure_reason": item.get("failure_reason", "unspecified"),
        "suggested_patch": {
            "target_file": item.get("target_file", "skills/TODO/SKILL.md"),
            "change_summary": item.get("suggested_change", "Add missing safeguards and clarify protocol."),
        },
        "suggested_tests": item.get("suggested_tests", ["pytest -q tests/skills"]),
        "suggested_evals": item.get("suggested_evals", ["python scripts/validation/validate_frontmatter.py ."]),
        "risk_level": risk,
        "auto_apply_allowed": False,
        "auto_merge_allowed": False,
        "requires_human_approval": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--failures", required=True, help="JSON file containing failed workflow evidence")
    parser.add_argument("--output", required=True, help="Output JSON path")
    args = parser.parse_args()

    failures = load_failures(Path(args.failures))
    proposals = [build_proposal(item) for item in failures]
    payload = {
        "source": str(args.failures),
        "proposal_count": len(proposals),
        "proposals": proposals,
        "guardrails": {
            "auto_apply": "disabled",
            "auto_merge": "disabled",
            "high_risk_requires_manual_review": True,
        },
    }
    Path(args.output).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
