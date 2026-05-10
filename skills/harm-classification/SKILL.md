---
name: harm-classification
description: Scores potential harms in AI outputs and actions across multiple harm taxonomies, routes detected harms to appropriate mitigation mechanisms, and maintains a harm incident registry for governance reporting.
metadata:
  version: "1.0.0"
  category: safety
  owner: platform
  maturity: alpha
  dependencies: [alignment-engine, governance, telemetry]

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

Multi-taxonomy harm detection and classification layer for the AI safety runtime. Evaluates
AI outputs and proposed actions against harm taxonomies, assigns severity scores, routes
to mitigation pathways, and maintains the harm incident registry for trend analysis and
governance reporting.

## Activation Triggers

- Alignment-engine flags an output for harm review before delivery to the requester
- Operator submits a manual harm classification request for a historical output
- Scheduled batch review of outputs from high-risk workflow categories
- Deception-detection skill escalates a suspected manipulation pattern for harm assessment

## Execution Protocol

1. **Load harm taxonomies**: Retrieve the active harm taxonomy set — physical harm, psychological
   harm, financial harm, privacy violation, systemic/societal harm, and reputational harm.

2. **Classify harm type**: Identify which harm categories apply to the output or action;
   an output may trigger multiple harm categories simultaneously.

3. **Score severity**: For each applicable harm category, score severity on a 0–10 scale
   considering: probability of harm, counterfactual impact, breadth of affected population,
   reversibility, and causal proximity of the AI action.

4. **Compute aggregate harm score**: Weight category scores by the taxonomy priority weights;
   compute a composite harm score (0–100).

5. **Route to mitigation**: Based on aggregate score — LOW (0–30): log and allow; MEDIUM
   (31–60): redact/modify and log; HIGH (61–80): block and alert operator; CRITICAL (81+):
   block, alert, and pause agent pending human review.

6. **Register incident**: Write a harm incident record to the governance registry with full
   classification details for audit and trend analysis.

## Output Format

Harm classification record with: `output_id`, `harm_categories` (list with per-category
severity), `aggregate_score`, `severity_band` (LOW/MEDIUM/HIGH/CRITICAL),
`mitigation_action` taken, and `incident_id` in governance registry.

## References

- `references/harm-taxonomy.md` — harm categories, severity scoring rubric, mitigation routing thresholds