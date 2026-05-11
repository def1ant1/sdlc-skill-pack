from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "runtime"))

from error_handler import to_handled_error  # noqa: E402
from error_types import RateLimitFailure, TimeoutFailure  # noqa: E402
from retry_policy import execute_with_retry  # noqa: E402


def test_timeout_failure_retries_then_succeeds_deterministically():
    attempts = {"n": 0}

    def flaky():
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise TimeoutFailure("connector timed out")
        return "ok"

    assert execute_with_retry(flaky, dry_run=False) == "ok"
    assert attempts["n"] == 3


def test_rate_limit_failure_has_structured_remediation_fields():
    exc = RateLimitFailure("rate limited", details={"skill": "connector:hubspot"})
    env = to_handled_error(exc)

    assert env.category.value == "rate_limit"
    assert env.retryable is True
    assert "wait" in env.remediation.lower() or "rate" in env.remediation.lower()
