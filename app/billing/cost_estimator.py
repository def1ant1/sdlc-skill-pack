"""
app/billing/cost_estimator.py — Pre-execution workflow cost estimation.

Uses benchmark baselines (p50 token counts) to estimate cost before running.
Falls back to static per-skill averages when no baseline data exists.
"""
from __future__ import annotations

import logging
from typing import Optional

from app.billing.pricing import DEFAULT_MODEL, MODEL_PRICING, cost_usd

logger = logging.getLogger("apotheon.cost_estimator")

# Static token estimates per skill when no benchmark data is available.
# Values are (avg_input_tokens, avg_output_tokens) based on empirical observation.
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

_DEFAULT_ESTIMATE = (2000, 3000)  # fallback for unknown skills


def estimate_skill_cost(
    skill_name: str,
    model: str = DEFAULT_MODEL,
    baseline: Optional[dict] = None,
) -> dict:
    """
    Estimate cost for a single skill execution.

    Args:
        skill_name: skill identifier
        model: model to use for pricing
        baseline: optional dict with avg_input_tokens / avg_output_tokens from DB

    Returns:
        dict with input_tokens, output_tokens, cost_usd, model, source
    """
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


def estimate_workflow_cost(
    skills: list[str],
    model: str = DEFAULT_MODEL,
    baselines: Optional[dict[str, dict]] = None,
) -> dict:
    """
    Estimate total cost for a workflow composed of the given skills.

    Args:
        skills: ordered list of skill names
        model: default model
        baselines: optional mapping skill_name -> baseline dict

    Returns:
        dict with per_skill breakdown and totals
    """
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

    pricing = MODEL_PRICING.get(model, {})
    return {
        "model": model,
        "skills": breakdown,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_cost_usd": round(total_cost, 6),
        "pricing_per_1m": pricing,
        "note": "Estimates only; actual costs depend on runtime prompt length and output verbosity.",
    }