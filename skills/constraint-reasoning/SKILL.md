---
name: constraint-reasoning
description: Evaluates candidate plans and decisions against hard and soft constraints, detects violations and conflicts, and generates alternative plans when the primary plan is infeasible.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, hierarchical-planning, telemetry]

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

Constraint satisfaction evaluator for the cognitive runtime. Validates proposed plans and
decisions against an explicit constraint set, distinguishes hard violations (blocking) from
soft violations (penalizing), and generates alternative feasible plans when the primary
proposal fails constraint checks.

## Activation Triggers

- Hierarchical-planning produces a candidate plan requiring constraint validation before execution
- Cognitive-runtime detects a constraint violation during plan execution and needs re-planning
- Operator adds or modifies a constraint and triggers re-validation of active plans
- Decision-intelligence skill requests constraint feasibility check before scoring alternatives

## Execution Protocol

1. **Load constraint set**: Retrieve all active constraints — hard (must not violate) and soft
   (should minimize violation) — from the governance registry and workflow definition.

2. **Evaluate candidate plan**: For each constraint, determine whether the plan satisfies,
   violates, or is indeterminate; record the violation type and severity.

3. **Classify violations**: Hard violations block execution immediately; soft violations
   accumulate a penalty score that reduces the plan's feasibility score.

4. **Generate alternatives**: For each blocking hard violation, propose the minimum set of
   plan modifications that would resolve it; enumerate up to 3 feasible alternative plans.

5. **Score alternatives**: Rank alternative plans by combined feasibility score (constraint
   satisfaction + resource efficiency + objective alignment).

6. **Emit constraint evaluation**: Return the evaluation result — FEASIBLE, INFEASIBLE with
   alternatives, or INDETERMINATE requiring human review — with full violation details.

## Output Format

Constraint evaluation record with: `plan_id`, `verdict` (FEASIBLE/INFEASIBLE/INDETERMINATE),
`hard_violations` (list), `soft_violations` (list with penalty scores), `feasibility_score`,
`alternative_plans` (ranked list), and recommended next action.

## References

- `references/constraint-catalog.md` — constraint types, evaluation logic, alternative generation rules