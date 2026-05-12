from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validate_workspace_state(state: dict[str, Any]) -> None:
    required = {"schema_version", "workspace", "conversations", "artifacts", "approvals", "execution_runs"}
    missing = required - set(state)
    if missing:
        raise ValueError(f"workspace state missing keys: {sorted(missing)}")
    workspace = state["workspace"]
    for key in ["workspace_id", "name", "created_at", "updated_at"]:
        if key not in workspace:
            raise ValueError(f"workspace missing required key: {key}")


def default_workspace_state(workspace_id: str = "default", name: str = "Default Workspace") -> dict[str, Any]:
    now = _utc_now()
    state = {
        "schema_version": "1.0.0",
        "workspace": {
            "workspace_id": workspace_id,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "active_conversation_id": None,
            "conversation_ids": [],
            "artifact_ids": [],
            "approval_ids": [],
            "execution_run_ids": [],
        },
        "conversations": [],
        "artifacts": [],
        "approvals": [],
        "execution_runs": [],
    }
    _validate_workspace_state(state)
    return state


def load_workspace_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return default_workspace_state()
    state = json.loads(path.read_text(encoding="utf-8"))
    _validate_workspace_state(state)
    return state


def save_workspace_state(path: Path, state: dict[str, Any]) -> None:
    state["workspace"]["updated_at"] = _utc_now()
    _validate_workspace_state(state)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")


def resume_session_from_workspace(session_state: Any, workspace: dict[str, Any]) -> None:
    active_id = workspace["workspace"].get("active_conversation_id")
    if not active_id:
        return
    for conv in workspace.get("conversations", []):
        if conv.get("session_id") == active_id:
            session_state.active_workspace_conversation = conv
            turn_state = conv.get("turn_state", {}) if isinstance(conv.get("turn_state"), dict) else {}
            for key, default in _turn_state_defaults().items():
                setattr(session_state, key, turn_state.get(key, default))
            break


def _turn_state_defaults() -> dict[str, Any]:
    return {
        "active_goal": "",
        "workflow_stage": "idle",
        "clarification_status": "not_started",
        "clarification_answer_map": {},
        "last_clarification_id": None,
        "completion_status": "incomplete",
    }


def snapshot_turn_state(session_state: Any) -> dict[str, Any]:
    defaults = _turn_state_defaults()
    snapshot: dict[str, Any] = {}
    for key, default in defaults.items():
        value = getattr(session_state, key, default)
        snapshot[key] = value if value is not None else default
    return snapshot


def append_audit_event(workspace: dict[str, Any], session_id: str, event_type: str,
                       payload: dict[str, Any] | None = None) -> None:
    event = {
        "event_type": event_type,
        "timestamp": _utc_now(),
        "payload": payload or {},
    }
    for conv in workspace.get("conversations", []):
        if conv.get("session_id") == session_id:
            conv.setdefault("timeline", []).append(event)
            conv["saved_at"] = _utc_now()
            return


def register_conversation(workspace: dict[str, Any], session_id: str, title: str | None = None, plan_id: str | None = None,
                          run_id: str | None = None, turn_state: dict[str, Any] | None = None) -> None:
    conv = {
        "session_id": session_id,
        "workspace_id": workspace["workspace"]["workspace_id"],
        "title": title,
        "plan_id": plan_id,
        "run_id": run_id,
        "turn_state": turn_state or _turn_state_defaults(),
        "timeline": [],
        "saved_at": _utc_now(),
    }
    workspace["conversations"] = [c for c in workspace["conversations"] if c.get("session_id") != session_id]
    workspace["conversations"].append(conv)
    ws = workspace["workspace"]
    ws["active_conversation_id"] = session_id
    ws["conversation_ids"] = sorted({*ws.get("conversation_ids", []), session_id})
    _validate_workspace_state(workspace)
