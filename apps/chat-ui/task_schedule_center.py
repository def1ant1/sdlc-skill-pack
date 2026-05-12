from __future__ import annotations

from typing import Any


def render_task_schedule_center(payload: dict[str, Any], interaction: dict[str, Any], qa_checker: Any) -> dict[str, Any]:
    issues = qa_checker(payload, interaction)
    return {"ok": not issues, "issues": issues, "payload": payload, "interaction": interaction}
