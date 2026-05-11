#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml

RUBRIC_KEYS = [
    "manifest",
    "skill_protocol",
    "contracts",
    "entities_events_refs",
    "governance_refs",
    "hitl",
    "telemetry",
    "eval",
    "examples",
    "failure_modes",
    "boundary_language",
]
MVP_SKILLS = {
    "cash-flow-forecasting",
    "financial-management",
    "revenue-leakage-detection",
    "process-optimization-phase-pack",
    "finance-accounting-phase-pack",
}
HIGH_RISK_CRITICAL_MVP = {"revenue-leakage-detection", "financial-management"}


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    return {} if end == -1 else (yaml.safe_load(text[3 : end + 1]) or {})


def eval_skill(skill_dir: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm = load_frontmatter(skill_md)
    meta = fm.get("metadata") or {}

    manifest_name = meta.get("manifest", "manifest.v9.json")
    manifest_path = skill_dir / manifest_name
    manifest: dict[str, Any] | None = None
    checks: dict[str, bool] = {}

    checks["manifest"] = manifest_path.is_file()
    if checks["manifest"]:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            checks["manifest"] = False

    checks["skill_protocol"] = all(k in fm for k in ("name", "description", "use_when", "do_not_use_when"))
    checks["contracts"] = "input_contract" in text.lower() and "output_contract" in text.lower()
    checks["entities_events_refs"] = "entity" in text.lower() and "event" in text.lower()
    checks["governance_refs"] = "governance" in text.lower()
    checks["hitl"] = "human" in text.lower() and "approval" in text.lower()
    checks["telemetry"] = "telemetry" in text.lower()
    checks["eval"] = (skill_dir / "eval.spec.json").is_file()
    checks["examples"] = (skill_dir / "examples").is_dir()
    checks["failure_modes"] = "failure" in text.lower()
    checks["boundary_language"] = any(
        k in text.lower() for k in ("do_not_use_when", "do not use when", "out of scope", "not supported", "boundary")
    )

    if manifest:
        checks["contracts"] = checks["contracts"] or bool(manifest.get("input_contract") and manifest.get("output_contract"))
        checks["entities_events_refs"] = checks["entities_events_refs"] or bool(manifest.get("data_contracts") or manifest.get("telemetry_events"))
        checks["governance_refs"] = checks["governance_refs"] or bool(manifest.get("governance_level"))
        checks["hitl"] = checks["hitl"] or manifest.get("human_approval_required") is not None
        checks["telemetry"] = checks["telemetry"] or bool(manifest.get("telemetry_events"))
        checks["eval"] = checks["eval"] or bool(manifest.get("eval_metrics"))
        checks["failure_modes"] = checks["failure_modes"] or bool(manifest.get("failure_modes"))

    passed = sum(1 for v in checks.values() if v)
    level = min(5, passed // 2)

    return {
        "id": skill_dir.name,
        "level": level,
        "checks": checks,
        "missing": [k for k in RUBRIC_KEYS if not checks[k]],
        "is_mvp": skill_dir.name in MVP_SKILLS,
        "is_high_risk_critical_mvp": skill_dir.name in HIGH_RISK_CRITICAL_MVP,
    }


def write_report(path: Path, rows: list[dict[str, Any]], summary: dict[str, Any]) -> None:
    lines = [
        "# Skill Maturity Report",
        "",
        "## Scoring framework",
        "- Level = `min(5, floor(passed_checks/2))` across 11 rubric checks.",
        f"- MVP threshold: >70% at L3+ and >50% at L4+ across `{len(MVP_SKILLS)}` skills.",
        "- High-risk critical MVP threshold: every tagged skill must be L5.",
        "",
        "## Threshold results",
        f"- MVP L3+: {summary['mvp_l3_pct']:.1f}% ({summary['mvp_l3_count']}/{summary['mvp_total']})",
        f"- MVP L4+: {summary['mvp_l4_pct']:.1f}% ({summary['mvp_l4_count']}/{summary['mvp_total']})",
        f"- High-risk critical MVP at L5: {summary['critical_l5_count']}/{summary['critical_total']}",
        "",
        "## Skill-level results",
        "| Skill | Level | MVP | High-risk critical MVP | Missing Criteria |",
        "|---|---:|---:|---:|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['id']}` | {row['level']} | {'yes' if row['is_mvp'] else 'no'} | {'yes' if row['is_high_risk_critical_mvp'] else 'no'} | {', '.join(row['missing']) or '-'} |"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", default="reports/skill_maturity_report.md")
    args = ap.parse_args()
    root = Path(args.root)

    rows = [eval_skill(d) for d in sorted((root / "skills").iterdir()) if d.is_dir() and (d / "SKILL.md").exists()]
    mvp_rows = [r for r in rows if r["is_mvp"]]
    crit_rows = [r for r in rows if r["is_high_risk_critical_mvp"]]

    mvp_total = len(mvp_rows)
    mvp_l3_count = sum(1 for r in mvp_rows if r["level"] >= 3)
    mvp_l4_count = sum(1 for r in mvp_rows if r["level"] >= 4)
    critical_l5_count = sum(1 for r in crit_rows if r["level"] == 5)

    summary = {
        "mvp_total": mvp_total,
        "mvp_l3_count": mvp_l3_count,
        "mvp_l4_count": mvp_l4_count,
        "mvp_l3_pct": (100.0 * mvp_l3_count / mvp_total) if mvp_total else 0.0,
        "mvp_l4_pct": (100.0 * mvp_l4_count / mvp_total) if mvp_total else 0.0,
        "critical_total": len(crit_rows),
        "critical_l5_count": critical_l5_count,
    }
    write_report(root / args.report, rows, summary)

    failures = []
    if summary["mvp_l3_pct"] <= 70.0:
        failures.append("MVP level-3+ threshold failed (must be >70%).")
    if summary["mvp_l4_pct"] <= 50.0:
        failures.append("MVP level-4+ threshold failed (must be >50%).")
    if summary["critical_l5_count"] != summary["critical_total"]:
        failures.append("High-risk critical MVP threshold failed (all must be level 5).")
    if failures:
        print("\n".join(failures))
        return 1
    print(f"Skill maturity report generated: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
