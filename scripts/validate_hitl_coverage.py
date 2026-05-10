#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path.cwd()
SKILL_DIRS = ("core", "skills", "agents")
REPORT_PATH = ROOT / "reports" / "hitl_coverage_report.md"
REQUIRED_DOMAINS = [
    "finance",
    "hr",
    "legal",
    "procurement",
    "customer-comm",
    "deployment",
    "security",
    "external-mutation",
]

DOMAIN_PATTERNS = {
    "finance": ["finance", "budget", "invoice", "accounting", "revenue", "cash", "fpa"],
    "hr": ["hr", "hiring", "recruit", "payroll", "people-ops", "talent"],
    "legal": ["legal", "contract", "nda", "policy", "regulatory", "compliance"],
    "procurement": ["procurement", "vendor", "purchase", "sourcing"],
    "customer-comm": ["customer", "support", "success", "communication", "external message"],
    "deployment": ["deploy", "release", "production", "infrastructure", "sre", "devsecops"],
    "security": ["security", "vuln", "threat", "incident", "soc2", "auth"],
    "external-mutation": ["write", "update", "delete", "send", "publish", "mutate", "sync"],
}


def parse_frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    return yaml.safe_load(text[3 : end + 1]) or {}


def iter_skills() -> list[dict]:
    rows: list[dict] = []
    for parent in SKILL_DIRS:
        base = ROOT / parent
        if not base.exists():
            continue
        for child in sorted(base.iterdir(), key=lambda p: p.name):
            skill = child / "SKILL.md"
            if child.is_dir() and skill.exists():
                fm = parse_frontmatter(skill)
                body = skill.read_text(encoding="utf-8").lower()
                gates = fm.get("hitl_gates") or []
                if isinstance(gates, dict):
                    gates = [gates]
                rows.append({
                    "id": child.name,
                    "path": str(skill.relative_to(ROOT)),
                    "frontmatter": fm,
                    "body": body,
                    "gates": [g for g in gates if isinstance(g, dict)],
                })
    return rows


def infer_risk(skill: dict) -> str:
    blob = f"{skill['id']} {skill['body']}"
    if any(k in blob for k in ["critical", "level-3", "l3", "always required"]):
        return "L3"
    if any(k in blob for k in ["high", "l2", "approval", "human review"]):
        return "L2"
    return "L1"


def gate_covers_required_fields(gate: dict) -> bool:
    return all(gate.get(k) for k in ["risk_tier", "approval_trigger", "approver_role", "action_scope"])


def gate_exists(skill: dict, target: str) -> bool:
    for gate in skill["gates"]:
        tier = str(gate.get("risk_tier", "")).lower()
        if target.lower() in tier and gate_covers_required_fields(gate):
            return True
    return False


def covers_domain(skill: dict, domain: str) -> bool:
    blob = f"{skill['id']} {skill['body']}"
    return any(p in blob for p in DOMAIN_PATTERNS[domain])


def main() -> int:
    skills = iter_skills()
    l3 = [s for s in skills if infer_risk(s) == "L3"]
    l2 = [s for s in skills if infer_risk(s) == "L2"]

    l3_cov = [s for s in l3 if gate_exists(s, "l3") or gate_exists(s, "critical")]
    l2_cov = [s for s in l2 if gate_exists(s, "l2") or gate_exists(s, "high")]

    l3_ratio = (len(l3_cov) / len(l3) * 100) if l3 else 100.0
    l2_ratio = (len(l2_cov) / len(l2) * 100) if l2 else 100.0

    domain_rows = {}
    domain_failures = []
    for domain in REQUIRED_DOMAINS:
        in_domain = [s for s in skills if covers_domain(s, domain)]
        covered = [s for s in in_domain if s["gates"] and any(gate_covers_required_fields(g) for g in s["gates"])]
        ratio = (len(covered) / len(in_domain) * 100) if in_domain else 0.0
        domain_rows[domain] = (len(covered), len(in_domain), ratio)
        if ratio < 100.0:
            domain_failures.append((domain, in_domain, covered))

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# HITL Coverage Report",
        "",
        "## Policy Gates",
        f"- L3/critical HITL coverage: **{l3_ratio:.2f}%** (required: 100%)",
        f"- L2/high-risk HITL coverage: **{l2_ratio:.2f}%** (required: >=95%)",
        "",
        "## Required Domain Coverage",
    ]
    for d, (c, t, r) in domain_rows.items():
        lines.append(f"- {d}: **{c}/{t}** ({r:.2f}%)")

    lines += ["", "## Per-skill Exceptions"]
    l3_missing = [s for s in l3 if s not in l3_cov]
    l2_missing = [s for s in l2 if s not in l2_cov]
    if not l3_missing and not l2_missing and not domain_failures:
        lines.append("- None")
    else:
        for s in l3_missing:
            lines.append(f"- `{s['id']}`: missing compliant L3/critical HITL metadata gate")
        for s in l2_missing:
            lines.append(f"- `{s['id']}`: missing compliant L2/high-risk HITL metadata gate")
        for d, in_domain, covered in domain_failures:
            missing_ids = sorted({s["id"] for s in in_domain if s not in covered})[:20]
            if missing_ids:
                lines.append(f"- `{d}` domain missing HITL metadata on: {', '.join(f'`{x}`' for x in missing_ids)}")

    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")

    failed = l3_ratio < 100.0 or l2_ratio < 95.0 or bool(domain_failures)
    print(json.dumps({"l3_ratio": l3_ratio, "l2_ratio": l2_ratio, "domain_failures": [d for d, _, _ in domain_failures], "report": str(REPORT_PATH.relative_to(ROOT))}, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
