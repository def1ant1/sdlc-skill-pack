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


def load_frontmatter(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3 : end + 1]) or {}


def has_boundary_language(text: str) -> bool:
    needles = ["do_not_use_when", "do not use when", "out of scope", "not supported", "boundary"]
    blob = text.lower()
    return any(n in blob for n in needles)


def eval_skill(skill_dir: Path) -> dict[str, Any]:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8")
    fm = load_frontmatter(skill_md)
    meta = fm.get("metadata") or {}

    manifest_name = meta.get("manifest")
    manifest_path = skill_dir / manifest_name if manifest_name else None
    manifest = None
    checks: dict[str, bool] = {}

    checks["manifest"] = bool(manifest_path and manifest_path.is_file())
    if checks["manifest"]:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            checks["manifest"] = False

    checks["skill_protocol"] = all(k in fm for k in ("name", "description", "use_when", "do_not_use_when"))

    checks["contracts"] = bool("input_contract" in text.lower() and "output_contract" in text.lower())
    if manifest:
        checks["contracts"] = checks["contracts"] or bool(manifest.get("input_contract") and manifest.get("output_contract"))

    checks["entities_events_refs"] = "entity" in text.lower() and "event" in text.lower()
    if manifest:
        checks["entities_events_refs"] = checks["entities_events_refs"] or bool(
            manifest.get("data_contracts") or manifest.get("telemetry_events")
        )

    checks["governance_refs"] = "governance" in text.lower() or bool(manifest and manifest.get("governance_level"))
    checks["hitl"] = "human" in text.lower() and "approval" in text.lower() or bool(
        manifest and manifest.get("human_approval_required") is not None
    )
    checks["telemetry"] = "telemetry" in text.lower() or bool(manifest and manifest.get("telemetry_events"))
    checks["eval"] = (skill_dir / "eval.spec.json").is_file() or "eval" in text.lower() or bool(manifest and manifest.get("eval_metrics"))
    checks["examples"] = (skill_dir / "examples").is_dir() or "example" in text.lower()
    checks["failure_modes"] = "failure" in text.lower() or bool(manifest and manifest.get("failure_modes"))
    checks["boundary_language"] = has_boundary_language(text)

    passed = sum(1 for v in checks.values() if v)
    level = min(5, passed // 2)

    tags = set(manifest.get("tags", []) if manifest else [])
    p0 = "p0" in tags
    critical = "critical" in tags

    return {
        "id": skill_dir.name,
        "level": level,
        "checks": checks,
        "missing": [k for k in RUBRIC_KEYS if not checks[k]],
        "p0": p0,
        "critical": critical,
        "manifest_path": str(manifest_path) if manifest_path else None,
    }


def write_report(path: Path, rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Skill Maturity Report",
        "",
        "Rubric checks: " + ", ".join(RUBRIC_KEYS),
        "",
        "| Skill | Level | Tags | Missing Criteria |",
        "|---|---:|---|---|",
    ]
    for row in rows:
        tags = ", ".join([t for t, ok in (("P0", row["p0"]), ("critical", row["critical"])) if ok]) or "-"
        missing = ", ".join(row["missing"]) or "-"
        lines.append(f"| `{row['id']}` | {row['level']} | {tags} | {missing} |")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--report", default="reports/skill_maturity_report.md")
    args = ap.parse_args()

    root = Path(args.root)
    rows = []
    missing_tag_meta = []
    for skill_dir in sorted((root / "skills").iterdir()):
        if skill_dir.is_dir() and (skill_dir / "SKILL.md").exists():
            row = eval_skill(skill_dir)
            rows.append(row)
            skill_md = skill_dir / 'SKILL.md'
            fm = load_frontmatter(skill_md)
            priority = str(fm.get('priority') or (fm.get('metadata') or {}).get('priority') or '').upper()
            expected_p0 = priority == 'P0'
            expected_critical = bool((fm.get('metadata') or {}).get('critical'))
            if row['manifest_path'] and ((expected_p0 and not row['p0']) or (expected_critical and not row['critical'])):
                missing_tag_meta.append(row['id'])

    write_report(root / args.report, rows)

    failures = []
    for row in rows:
        if row["p0"] and row["level"] < 4:
            failures.append(f"{row['id']}: P0 must be >=4 (actual {row['level']})")
        if row["critical"] and row["level"] != 5:
            failures.append(f"{row['id']}: critical must be 5 (actual {row['level']})")

    if missing_tag_meta:
        failures.append(
            "rubric metadata missing manifest tags (expected tags include 'p0' and/or 'critical' where applicable): "
            + ", ".join(missing_tag_meta)
        )

    if failures:
        print("\n".join(failures))
        return 1

    print(f"Skill maturity report generated: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
