#!/usr/bin/env python3
from __future__ import annotations

import datetime
import hashlib
import json
from pathlib import Path

from scripts.runtime.error_envelope import build_error_envelope

SHARED_SKILLS: dict[str, dict] = {
    "finance-operations": {"domain": "finance", "signals": ["finance", "budget", "forecast", "cash", "expense", "invoice", "ap/ar", "close", "variance"]},
    "procurement-operations": {"domain": "procurement", "signals": ["procurement", "vendor", "supplier", "sourcing", "purchase", "po", "contract", "rfx"]},
    "customer-operations": {"domain": "customer", "signals": ["customer", "support", "onboarding", "retention", "churn", "csat", "crm", "ticket"]},
    "inventory-operations": {"domain": "inventory", "signals": ["inventory", "stock", "warehouse", "replenishment", "sku", "safety stock", "fulfillment"]},
    "hr-operations": {"domain": "hr", "signals": ["hr", "hiring", "headcount", "payroll", "workforce", "policy", "performance"]},
    "legal-operations": {"domain": "legal", "signals": ["legal", "compliance", "regulatory", "contract review", "terms", "risk", "privacy"]},
    "executive-reporting": {"domain": "reporting", "signals": ["report", "dashboard", "executive", "kpi", "board", "summary"]},
}
DOMAIN_DEFAULTS: dict[str, list[str]] = {
    "finance": ["finance-operations", "procurement-operations", "legal-operations", "executive-reporting"],
    "customer": ["customer-operations", "finance-operations", "legal-operations", "executive-reporting"],
    "inventory": ["inventory-operations", "procurement-operations", "finance-operations", "executive-reporting"],
    "business": ["finance-operations", "procurement-operations", "customer-operations", "inventory-operations", "hr-operations", "legal-operations", "executive-reporting"],
}
_APPROVAL_POLICIES: dict[str, dict] = {
    "finance-operations": {"approver_role": "finance-controller", "policy_tags": ["budget-control", "spend-authorization"]},
    "procurement-operations": {"approver_role": "procurement-manager", "policy_tags": ["vendor-governance", "third-party-risk"]},
    "hr-operations": {"approver_role": "hr-business-partner", "policy_tags": ["workforce-policy", "separation-of-duties"]},
    "legal-operations": {"approver_role": "legal-counsel", "policy_tags": ["regulatory-compliance", "contract-risk"]},
}

def route_objective(objective: str, domain: str) -> list[str]:
    lowered = objective.lower()
    selected = [name for name, meta in SHARED_SKILLS.items() if any(sig in lowered for sig in meta["signals"])]
    if not selected:
        return DOMAIN_DEFAULTS[domain]
    ordered = DOMAIN_DEFAULTS[domain]
    return [s for s in ordered if s in selected] or ordered

def _skill_exists(skill: str) -> bool:
    repo_root = Path(__file__).resolve().parents[2]
    return any((repo_root / prefix / skill / "SKILL.md").exists() for prefix in ("skills", "core"))

def _diagnose_routing(objective: str, routed: list[str]) -> dict:
    lowered = objective.strip().lower()
    signal_hits = {name: sum(1 for sig in meta["signals"] if sig in lowered) for name, meta in SHARED_SKILLS.items()}
    top = max(signal_hits.values()) if signal_hits else 0
    missing_required = sorted([s for s in routed if not _skill_exists(s)])
    return {
        "objective_non_empty": bool(objective.strip()),
        "selected_skills_exist": len(missing_required) == 0,
        "dependency_completeness": True,
        "ambiguous_routing": top > 0 and list(signal_hits.values()).count(top) > 1,
        "missing_required_skills": missing_required,
        "missing_optional_skills": [],
        "remediation": "Install or add missing skills before execution: " + ", ".join(missing_required) if missing_required else None,
        "warnings": [],
    }

def _governance_annotation(skill: str) -> dict:
    policy = _APPROVAL_POLICIES.get(skill)
    if not policy:
        return {"approval_required": False, "approver_role": None, "policy_tags": [], "reason": "No elevated governance policy mapped for this step."}
    return {"approval_required": True, "approver_role": policy["approver_role"], "policy_tags": policy["policy_tags"], "reason": "Step impacts controlled business processes and requires explicit approval."}

def build_domain_plan(objective: str, domain: str) -> dict:
    routed = route_objective(objective, domain)
    diagnostics = _diagnose_routing(objective, routed)
    if not diagnostics["objective_non_empty"]:
        envelope = build_error_envelope(correlation_id="corr-planner", workflow_run_id="n/a", skill="planner", step="plan", category="validation", retryable=False, user_action_required=True, message="Planner objective is empty.", technical_detail="Objective must not be empty.", root_cause_hint="Caller provided blank objective input.", remediation="Provide a non-empty objective and rerun planner.", source_exception="ValueError")
        raise ValueError(json.dumps(envelope, sort_keys=True))
    if diagnostics["missing_required_skills"]:
        envelope = build_error_envelope(correlation_id="corr-planner", workflow_run_id="n/a", skill="planner", step="skill_resolution", category="config", retryable=False, user_action_required=True, message="Planner could not resolve required skills.", technical_detail=f"Missing skills: {', '.join(diagnostics['missing_required_skills'])}", root_cause_hint="Required skills are not installed in skills/ or core/.", remediation=diagnostics["remediation"] or "Install missing skills and rerun planner.", source_exception="ValueError")
        raise ValueError(json.dumps(envelope, sort_keys=True))
    plan_id = f"{domain.upper()}-{datetime.date.today().strftime('%Y%m%d')}-{hashlib.sha1(f'{domain}:{objective.strip().lower()}'.encode()).hexdigest()[:8]}"
    skill_chain = [{"step": i, "skill": skill, "phase": SHARED_SKILLS[skill]["domain"], "depends_on": [routed[i - 2]] if i > 1 else [], "governance": _governance_annotation(skill)} for i, skill in enumerate(routed, start=1)]
    return {
        "plan_id": plan_id, "created": datetime.date.today().isoformat(), "planner": f"{domain}-workflow-planner", "objective": objective,
        "planning_contract": {"version": "1.0", "routed_domains": sorted({SHARED_SKILLS[s]["domain"] for s in routed}), "shared_skill_registry": list(SHARED_SKILLS.keys()), "schema": "workflow-plan@1.0"},
        "skill_chain": skill_chain,
        "governance_checks": [{"name": "policy-compliance-review", "owner": "legal-operations", "fail_action": "block"}, {"name": "separation-of-duties", "owner": "hr-operations", "fail_action": "escalate"}],
        "hitl_checkpoints": [{"checkpoint": "objective-approval", "required": True, "approver_role": "business-owner"}, {"checkpoint": "pre-execution-risk-review", "required": True, "approver_role": "risk-committee"}, {"checkpoint": "final-signoff", "required": True, "approver_role": "executive-sponsor"}],
        "next_action": {"skill": routed[0], "reason": "highest-priority routed skill"},
        "planner_diagnostics": diagnostics,
    }
