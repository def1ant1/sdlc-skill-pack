"""
app/billing/quota.py — Per-org concurrent workflow quota enforcement.

Plan tiers and their limits:
  free:       1 concurrent workflow,   10K tokens/day
  starter:    3 concurrent workflows,  100K tokens/day
  pro:        10 concurrent workflows, 1M tokens/day
  enterprise: unlimited
"""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger("apotheon.quota")

PLAN_LIMITS: dict[str, dict] = {
    "free":       {"max_concurrent": 1,   "daily_tokens": 10_000},
    "starter":    {"max_concurrent": 3,   "daily_tokens": 100_000},
    "pro":        {"max_concurrent": 10,  "daily_tokens": 1_000_000},
    "enterprise": {"max_concurrent": 999, "daily_tokens": 999_000_000},
}

DEFAULT_PLAN = "starter"


@dataclass
class QuotaStatus:
    allowed: bool
    reason: str = ""
    current_concurrent: int = 0
    max_concurrent: int = 0
    plan_tier: str = ""


class QuotaEnforcer:
    """
    Check and enforce per-org quotas against the database.

    Usage:
        enforcer = QuotaEnforcer(db, org_id, plan_tier)
        status = await enforcer.check_concurrent()
        if not status.allowed:
            raise HTTPException(429, status.reason)
    """

    def __init__(self, db, org_id: str, plan_tier: str = DEFAULT_PLAN):
        self._db = db
        self._org_id = org_id
        self._plan_tier = plan_tier
        self._limits = PLAN_LIMITS.get(plan_tier, PLAN_LIMITS[DEFAULT_PLAN])

    async def check_concurrent(self) -> QuotaStatus:
        """Return QuotaStatus for concurrent workflow limit."""
        max_c = self._limits["max_concurrent"]
        try:
            from app.db.repositories.workflow_repository import WorkflowRepository
            repo = WorkflowRepository(self._db, self._org_id)
            current = await repo.count_running()
        except Exception as exc:
            logger.warning("Quota check DB error: %s — allowing by default", exc)
            return QuotaStatus(allowed=True, reason="quota_check_skipped", plan_tier=self._plan_tier)

        if current >= max_c:
            return QuotaStatus(
                allowed=False,
                reason=f"Concurrent workflow limit reached ({current}/{max_c}) for plan '{self._plan_tier}'",
                current_concurrent=current,
                max_concurrent=max_c,
                plan_tier=self._plan_tier,
            )
        return QuotaStatus(
            allowed=True,
            current_concurrent=current,
            max_concurrent=max_c,
            plan_tier=self._plan_tier,
        )

    def token_budget(self) -> int:
        """Return daily token budget for this plan."""
        return self._limits["daily_tokens"]