from __future__ import annotations

import datetime as dt
import uuid
from typing import Any

CATEGORIES = {
    "validation", "config", "auth", "network", "rate_limit", "timeout", "dependency", "connector",
    "data_quality", "schema", "governance", "hitl", "model", "memory", "schedule", "runtime", "security", "unknown",
}


def build_error_envelope(*, correlation_id: str, workflow_run_id: str = "n/a", schedule_run_id: str = "n/a", skill: str,
                         step: int | str = "n/a", severity: str = "error", category: str = "unknown", retryable: bool = False,
                         user_action_required: bool = True, message: str, technical_detail: str = "", root_cause_hint: str = "",
                         remediation: str = "Review logs and retry after correcting configuration.", source_exception: str = "") -> dict[str, Any]:
    if category not in CATEGORIES:
        category = "unknown"
    return {
        "error_id": f"err-{uuid.uuid4().hex[:8]}",
        "correlation_id": correlation_id,
        "workflow_run_id": workflow_run_id or "n/a",
        "schedule_run_id": schedule_run_id or "n/a",
        "skill": skill,
        "step": step,
        "severity": severity,
        "category": category,
        "retryable": retryable,
        "user_action_required": user_action_required,
        "message": message,
        "technical_detail": technical_detail,
        "root_cause_hint": root_cause_hint,
        "remediation": remediation,
        "source_exception": source_exception,
        "created_at": dt.datetime.now(dt.timezone.utc).isoformat(),
    }
