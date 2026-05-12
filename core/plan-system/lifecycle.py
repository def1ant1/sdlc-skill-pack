from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


VALID_TRANSITIONS: dict[str, set[str]] = {
    "draft": {"in_review", "archived"},
    "in_review": {"draft", "approved", "archived"},
    "approved": {"archived"},
    "archived": set(),
}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class PlanLifecycleManager:
    data: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        if not self.data:
            now = _utc_now()
            self.data = {
                "id": "plan-draft",
                "title": "Untitled Plan",
                "status": "draft",
                "version": 1,
                "created_at": now,
                "updated_at": now,
                "objectives": [],
                "phases": [],
                "skills": [],
                "cost_assumptions": {},
                "history": [],
            }
        self._ensure_history_seed()

    def _ensure_history_seed(self) -> None:
        if not self.data.get("history"):
            self.data["history"] = [{
                "event": "plan.created",
                "version": self.data["version"],
                "timestamp": self.data["created_at"],
                "snapshot": copy.deepcopy(self.data),
            }]

    @property
    def plan_id(self) -> str:
        return self.data["id"]

    @property
    def title(self) -> str:
        return self.data.get("title", "Untitled Plan")

    @property
    def status(self) -> str:
        return self.data.get("status", "draft")

    @property
    def current_version(self) -> int:
        return int(self.data.get("version", 1))

    @property
    def objectives(self) -> list[str]:
        return self.data.get("objectives", [])

    @property
    def phases(self) -> list[dict[str, Any]]:
        return self.data.get("phases", [])

    @property
    def cost_assumptions(self) -> dict[str, Any]:
        return self.data.get("cost_assumptions", {})

    @property
    def history(self) -> list[dict[str, Any]]:
        return self.data.get("history", [])

    def _record_event(self, event: str, **payload: Any) -> None:
        self.data["history"].append({
            "event": event,
            "version": self.current_version,
            "timestamp": _utc_now(),
            **payload,
        })

    def update_plan(self, **fields: Any) -> None:
        self.data.update(fields)
        self.data["version"] = self.current_version + 1
        self.data["updated_at"] = _utc_now()
        self._record_event("plan.revised", snapshot=copy.deepcopy(self.data))

    def transition(self, new_status: str) -> None:
        current = self.status
        if new_status == current:
            return
        if new_status not in VALID_TRANSITIONS.get(current, set()):
            raise ValueError(f"invalid status transition: {current} -> {new_status}")
        self.data["status"] = new_status
        self.data["version"] = self.current_version + 1
        self.data["updated_at"] = _utc_now()
        self._record_event("plan.status_changed", from_status=current, to_status=new_status)
