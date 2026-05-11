from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import time

class QuotaPressure(str, Enum):
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRITICAL = "critical"

@dataclass(slots=True)
class QuotaBudget:
    limit: int
    remaining: int
    reset_epoch_seconds: int | None = None

@dataclass(slots=True)
class RateLimitPolicy:
    connector_id: str
    requests_per_minute: int
    daily_quota: int | None = None
    cache_ttl_seconds: int = 300
    degrade_to_cached_at: float = 0.15
    degrade_to_read_only_at: float = 0.05

class RateLimitManager:
    def __init__(self, policy: RateLimitPolicy):
        self.policy = policy
        self._minute_tokens = float(policy.requests_per_minute)
        self._last_refill = time.monotonic()
        self._daily_usage = 0

    def acquire(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_refill
        rpm = self.policy.requests_per_minute
        self._minute_tokens = min(rpm, self._minute_tokens + elapsed * (rpm / 60.0))
        self._last_refill = now
        if self._minute_tokens < 1.0:
            time.sleep(max(0.0, (1.0 - self._minute_tokens) * (60.0 / rpm)))
            self._minute_tokens = 0.0
        else:
            self._minute_tokens -= 1.0
        self._daily_usage += 1

    def pressure(self) -> QuotaPressure:
        if not self.policy.daily_quota:
            return QuotaPressure.NORMAL
        remaining = max(self.policy.daily_quota - self._daily_usage, 0)
        ratio = remaining / max(self.policy.daily_quota, 1)
        if ratio <= self.policy.degrade_to_read_only_at:
            return QuotaPressure.CRITICAL
        if ratio <= self.policy.degrade_to_cached_at:
            return QuotaPressure.ELEVATED
        return QuotaPressure.NORMAL

    def budget(self) -> QuotaBudget:
        if not self.policy.daily_quota:
            return QuotaBudget(limit=0, remaining=0)
        return QuotaBudget(limit=self.policy.daily_quota, remaining=max(self.policy.daily_quota - self._daily_usage, 0))
