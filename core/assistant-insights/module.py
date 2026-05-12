from __future__ import annotations

from typing import Any

from core.ui_p0_common import P0OperationContext, apply_reversible_update, enforce_policy

SCHEMA = {
    "module": "assistant_insights",
    "required": ["id", "status", "updated_at"],
    "status_values": ["pending", "active", "completed", "failed"],
}


def validate_schema(payload: dict[str, Any]) -> list[str]:
    errs=[]
    for key in SCHEMA["required"]:
        if key not in payload:
            errs.append(f"missing: {key}")
    if "status" in payload and payload["status"] not in SCHEMA["status_values"]:
        errs.append("invalid status")
    return errs


def qa_check(payload: dict[str, Any], interaction: dict[str, Any]) -> list[str]:
    errs=validate_schema(payload)
    if interaction.get("event") != "submit":
        errs.append("ui interaction must be submit")
    return errs


def process_action(state: dict[str, Any], payload: dict[str, Any], interaction: dict[str, Any], ctx: P0OperationContext) -> dict[str, Any]:
    enforce_policy("assistant_insights", payload)
    issues=qa_check(payload, interaction)
    if issues:
        raise ValueError("; ".join(issues))
    new_state,_ = apply_reversible_update(state, payload)
    ctx.log("assistant_insights", "process_action", {"payload": payload, "interaction": interaction})
    return new_state
