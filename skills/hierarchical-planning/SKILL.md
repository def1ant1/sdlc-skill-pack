---
name: hierarchical-planning
description: Decomposes high-level objectives into executable task hierarchies using Hierarchical Task Network planning, producing structured goal trees with dependency ordering and resource requirements.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [cognitive-runtime, workflow-runtime, telemetry]

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

HTN-based planning engine for the cognitive runtime. Translates abstract objectives into
fully ordered, executable task hierarchies with explicit dependency graphs, resource
requirements, and success criteria at every level of decomposition.

## Activation Triggers

- New objective received by cognitive-runtime requiring task decomposition
- Replanning triggered by goal failure, constraint violation, or context change
- Operator-requested planning for a multi-step initiative
- Proactive planning triggered by strategic-planning skill for long-horizon objectives

## Execution Protocol

1. **Parse objective**: Extract the goal statement, constraints (hard and soft), available
   resources, and deadline from the planning request context.

2. **Select planning strategy**: Choose from sequential, parallel, speculative, conservative,
   or adaptive strategy based on objective complexity, risk tolerance, and resource availability
   per the planning-strategies reference.

3. **Decompose to sub-goals**: Apply HTN methods to recursively decompose the objective into
   sub-goals until all leaf nodes are primitive actions executable by a skill or agent.

4. **Assign resources**: For each leaf task, estimate required CPU/GPU/time budget and assign
   to an available agent tier based on resource-arbitration-policy.

5. **Order with dependencies**: Construct a DAG of task dependencies; compute the critical
   path; identify parallelizable branches; set earliest-start and latest-finish times.

6. **Validate plan**: Check all hard constraints are satisfiable; verify resource totals do
   not exceed available capacity; confirm all required skills exist in the skill registry.

7. **Emit goal tree**: Serialize the completed plan as a goal tree and publish to cognitive-runtime
   for execution monitoring and replanning.

## Output Format

Goal tree document with: root goal GOAL-ID, decomposition depth, total leaf tasks, critical
path duration, resource budget summary, dependency DAG, and per-node status (PENDING).

## References

- `references/htn-decomposition-rules.md` — method library, decomposition heuristics, strategy selection criteria