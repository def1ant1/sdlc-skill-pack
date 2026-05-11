"""Pre-execution workflow cost estimation and runtime cost summaries."""
from __future__ import annotations

from collections import defaultdict
from datetime import UTC, datetime
from typing import Optional

from app.billing.pricing import DEFAULT_MODEL, MODEL_PRICING, cost_usd

_STATIC_ESTIMATES: dict[str, tuple[int, int]] = {
    "requirements": (1200, 2400),
    "architecture": (2500, 4000),
    "ai-engineering": (3000, 5000),
    "backend": (2000, 3500),
    "frontend": (1800, 3000),
    "code-review": (2500, 2000),
    "qa": (2000, 3000),
    "devsecops": (2500, 4000),
    "release-management": (1500, 2500),
    "observability": (1500, 2000),
    "sre": (2000, 3000),
    "compliance-automation": (3000, 4500),
    "executive-reporting": (2000, 3500),
    "sdlc-orchestration": (800, 1200),
    "sdlc-memory-token-management": (600, 800),
    "audit-trail": (400, 600),
}
_DEFAULT_ESTIMATE = (2000, 3000)


def estimate_skill_cost(skill_name: str, model: str = DEFAULT_MODEL, baseline: Optional[dict] = None) -> dict:
    if baseline and baseline.get("avg_input_tokens") and baseline.get("avg_output_tokens"):
        input_tok = int(baseline["avg_input_tokens"])
        output_tok = int(baseline["avg_output_tokens"])
        source = "benchmark"
    else:
        input_tok, output_tok = _STATIC_ESTIMATES.get(skill_name, _DEFAULT_ESTIMATE)
        source = "static_estimate"

    usd = cost_usd(model, input_tok, output_tok)
    return {
        "skill_name": skill_name,
        "model": model,
        "input_tokens": input_tok,
        "output_tokens": output_tok,
        "cost_usd": round(usd, 6),
        "source": source,
    }


def estimate_workflow_cost(skills: list[str], model: str = DEFAULT_MODEL, baselines: Optional[dict[str, dict]] = None) -> dict:
    baselines = baselines or {}
    breakdown = []
    total_input = 0
    total_output = 0
    total_cost = 0.0

    for skill in skills:
        est = estimate_skill_cost(skill, model=model, baseline=baselines.get(skill))
        breakdown.append(est)
        total_input += est["input_tokens"]
        total_output += est["output_tokens"]
        total_cost += est["cost_usd"]

    return {
        "model": model,
        "skills": breakdown,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost_usd": round(total_cost, 6),
        "pricing_per_1m": MODEL_PRICING.get(model, {}),
        "note": "Estimates only; actual costs depend on runtime prompt length and output verbosity.",
    }


def summarize_cost_events(events: list[dict]) -> dict:
    """Aggregate runtime events into daily/weekly/monthly cost summaries."""
    daily = defaultdict(float)
    weekly = defaultdict(float)
    monthly = defaultdict(float)
    total = 0.0

    for event in events:
        cost = float(event.get("estimated_cost_usd", event.get("cost_usd", 0.0)) or 0.0)
        ts_raw = event.get("timestamp") or datetime.now(UTC).isoformat()
        ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        day_key = ts.date().isoformat()
        iso_year, iso_week, _ = ts.isocalendar()
        week_key = f"{iso_year}-W{iso_week:02d}"
        month_key = f"{ts.year}-{ts.month:02d}"
        daily[day_key] += cost
        weekly[week_key] += cost
        monthly[month_key] += cost
        total += cost

    return {
        "total_cost_usd": round(total, 6),
        "daily": {k: round(v, 6) for k, v in sorted(daily.items())},
        "weekly": {k: round(v, 6) for k, v in sorted(weekly.items())},
        "monthly": {k: round(v, 6) for k, v in sorted(monthly.items())},
    }
