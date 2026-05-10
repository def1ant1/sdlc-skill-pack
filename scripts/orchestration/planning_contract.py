#!/usr/bin/env python3
from __future__ import annotations

import datetime
import uuid

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


def route_objective(objective: str, domain: str) -> list[str]:
    lowered = objective.lower()
    selected = [name for name, meta in SHARED_SKILLS.items() if any(sig in lowered for sig in meta["signals"])]
    if not selected:
        return DOMAIN_DEFAULTS[domain]
    ordered = DOMAIN_DEFAULTS[domain]
    return [s for s in ordered if s in selected] or ordered


def build_domain_plan(objective: str, domain: str) -> dict:
    routed = route_objective(objective, domain)
    plan_id = f"{domain.upper()}-{datetime.date.today().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    skill_chain = [{
        "step": i,
        "skill": skill,
        "phase": SHARED_SKILLS[skill]["domain"],
        "depends_on": [routed[i - 2]] if i > 1 else [],
    } for i, skill in enumerate(routed, start=1)]

    return {
        "plan_id": plan_id,
        "created": datetime.date.today().isoformat(),
        "planner": f"{domain}-workflow-planner",
        "objective": objective,
        "planning_contract": {
            "version": "1.0",
            "routed_domains": sorted({SHARED_SKILLS[s]["domain"] for s in routed}),
            "shared_skill_registry": list(SHARED_SKILLS.keys()),
        },
        "skill_chain": skill_chain,
        "governance_checks": [
            {"name": "policy-compliance-review", "owner": "legal-operations", "fail_action": "block"},
            {"name": "separation-of-duties", "owner": "hr-operations", "fail_action": "escalate"},
        ],
        "hitl_checkpoints": [
            {"checkpoint": "objective-approval", "required": True, "approver_role": "business-owner"},
            {"checkpoint": "pre-execution-risk-review", "required": True, "approver_role": "risk-committee"},
            {"checkpoint": "final-signoff", "required": True, "approver_role": "executive-sponsor"},
        ],
        "next_action": {"skill": routed[0], "reason": "highest-priority routed skill"},
    }
