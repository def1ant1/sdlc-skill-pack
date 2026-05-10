---
name: economic-coordination
description: Coordinates AI compute resource allocation across agents using priority economics, task bidding, quota enforcement, and budget-aware scheduling to maximize enterprise value per compute dollar.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [runtime-economics, agent-kernel, cluster-management, governance]

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

Internal resource arbitration authority for the Autonomous OS. Manages compute budgets across
agents and workflows, enforces per-agent quotas, runs priority-weighted task scheduling, and
ensures high-value work is never starved by lower-priority background tasks.

## Activation Triggers

- Resource contention detected between competing agents
- Compute budget threshold reached for a period
- High-priority task requiring immediate resource reallocation
- Budget period reset requiring quota refresh
- Quota violation detected by agent-kernel

## Execution Protocol

1. **Assess resource demand**: Collect pending task queue from all agents with priority weights,
   estimated compute requirements, and deadline urgency.

2. **Check budget availability**: Verify remaining compute budget for the current period;
   compute available headroom per resource type (CPU, GPU, RAM).

3. **Run priority scheduling**: Sort pending tasks by priority weight (P0: 100, P1: 50,
   P2: 20, P3: 5); allocate compute greedily down the priority queue.

4. **Enforce quotas**: Cap any single agent at its configured tier quota; redistribute
   excess demand to other waiting tasks in the same priority band.

5. **Handle budget exhaustion**: Suspend lowest-priority tasks; emit budget.alert if
   critical work is blocked; escalate to operator if budget override needed.

6. **Record economics**: Emit cost.allocated events per agent per period; produce period
   summary for runtime-economics reporting and budget forecasting.

## Output Format

Resource allocation decision with: tasks scheduled, tasks deferred, quota adjustments applied,
budget consumption update, and period economics summary.

## References

- `references/resource-arbitration-policy.md` — priority weights by task class, quota defaults per agent tier, budget enforcement and override rules