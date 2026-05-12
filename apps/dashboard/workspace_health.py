from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class ActionContext:
    actor_id: str
    workspace_id: str
    conversation_id: str
    message_id: str
    permissions: set[str]


def _event(action: str, status: str, context: ActionContext, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "event_type": "assistant.action",
        "action": action,
        "status": status,
        "actor_id": context.actor_id,
        "workspace_id": context.workspace_id,
        "conversation_id": context.conversation_id,
        "message_id": context.message_id,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }


def route_action(action: str, context: ActionContext, payload: dict[str, Any]) -> dict[str, Any]:
    permissions = {
        "view_workspace_health": "workspace.read",
    }
    required = permissions.get(action)
    if not required:
        return {"ok": False, "event": _event(action, "rejected", context, {"reason": "unknown_action"})}
    if required not in context.permissions:
        return {"ok": False, "event": _event(action, "rejected", context, {"reason": "missing_permission", "required": required})}
    return {"ok": True, "event": _event(action, "executed", context, {"payload_keys": sorted(payload.keys())})}
