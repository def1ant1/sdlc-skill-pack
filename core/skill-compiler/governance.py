"""Governance wrapper stubs."""

def wrap_with_governance(compiled_skill: dict) -> dict:
    payload = dict(compiled_skill)
    payload["governance"] = {
        "policy_checks": ["allowlist", "approval_gate"],
        "status": "stub",
    }
    return payload
