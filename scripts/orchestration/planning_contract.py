#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
POLICY_REFS = [
    "references/business-policy-standard.md",
    "references/semantic-cache-policy.md",
]
DOMAIN_DEFAULTS: dict[str, list[str]] = {
    "business": ["business-orchestration", "governance", "audit-trail"],
    "customer": ["meeting-intelligence", "business-orchestration", "governance"],
    "finance": ["billing-runtime", "business-policy-engine", "audit-trail"],
    "inventory": ["master-data-management", "business-orchestration", "audit-trail"],
    "legal": ["compliance-runtime", "governance", "business-policy-engine"],
    "data-security": ["sandbox-execution", "policy-engine", "compliance-runtime"],
}


def _load_skill_inventory(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {row.get("id", "") for row in data if isinstance(row, dict)}


def _load_skill_graph(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {n.get("name", "") for n in data.get("nodes", []) if isinstance(n, dict)}


def build_domain_plan(objective: str, domain: str, *, dry_run: bool, inventory_path: Path, graph_path: Path) -> dict:
    if not objective.strip():
        raise ValueError("objective is required")
    if domain not in DOMAIN_DEFAULTS:
        raise ValueError(f"unsupported domain: {domain}")

    missing_inputs = [str(p) for p in (inventory_path, graph_path) if not p.exists()]
    if missing_inputs:
        raise ValueError(
            "missing skill metadata inputs: " + ", ".join(missing_inputs) +
            ". Generate them with scripts/generate_skill_inventory.py and scripts/skills/build_skill_graph.py"
        )

    inventory_skills = _load_skill_inventory(inventory_path)
    graph_skills = _load_skill_graph(graph_path)
    required = DOMAIN_DEFAULTS[domain]
    missing_from_inventory = sorted([s for s in required if s not in inventory_skills])
    missing_from_graph = sorted([s for s in required if s not in graph_skills])
    missing = sorted(set(missing_from_inventory + missing_from_graph))
    if missing:
        raise ValueError(
            "required skills unavailable. "
            f"missing_in_inventory={missing_from_inventory}; missing_in_graph={missing_from_graph}; "
            "install/add skills and regenerate reports."
        )

    created = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    steps = []
    for i, skill in enumerate(required, start=1):
        sid = f"{domain.replace('-', '')}-{i}"
        steps.append({
            "id": sid,
            "order": i,
            "title": f"Run {skill}",
            "skill": skill,
            "depends_on": [steps[-1]["id"]] if steps else [],
            "governance_policy_refs": POLICY_REFS,
            "outputs": [f"reports/{domain}-{skill}-output.json"],
        })

    return {
        "id": "sample-sdlc-plan",
        "description": f"Auto-generated {domain} workflow plan",
        "objectives": [objective.strip()],
        "steps": steps,
        "governance_gates": [
            {"id": "gate-policy", "policy_ref": "references/business-policy-standard.md", "enforcement": "blocking"},
            {"id": "gate-docs", "policy_ref": "docs/standards/documentation-governance.md", "enforcement": "advisory"},
        ],
        "dry_run_safety": {
            "enabled": dry_run,
            "no_external_writes": True,
            "require_human_approval_for_mutations": True,
        },
        "deterministic_artifacts": [
            {"name": "workflow-plan", "path": "reports/generated-workflow-plan.json", "format": "json"}
        ],
        "planner_metadata": {"planner": f"{domain}-workflow-planner", "version": "1.0.0", "created_at": created},
    }


def run_planner_cli(domain: str) -> int:
    p = argparse.ArgumentParser(description=f"Generate {domain} workflow plan")
    p.add_argument("objective", nargs="?", help="Objective text")
    p.add_argument("--stdin", action="store_true", help="Read objective from stdin")
    p.add_argument("--dry-run", action="store_true", required=True, help="Required safety flag")
    p.add_argument("--json", action="store_true", required=True, help="Emit JSON output")
    p.add_argument("--output", type=Path, required=True, help="Output path for plan JSON")
    p.add_argument("--inventory", type=Path, default=ROOT / "reports" / "skill_inventory.json")
    p.add_argument("--graph", type=Path, default=ROOT / "reports" / "skill_graph.json")
    a = p.parse_args()

    objective = (Path("-").read_text() if False else "")
    objective = a.objective if a.objective else ""
    if a.stdin or not a.objective:
        import sys
        objective = sys.stdin.read().strip()
    try:
        plan = build_domain_plan(objective, domain, dry_run=a.dry_run, inventory_path=a.inventory, graph_path=a.graph)
    except ValueError as exc:
        import sys
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    if a.json:
        print(json.dumps(plan, indent=2, sort_keys=True))
    return 0
