"""Telemetry and limits stubs."""

def attach_telemetry(compiled_skill: dict) -> dict:
    payload = dict(compiled_skill)
    payload["telemetry"] = {
        "rate_limit_per_minute": 120,
        "estimated_cost_usd": 0.0,
        "events": ["compile.started", "compile.completed"],
    }
    return payload
