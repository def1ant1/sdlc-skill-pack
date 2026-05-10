---
name: goal-decomposition
description: Converts abstract strategic objectives into atomic, measurable sub-goals with explicit success criteria, ownership assignments, and dependency ordering for execution by the cognitive runtime.
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

Atomic sub-goal generator for the cognitive runtime. Bridges the gap between high-level
intent and executable tasks by producing SMART sub-goals — Specific, Measurable, Achievable,
Relevant, Time-bound — with clear ownership and measurable completion criteria.

## Activation Triggers

- Hierarchical-planning requests leaf-level decomposition for a goal node
- Strategic-planning skill requires operationalization of a quarterly objective
- Operator submits a new initiative requiring structured breakdown
- Replanning event triggers re-decomposition of a failed sub-goal

## Execution Protocol

1. **Parse goal context**: Extract the parent goal statement, available context (domain,
   constraints, resources, timeline), and the desired decomposition depth.

2. **Generate candidate sub-goals**: Produce 3–7 candidate sub-goals per parent, each with
   a clear action verb, measurable outcome metric, and explicit completion condition.

3. **Validate SMART criteria**: For each candidate, verify specificity (unambiguous scope),
   measurability (quantifiable success metric), achievability (within resource bounds),
   relevance (contributes to parent goal), and time-boundedness (has deadline).

4. **Assign ownership**: Match each sub-goal to the most capable available agent or skill
   based on the goal domain, required capabilities, and current agent workloads.

5. **Order dependencies**: Identify which sub-goals must complete before others can start;
   construct dependency edges; validate the dependency graph is acyclic.

6. **Emit sub-goal records**: Publish each sub-goal as a structured GOAL-ID record to the
   cognitive-runtime goal tree.

## Output Format

Sub-goal set with: parent GOAL-ID, N child GOAL-IDs each containing goal statement, success
metric, owner, deadline, dependencies, and SMART validation status.

## References

- `references/goal-schema.md` — GOAL-ID format, SMART validation rules, decomposition depth limits