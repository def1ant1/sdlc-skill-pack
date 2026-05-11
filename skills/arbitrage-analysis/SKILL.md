---
name: arbitrage-analysis
description: Analyze cross-market arbitrage opportunities with comprehensive spread modeling, policy-safe intelligence gathering, and human-gated execution recommendations.
---

# Arbitrage Analysis

## Purpose
Identify and compare potential arbitrage opportunities while explicitly modeling execution uncertainty and enforcing safe/ethical policy boundaries.

## Required opportunity schema
For every opportunity, output the following fields:

- `gross_spread`: Difference between best expected sell proceeds and buy cost before deductions.
- `estimated_costs`: Itemized and totaled deductions, including:
  - platform/exchange fees
  - taxes and duties
  - shipping/logistics/fulfillment
  - expected slippage
  - timing risk premium
- `net_spread`: `gross_spread - estimated_costs.total`
- `liquidity_score`: 0-100 score based on observed depth/volume/turnover and time-to-fill assumptions.
- `timing_risk`: 0-100 risk score where higher means greater risk from latency, volatility, transfer delays, settlement windows, or inventory holding time.
- `confidence`: 0-100 confidence score based on source quality, quote freshness, and model assumptions.
- `legal_policy_checks`: Structured pass/warn/fail results for legal constraints, platform policy compliance, and jurisdiction restrictions.

## Spread modeling requirements
Compute expected spread using:

1. `gross_spread = expected_sell_price - expected_buy_price`
2. `estimated_costs.total = fees + taxes + shipping + slippage + timing_risk_premium`
3. `net_spread = gross_spread - estimated_costs.total`

Where:

- `fees` include trading, withdrawal, deposit, conversion, listing, and payment processing costs.
- `taxes` include estimated VAT/sales tax/capital gains exposure when relevant.
- `shipping` includes transport, insurance, packaging, and handling.
- `slippage` includes order book depth effects and expected adverse fill.
- `timing_risk_premium` estimates expected decay from transfer/settlement delays and volatility during the execution window.

## Policy boundaries (hard constraints)
Never provide or recommend:

- Terms-of-service violating access patterns (e.g., unauthorized scraping, credential sharing, anti-bot bypassing).
- Market manipulation tactics (spoofing, wash trading, fake listings, rumor pumping).
- Bypass guidance for controls, limits, compliance checks, or platform safeguards.

If a user request conflicts with these constraints, refuse that part and propose compliant alternatives.

## Human approval gate (mandatory)
Before any operational action, require explicit human approval for:

- purchase or procurement actions
- listing/publication actions
- trade execution or order placement
- outreach/contact to counterparties

Default mode is **analysis only**. Do not execute or simulate execution as committed action without approval.
