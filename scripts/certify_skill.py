#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


def certify(skill_dir: Path, checks: dict[str, bool], evidence: dict[str, str], unresolved_routing_collisions: int) -> dict:
    reasons: list[str] = []
    manifest_path = skill_dir / "manifest.v9.json"

    if not manifest_path.exists():
        reasons.append("missing_manifest")
    else:
        try:
            json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            reasons.append("invalid_manifest_json")

    for check_name, passed in checks.items():
        if not passed:
            reasons.append(f"{check_name}_failed")
    if unresolved_routing_collisions > 0:
        reasons.append("unresolved_routing_collisions")

    return {
        "skill": skill_dir.name,
        "status": "certified" if not reasons else "rejected",
        "reasons": reasons,
        "criteria": checks,
        "evidence": evidence,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }


def write_report(path: Path, result: dict) -> None:
    lines = [
        "# Skill Certification Report",
        "",
        "## Repeatable certification criteria",
        "- Manifest exists and parses as JSON.",
        "- Eval/security/context/context-budget/telemetry checks pass.",
        "- No unresolved routing collisions.",
        "",
        "## Evidence outputs",
        f"- Skill: `{result['skill']}`",
        f"- Timestamp (UTC): `{result['generated_at_utc']}`",
        f"- Status: `{result['status']}`",
        f"- Reasons: `{', '.join(result['reasons']) if result['reasons'] else 'none'}`",
        "",
        "```json",
        json.dumps(result, indent=2),
        "```",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("skill_dir", type=Path)
    p.add_argument("--eval-passed", action="store_true")
    p.add_argument("--security-passed", action="store_true")
    p.add_argument("--context-passed", action="store_true")
    p.add_argument("--context-budget-passed", action="store_true")
    p.add_argument("--telemetry-passed", action="store_true")
    p.add_argument("--unresolved-routing-collisions", type=int, default=0)
    p.add_argument("--evidence-eval", default="reports/skill_benchmark_results.json")
    p.add_argument("--evidence-security", default="reports/security_scan_report.md")
    p.add_argument("--evidence-context", default="reports/context_budget_report.md")
    p.add_argument("--evidence-telemetry", default="reports/ai_telemetry_replay.md")
    p.add_argument("--report", default="reports/skill_certification_report.md")
    args = p.parse_args()

    checks = {
        "eval": args.eval_passed,
        "security": args.security_passed,
        "context": args.context_passed,
        "context_budget": args.context_budget_passed,
        "telemetry": args.telemetry_passed,
    }
    evidence = {
        "eval": args.evidence_eval,
        "security": args.evidence_security,
        "context": args.evidence_context,
        "telemetry": args.evidence_telemetry,
    }

    result = certify(args.skill_dir, checks, evidence, args.unresolved_routing_collisions)
    write_report(Path(args.report), result)
    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "certified" else 1


if __name__ == "__main__":
    raise SystemExit(main())
