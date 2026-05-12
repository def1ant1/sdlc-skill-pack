from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class P0OperationContext:
    audit_log: list[dict[str, Any]] = field(default_factory=list)

    def log(self, module: str, action: str, payload: dict[str, Any], user: str = "system") -> None:
        self.audit_log.append(
            {
                "timestamp": utc_now(),
                "module": module,
                "action": action,
                "user": user,
                "payload": deepcopy(payload),
            }
        )


def enforce_policy(module: str, payload: dict[str, Any]) -> None:
    if payload.get("policy_blocked"):
        raise PermissionError(f"{module} action blocked by policy")


def apply_reversible_update(state: dict[str, Any], patch: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    before = deepcopy(state)
    state.update(patch)
    return state, before


def rollback_update(state: dict[str, Any], snapshot: dict[str, Any]) -> dict[str, Any]:
    state.clear()
    state.update(deepcopy(snapshot))
    return state
