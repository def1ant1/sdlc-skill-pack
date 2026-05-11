"""Category-aware retry policies with exponential backoff, jitter, and caps."""
from __future__ import annotations

import random
import time
from dataclasses import dataclass
from typing import Callable, TypeVar

from error_types import ErrorCategory, RuntimeErrorBase, TimeoutFailure

T = TypeVar("T")


@dataclass(slots=True)
class RetryDecision:
    should_retry: bool
    delay_seconds: float = 0.0
    reason: str = ""


@dataclass(slots=True)
class RetryPolicy:
    max_attempts: int = 5
    base_delay_seconds: float = 0.5
    max_delay_seconds: float = 30.0
    jitter_ratio: float = 0.2

    def _exponential_backoff(self, attempt: int) -> float:
        raw = min(self.max_delay_seconds, self.base_delay_seconds * (2 ** max(0, attempt - 1)))
        jitter = raw * self.jitter_ratio
        return max(0.0, raw + random.uniform(-jitter, jitter))

    def decide(self, exc: Exception, attempt: int, dry_run: bool = False) -> RetryDecision:
        if attempt >= self.max_attempts:
            return RetryDecision(False, reason="max attempts reached")

        if not isinstance(exc, RuntimeErrorBase):
            return RetryDecision(False, reason="untyped exception")

        if dry_run and not exc.dry_run_safe:
            return RetryDecision(False, reason="dry-run safety policy")

        if exc.high_risk_side_effect:
            return RetryDecision(False, reason="high-risk side effect")

        if not exc.retryable:
            return RetryDecision(False, reason=f"non-retryable category {exc.category.value}")

        delay = self._exponential_backoff(attempt)
        return RetryDecision(True, delay_seconds=delay, reason=f"retryable category {exc.category.value}")


def execute_with_retry(fn: Callable[[], T], policy: RetryPolicy | None = None, *, dry_run: bool = False, timeout_seconds: float | None = None) -> T:
    policy = policy or RetryPolicy()
    attempt = 1
    started = time.monotonic()
    while True:
        try:
            if timeout_seconds is not None and time.monotonic() - started > timeout_seconds:
                raise TimeoutFailure(f"Operation timed out after {timeout_seconds}s")
            return fn()
        except Exception as exc:  # noqa: BLE001
            decision = policy.decide(exc, attempt=attempt, dry_run=dry_run)
            if not decision.should_retry:
                raise
            time.sleep(decision.delay_seconds)
            attempt += 1
