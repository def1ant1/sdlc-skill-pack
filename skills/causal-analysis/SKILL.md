---
name: causal-analysis
description: Applies causal inference methods (DiD, IV, RCT analysis, do-calculus) to enterprise data to establish causal relationships, estimate treatment effects, and support evidence-based decisions.
metadata:
  version: "1.0.0"
  category: analytics
  owner: data
  maturity: alpha
  dependencies: [data-fabric, semantic-layer, telemetry]

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

Causal inference engine for enterprise decision support. Moves beyond correlation to establish
causal relationships using rigorous statistical methods, enabling confident attribution of
outcomes to actions and reliable estimation of intervention effects before costly commitments.

## Activation Triggers

- Decision-intelligence skill requests causal evidence for a high-stakes decision
- Research-runtime requires causal effect estimation for a hypothesis test
- Operator submits a causal analysis request for a past intervention
- Predictive-reasoning skill needs causal structure to improve forecast accuracy

## Execution Protocol

1. **Define causal question**: Formalize the research question as a causal estimand —
   the specific treatment, outcome, and population of interest.

2. **Select identification strategy**: Choose the appropriate method based on data availability
   and study design — RCT analysis, Difference-in-Differences (DiD), Instrumental Variables
   (IV), Regression Discontinuity (RD), or do-calculus on a causal graph.

3. **Check identification assumptions**: Verify method-specific assumptions — parallel trends
   (DiD), instrument validity (IV), as-good-as-random assignment (RD), or d-separation in
   the causal graph.

4. **Estimate causal effect**: Apply the selected method; compute Average Treatment Effect
   (ATE) or Conditional ATE (CATE) with confidence intervals and p-values.

5. **Conduct robustness checks**: Test sensitivity to assumption violations using placebo
   tests, alternative control groups, or refutation methods; flag fragile estimates.

6. **Produce causal report**: Document estimand, method, assumptions, effect estimate,
   confidence interval, robustness findings, and actionable recommendation.

## Output Format

Causal analysis report with: `estimand`, `method`, `effect_estimate` (with 95% CI),
`p_value`, `assumption_checks` (pass/fail per assumption), `robustness_score`, and
`recommendation` with confidence level.

## References

- `references/causal-methods.md` — method selection guide, assumption checklists, robustness testing protocols