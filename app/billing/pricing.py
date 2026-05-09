"""
app/billing/pricing.py — Model pricing table (USD per million tokens).

Prices are approximate list prices as of early 2026.
Override via APOTHEON_MODEL_PRICING env var (JSON string) if needed.
"""
from __future__ import annotations

import json
import os

# Format: model_id -> {"input": $/1M tokens, "output": $/1M tokens}
_DEFAULT_PRICING: dict[str, dict[str, float]] = {
    "claude-opus-4-6": {"input": 15.00, "output": 75.00},
    "claude-sonnet-4-6": {"input": 3.00, "output": 15.00},
    "claude-haiku-4-5-20251001": {"input": 0.80, "output": 4.00},
    # Fallback / legacy
    "claude-3-opus-20240229": {"input": 15.00, "output": 75.00},
    "claude-3-sonnet-20240229": {"input": 3.00, "output": 15.00},
    "claude-3-haiku-20240307": {"input": 0.25, "output": 1.25},
}

# Allow runtime override via env var
_env_override = os.environ.get("APOTHEON_MODEL_PRICING", "")
if _env_override:
    try:
        MODEL_PRICING: dict[str, dict[str, float]] = json.loads(_env_override)
    except json.JSONDecodeError:
        MODEL_PRICING = _DEFAULT_PRICING
else:
    MODEL_PRICING = _DEFAULT_PRICING

DEFAULT_MODEL = os.environ.get("APOTHEON_DEFAULT_MODEL", "claude-sonnet-4-6")


def cost_usd(model: str, input_tokens: int, output_tokens: int) -> float:
    """Calculate USD cost for a model call."""
    pricing = MODEL_PRICING.get(model, MODEL_PRICING.get(DEFAULT_MODEL, {"input": 3.0, "output": 15.0}))
    return (input_tokens / 1_000_000 * pricing["input"]) + (output_tokens / 1_000_000 * pricing["output"])