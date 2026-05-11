"""Per-org quota and budget threshold policy helpers."""
from __future__ import annotations

from dataclasses import dataclass

PLAN_LIMITS: dict[str, dict] = {
    "free": {"max_concurrent": 1, "daily_tokens": 10_000, "daily_budget_usd": 2.0, "warn_pct": 0.8, "block_pct": 1.0},
    "starter": {"max_concurrent": 3, "daily_tokens": 100_000, "daily_budget_usd": 30.0, "warn_pct": 0.8, "block_pct": 1.0},
    "pro": {"max_concurrent": 10, "daily_tokens": 1_000_000, "daily_budget_usd": 300.0, "warn_pct": 0.85, "block_pct": 1.0},
    "enterprise": {"max_concurrent": 999, "daily_tokens": 999_000_000, "daily_budget_usd": 10_000.0, "warn_pct": 0.9, "block_pct": 1.0},
}
DEFAULT_PLAN = "starter"


@dataclass
class BudgetPolicyDecision:
    action: str
    estimated_run_cost_usd: float
    projected_total_usd: float
    budget_limit_usd: float
    message: str


def evaluate_budget_policy(consumed_usd: float, estimated_run_cost_usd: float, plan_tier: str = DEFAULT_PLAN) -> BudgetPolicyDecision:
    limits = PLAN_LIMITS.get(plan_tier, PLAN_LIMITS[DEFAULT_PLAN])
    budget = float(limits["daily_budget_usd"])
    warn = float(limits["warn_pct"])
    block = float(limits["block_pct"])
    projected = float(consumed_usd) + float(estimated_run_cost_usd)
    ratio = projected / budget if budget > 0 else 0.0

    if ratio >= block:
        return BudgetPolicyDecision("block", estimated_run_cost_usd, projected, budget, f"Projected spend ${projected:.2f} exceeds budget ${budget:.2f}")
    if ratio >= warn:
        return BudgetPolicyDecision("warn", estimated_run_cost_usd, projected, budget, f"Projected spend ${projected:.2f} is above {int(warn*100)}% threshold of ${budget:.2f}")
    return BudgetPolicyDecision("allow", estimated_run_cost_usd, projected, budget, "Within budget policy")
