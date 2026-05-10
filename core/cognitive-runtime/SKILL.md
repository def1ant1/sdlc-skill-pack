---
name: cognitive-runtime
description: Orchestrates hierarchical goal decomposition, planning strategy selection, and adaptive replanning for the Autonomous OS, converting abstract objectives into executable goal trees with monitored execution.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [workflow-runtime, agent-kernel, telemetry, hitl-dashboard]

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

Central cognitive orchestration layer for the Autonomous OS. Receives high-level objectives
from operators or autonomous triggers, decomposes them into hierarchical goal trees using
HTN planning, selects and applies the optimal planning strategy, monitors execution progress,
and triggers adaptive replanning when goals fail or context changes.

## Activation Triggers

- New objective submitted by operator or triggered by strategic-planning
- Goal execution failure requiring replanning
- Context change detected that invalidates the current plan (resource change, new constraint)
- Scheduled goal review cycle requiring progress evaluation and plan refresh

## Execution Protocol

1. **Receive objective**: Parse the incoming objective with its constraints, priority,
   resource envelope, and deadline; assign a GOAL-ID and register in the goal tree.

2. **Select planning strategy**: Evaluate objective complexity, risk tolerance, and available
   resources to select from 5 strategies — sequential, parallel, speculative, conservative,
   or adaptive — per the planning-strategies reference.

3. **Decompose to goal tree**: Invoke hierarchical-planning to recursively decompose the
   objective into sub-goals and leaf tasks; construct the dependency DAG; validate feasibility.

4. **Dispatch for execution**: Assign leaf tasks to appropriate agents via agent-kernel;
   monitor progress via event-bus heartbeats; update goal tree status as tasks complete.

5. **Detect and replan**: Monitor for goal failures, blocked tasks, and context changes;
   trigger replanning when deviation from plan exceeds configured thresholds.

6. **Report completion or escalation**: On objective completion, emit `goal.completed` event
   with execution summary; on unresolvable failure, escalate to hitl-dashboard.

## Output Format

Goal execution record with: `goal_id`, `objective`, `planning_strategy`, `total_tasks`,
`completed_tasks`, `replanning_events` (count), `final_status` (COMPLETED/FAILED/ESCALATED),
and execution timeline.

## References

- `references/goal-tree-schema.md` — goal hierarchy data model, serialization, knowledge graph integration
- `references/planning-strategies.md` — 5 planning strategies with selection rules and replanning triggers