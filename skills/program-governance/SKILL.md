---
name: program-governance
description: Tracks initiative milestones and deliverables, detects schedule and budget variances, escalates risks to executive sponsors, and produces governance-grade status reports for portfolio oversight.
metadata:
  version: "1.0.0"
  category: governance
  owner: strategy
  maturity: alpha
  dependencies: [portfolio-optimization, initiative-prioritization, telemetry]

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

Program milestone tracking and governance reporting engine for the PMO. Maintains the
authoritative view of initiative status across the portfolio, proactively detects schedule
slippage and budget variance, routes risks to appropriate escalation levels, and generates
governance-grade reports for executive and board consumption.

## Activation Triggers

- Scheduled weekly governance cycle generates status collection and reporting
- Initiative owner updates milestone status triggering variance analysis
- Budget tracker reports spend deviation exceeding the alert threshold
- Portfolio-optimization requests current initiative health data for rebalancing

## Execution Protocol

1. **Collect status**: Gather milestone completion status, actual vs. planned spend,
   resource utilization, risk register updates, and blocker log from all active initiatives.

2. **Compute variance**: For each initiative, calculate schedule variance (SV = planned - actual
   completion %), cost variance (CV = budget - actual spend), and resource variance; classify
   as GREEN (within tolerance), AMBER (approaching threshold), or RED (threshold breached).

3. **Assess risk register**: Review open risks for each initiative; evaluate probability and
   impact changes since last cycle; identify risks that have escalated in severity.

4. **Escalate blockers**: Route RED status items and high-severity risk escalations to the
   appropriate sponsor level — project lead (minor), program manager (significant),
   executive sponsor (critical), governance board (program-wide impact).

5. **Generate status report**: Produce the weekly portfolio status report with RAG summary,
   milestone heatmap, budget waterfall, top risks and mitigations, and decisions required.

6. **Update governance record**: Log all status data, escalations, and decisions in the
   program governance registry for audit trail.

## Output Format

Governance status report with: `report_date`, `portfolio_rag_summary` (initiative count by RAG),
`milestone_heatmap`, `budget_variance_summary`, `top_risks` (list with severity and owner),
`escalations_raised` (list), and `decisions_required` (list with deadline).

## References

- `references/governance-report-template.md` — RAG thresholds, variance calculation formulas, escalation routing matrix