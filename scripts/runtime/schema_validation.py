from __future__ import annotations


def validate_structured_skill_output(payload: dict) -> None:
    required = {"status", "summary"}
    missing = sorted(required - set(payload.keys()))
    if missing:
        raise ValueError(f"Structured output missing required keys: {', '.join(missing)}")
