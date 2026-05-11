---
name: comparison-engines
description: Compare candidate arbitrage opportunities across marketplaces and execution paths using normalized spread, cost, risk, confidence, and compliance scoring.
---

# Comparison Engines

## Purpose
Rank opportunities using normalized economics and risk/compliance dimensions so operators can approve only policy-safe, high-confidence candidates.

## Required scoring output
Each compared opportunity must include:

- `gross_spread`
- `estimated_costs` (itemized + total)
- `net_spread`
- `liquidity_score`
- `timing_risk`
- `confidence`
- `legal_policy_checks`

## Comparison method
1. Normalize all prices/costs to a common currency and timestamp.
2. Recompute spread model with the same assumptions across options:
   - fees
   - taxes
   - shipping
   - slippage
   - timing risk premium
3. Score and rank primarily by risk-adjusted `net_spread`, then by `liquidity_score`, then by `confidence`.
4. Apply a policy/compliance veto:
   - If `legal_policy_checks` is fail, mark as ineligible.
   - If warn, require explicit reviewer acknowledgment.

## Policy boundaries
The engine must reject any plan relying on:

- ToS-violating collection or access methods.
- Manipulation or deceptive market behavior.
- Guidance intended to bypass controls, rate limits, compliance, or moderation.

## Human-in-the-loop controls
No execution handoff is allowed without explicit approval. Require a human decision checkpoint before:

- buy/purchase
- listing/posting
- trade/order routing
- outreach or negotiation messages

When approval is missing, output analysis artifacts only and set `execution_status: "blocked_pending_human_approval"`.
