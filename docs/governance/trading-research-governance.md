# Trading Research Governance Standard

This policy defines governance boundaries for MB-P2-005 trading, portfolio, and arbitrage research skills.

## Scope
Applies to all `trading-research` category skills, including market data ingestion, portfolio/risk analytics, backtesting, and arbitrage analysis.

## Core Safety Constraints
- Research-only outputs; no autonomous trading and no direct order execution.
- Human-in-the-loop approval is mandatory before any operational action.
- Default execution mode is offline/dry-run using local fixtures.
- Skills must label trade ideas as hypotheses with assumptions, risk factors, time horizon, and invalidation criteria.

## Prohibited Assistance
- No market manipulation support (including spoofing/pump-and-dump patterns).
- No insider trading support.
- No evasive guidance or compliance circumvention strategies.
- No personalized final investment advice or guaranteed-return claims.

## Validation Expectations
- Governance validation tests must assert research-only, HITL gating, and prohibited-conduct blocking language.
- Backtesting guidance must remain bounded to analysis/simulation with no live execution paths.
