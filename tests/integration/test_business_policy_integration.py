from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent.parent


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def _validate_required_fields(instance: dict, schema: dict) -> None:
    for field in schema.get("required", []):
        assert field in instance, f"Missing required field: {field}"


def _validate_enum_constraints(instance: dict, schema: dict) -> None:
    properties = schema.get("properties", {})
    for key, rules in properties.items():
        if key not in instance:
            continue
        if "enum" in rules:
            assert instance[key] in rules["enum"], f"Invalid enum value for {key}: {instance[key]}"
        if "const" in rules:
            assert instance[key] == rules["const"], f"Invalid const value for {key}: {instance[key]}"
        if rules.get("type") == "object" and isinstance(instance[key], dict):
            _validate_required_fields(instance[key], rules)
            _validate_enum_constraints(instance[key], rules)


def validate_against_schema(instance: dict, schema: dict) -> None:
    _validate_required_fields(instance, schema)
    _validate_enum_constraints(instance, schema)


def evaluate_policy(policy: dict, context: dict) -> tuple[bool, dict]:
    blocked = False
    violations: list[str] = []
    for rule in policy.get("rules", []):
        if rule["condition"] == "amount_gt_10000" and context.get("amount", 0) > 10000:
            action = rule["action"]
            if action in {"emit_violation", "block", "require_approval"}:
                violations.append(rule["rule_id"])
            if action in {"block", "require_approval"}:
                blocked = True

    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "business_policy.violation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "actor": {"actor_id": "system", "actor_type": "service", "display_name": "Policy Engine"},
        "source": "business-policy-engine",
        "confidence": 1.0,
        "lineage": {"correlation_id": "corr-001", "causation_id": "cause-001", "parent_event_ids": []},
        "policy_context": {
            "policy_id": policy["policy_id"],
            "policy_version": policy["version"],
            "evaluation_result": "fail" if violations else "pass",
            "violations": violations,
        },
        "payload": {"amount": context.get("amount"), "blocked": blocked},
    }
    return blocked, event


def _trigger_external_side_effect(amount: int, blocked: bool, approval_decision: str | None) -> bool:
    if blocked and approval_decision != "approve":
        return False
    return amount > 0


def test_policy_violation_event_and_side_effect_blocked_pending_approval():
    policy_schema = _load(REPO_ROOT / "schemas" / "business-policy.schema.json")
    event_schema = _load(REPO_ROOT / "schemas" / "events" / "business_policy_violation.schema.json")

    policy_instance = {
        "policy_id": "pol-001",
        "name": "High value transfer check",
        "version": "1.0.0",
        "status": "active",
        "scope": {"entities": ["payment"], "events": ["invoice.created"]},
        "rules": [{"rule_id": "r1", "condition": "amount_gt_10000", "action": "require_approval", "severity": "high"}],
        "enforcement": {"mode": "enforced", "owner": "finance"},
    }

    validate_against_schema(policy_instance, policy_schema)

    blocked, event = evaluate_policy(policy_instance, {"amount": 12000})

    validate_against_schema(event, event_schema)
    assert blocked is True
    assert event["policy_context"]["violations"] == ["r1"]
    assert _trigger_external_side_effect(amount=12000, blocked=blocked, approval_decision=None) is False


def test_approved_flow_allows_external_side_effect_after_policy_gate():
    blocked, _ = evaluate_policy(
        {
            "policy_id": "pol-002",
            "name": "High value transfer check",
            "version": "1.0.0",
            "status": "active",
            "scope": {"entities": ["payment"], "events": ["invoice.created"]},
            "rules": [{"rule_id": "r1", "condition": "amount_gt_10000", "action": "require_approval", "severity": "high"}],
            "enforcement": {"mode": "enforced", "owner": "finance"},
        },
        {"amount": 12500},
    )

    assert blocked is True
    assert _trigger_external_side_effect(amount=12500, blocked=blocked, approval_decision="approve") is True
