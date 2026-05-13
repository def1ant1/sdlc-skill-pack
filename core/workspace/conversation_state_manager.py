from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

DEFAULT_SCHEMA_VERSION = "1.0.0"

_REQUIRED_DEFAULTS: dict[str, Any] = {
    "active_goal": "",
    "intent": "",
    "intent_confidence": 0.0,
    "workflow_stage": "intake",
    "completed_steps": [],
    "pending_steps": [],
    "execution_status": "idle",
    "delivery_status": "pending",
    "artifact_generated": False,
    "final_response_synthesized": False,
    "workflow_complete": False,
    "completion_reason": "",
    "clarification_resolved": False,
    "memory_summary": "",
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ConversationStateManager:
    """Read/merge/write lifecycle for conversation state with version metadata."""

    schema_version: str = DEFAULT_SCHEMA_VERSION

    def create(self, initial_state: dict[str, Any] | None = None) -> dict[str, Any]:
        base = {
            "version": 1,
            "schema_version": self.schema_version,
            "updated_at": _utc_now(),
            **deepcopy(_REQUIRED_DEFAULTS),
        }
        if initial_state:
            base = self.merge(base, initial_state, bump_version=False)
        return base

    def read(self, state: dict[str, Any] | None) -> dict[str, Any]:
        if not state:
            return self.create()
        hydrated = deepcopy(state)
        for field, default in _REQUIRED_DEFAULTS.items():
            hydrated.setdefault(field, deepcopy(default))
        hydrated.setdefault("schema_version", self.schema_version)
        hydrated.setdefault("version", 1)
        hydrated.setdefault("updated_at", _utc_now())
        return hydrated

    def merge(self, current_state: dict[str, Any] | None, patch: dict[str, Any], bump_version: bool = True) -> dict[str, Any]:
        merged = self.read(current_state)
        for key, value in patch.items():
            if value is not None:
                merged[key] = deepcopy(value)
        if bump_version:
            merged["version"] = int(merged.get("version", 1)) + 1
        merged["updated_at"] = _utc_now()
        return merged

    def write(self, current_state: dict[str, Any] | None, patch: dict[str, Any]) -> dict[str, Any]:
        return self.merge(current_state, patch, bump_version=True)
