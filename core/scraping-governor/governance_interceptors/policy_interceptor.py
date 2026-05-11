from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(slots=True)
class InterceptDecision:
    allowed: bool
    reason: str
    evaluated_at: str


class SourcePolicyInterceptor:
    def evaluate(self, source_def: dict) -> InterceptDecision:
        legal = source_def.get("legal", {})
        robots = source_def.get("robots", {})
        tos = source_def.get("terms_of_service", {})
        throttling = source_def.get("throttling", {})

        if not legal.get("review_approved", False):
            return self._deny("legal review not approved")
        if not robots.get("allow_scraping", False):
            return self._deny("robots policy disallows scraping")
        if not tos.get("allow_automation", False):
            return self._deny("terms of service disallow automation")
        if throttling.get("max_requests_per_minute", 0) <= 0:
            return self._deny("invalid throttle configuration")

        return InterceptDecision(True, "compliant", self._now_iso())

    def _deny(self, reason: str) -> InterceptDecision:
        return InterceptDecision(False, reason, self._now_iso())

    @staticmethod
    def _now_iso() -> str:
        return datetime.now(timezone.utc).isoformat()
