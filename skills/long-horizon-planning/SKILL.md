---
name: long-horizon-planning
description: Develops multi-week to multi-year strategic execution plans with rolling-horizon detail, milestone sequencing, risk-adjusted scheduling, and adaptive replanning triggers.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, hierarchical-planning, forecasting, decision-intelligence]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Long-horizon planning specialist for objectives spanning weeks to years. Applies rolling-horizon
planning: near-term phases are planned in detail, distant phases at coarser granularity. Integrates
risk-adjusted scheduling, dependency tracking, and automatic replanning triggers to keep plans
actionable as conditions evolve.

## Activation Triggers

- Strategic objective with horizon > 4 weeks submitted
- Annual or quarterly planning cycle initiated
- Existing long-horizon plan requires major revision due to changed conditions
- Product roadmap or technology migration requiring multi-phase sequencing

## Execution Protocol

1. **Parse objective and horizon**: Extract goal statement, hard deadline, constraints, and key
   milestones; classify horizon (medium: 4-12 weeks, long: 3-12 months, strategic: 1-5 years).

2. **Retrieve strategic context**: Query knowledge-graph for relevant prior plans, decisions,
   resource commitments, and organizational constraints affecting this horizon.

3. **Apply rolling-horizon structure**: Decompose into planning zones: Zone 1 (next 4 weeks,
   detailed task-level plan), Zone 2 (4-16 weeks, milestone-level plan), Zone 3 (beyond 16 weeks,
   objective-level roadmap with uncertainty ranges).

4. **Risk-adjust schedule**: For each milestone, apply duration uncertainty (±20% for near-term,
   ±50% for Zone 2, ±100% for Zone 3); compute P50 and P90 completion dates.

5. **Define replanning triggers**: Specify conditions that invalidate the plan and trigger a new
   planning cycle (e.g., milestone delayed >20%, strategic assumption changed, key resource lost).

6. **Produce plan artifact**: Structured plan with Zone 1 task list, Zone 2 milestone map, Zone 3
   roadmap, risk-adjusted schedule, and replanning trigger definitions.

## Output Format

Long-horizon plan document with: zone-by-zone breakdown, milestone dependency graph, P50/P90
schedule, top 5 risks with mitigation strategies, replanning triggers, and next Zone 1 sprint plan.

## References

- `references/rolling-horizon-methodology.md` — zone boundaries, uncertainty parameterization, replanning trigger criteria