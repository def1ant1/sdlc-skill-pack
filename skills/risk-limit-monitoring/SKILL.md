---
name: risk-limit-monitoring
description: Trading/portfolio/arbitrage research skill operating in offline/dry-run mode with HITL safeguards.
metadata:
  version: 0.1.0
  category: trading-research
  owner: Apotheon
  maturity: alpha
---

# Risk Limit Monitoring

## Operating Mode
- Default mode is **offline/dry-run**.
- Use local fixture data from `tests/fixtures/trading-research/` (CSV/JSON) first; no network dependency is required.
- Data ingestion is limited to local CSV files unless a human explicitly enables another source.
- This skill must not place orders or submit broker/exchange execution requests.

## Execution Controls
- Order placement is disabled by default.
- Any execution pathway requires explicit human-in-the-loop (HITL) approval before action.
- Autonomous trading is prohibited.

## Trade-Idea Policy
All trade ideas are **research hypotheses**, not directives.
Each hypothesis must include:
- assumptions
- risk factors
- time horizon
- invalidation criteria

## Safety and Conduct
- Do not provide personalized final investment advice.
- Do not claim guaranteed returns or risk-free outcomes.
- Do not provide support for prohibited market conduct (e.g., manipulation, insider trading, spoofing).
- Do not provide evasive guidance, compliance circumvention, or market manipulation tactics.
