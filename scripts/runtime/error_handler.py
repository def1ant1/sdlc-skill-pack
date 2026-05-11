"""Error handling and operator remediation mapping."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from error_types import ErrorCategory, RuntimeErrorBase


REMEDIATION_MAP: dict[ErrorCategory, str] = {
    ErrorCategory.VALIDATION: "Fix invalid payload/plan fields before rerun.",
    ErrorCategory.CONFIG: "Correct environment/config values and rerun.",
    ErrorCategory.AUTH: "Refresh credentials or permissions, then retry.",
    ErrorCategory.NETWORK: "Check connectivity/service health; safe to retry.",
    ErrorCategory.RATE_LIMIT: "Reduce request rate or wait for quota reset.",
    ErrorCategory.TIMEOUT: "Increase timeout or reduce workload size.",
    ErrorCategory.DEPENDENCY: "Validate dependent service status and versions.",
    ErrorCategory.CONNECTOR: "Inspect connector settings and upstream API changes.",
    ErrorCategory.CONFLICT: "Resolve concurrent update conflict before retry.",
    ErrorCategory.SIDE_EFFECT: "Require human approval; avoid automatic retries.",
    ErrorCategory.CANCELLED: "Review cancellation reason and resume from checkpoint if needed.",
    ErrorCategory.UNKNOWN: "Inspect logs and escalate with error context.",
}


@dataclass(slots=True)
class HandledError:
    category: ErrorCategory
    message: str
    retryable: bool
    remediation: str
    details: dict[str, Any] | None = None


def to_handled_error(exc: Exception) -> HandledError:
    if isinstance(exc, RuntimeErrorBase):
        category = exc.category
        message = exc.message
        retryable = exc.retryable
        details = exc.details
    else:
        category = ErrorCategory.UNKNOWN
        message = str(exc)
        retryable = False
        details = None

    return HandledError(
        category=category,
        message=message,
        retryable=retryable,
        remediation=REMEDIATION_MAP.get(category, REMEDIATION_MAP[ErrorCategory.UNKNOWN]),
        details=details,
    )
