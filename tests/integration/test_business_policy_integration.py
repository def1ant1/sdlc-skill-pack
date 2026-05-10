from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def evaluate_policy(policy: dict, context: dict) -> tuple[bool, dict]:
    blocked = False
    violations = []
    for rule in policy.get("rules", []):
        if rule["condition"] == "amount_gt_10000" and context.get("amount", 0) > 10000:
            action = rule["action"]
            if action in {"emit_violation", "block", "require_approval"}:
                violations.append(rule["rule_id"])
            if action in {"block", "require_approval"}:
                blocked = True
    event = {"event_type": "business_policy.violation", "policy_context": {"violations": violations}}
    return blocked, event


def test_policy_violation_event_and_side_effect_blocked_pending_approval():
    policy = _load(REPO_ROOT / "schemas" / "business-policy.schema.json")
    # minimal valid policy instance against modeled fields
    policy_instance = {
        "policy_id": "pol-001",
        "name": "High value transfer check",
        "version": "1.0.0",
        "status": "active",
        "scope": {"entities": ["payment"], "events": ["invoice.created"]},
        "rules": [{"rule_id": "r1", "condition": "amount_gt_10000", "action": "require_approval", "severity": "high"}],
        "enforcement": {"mode": "enforced", "owner": "finance"},
    }
    assert policy["title"] == "Business Policy"

    blocked, event = evaluate_policy(policy_instance, {"amount": 12000})

    assert blocked is True
    assert event["event_type"] == "business_policy.violation"
    assert event["policy_context"]["violations"] == ["r1"]
