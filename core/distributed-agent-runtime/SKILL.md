---
name: distributed-agent-runtime
description: Coordinates multi-agent task execution across distributed compute nodes with load balancing, fault tolerance, result aggregation, and distributed state synchronization.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [multi-agent, agent-kernel, event-bus, telemetry]

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

Runtime coordinator for distributed agent execution. Manages agent spawning across local and
remote compute nodes, routes tasks based on node capacity and locality, monitors execution
health, aggregates results from distributed sub-tasks, and handles node failures transparently.

## Activation Triggers

- Multi-agent task requiring parallel execution across nodes
- Agent pool on single node saturated; overflow to additional nodes needed
- Cross-node workflow dispatch from workflow-runtime
- Node failure requiring active task redistribution

## Execution Protocol

1. **Assess task parallelism**: Analyze task graph to identify independent sub-tasks that can
   execute concurrently on separate nodes.

2. **Select target nodes**: Score available nodes by: available capacity, network locality to
   required data, current queue depth, and cost per compute unit.

3. **Spawn agents on selected nodes**: Issue spawn requests via agent-kernel for each node;
   pass task context and data locality hints.

4. **Monitor execution**: Send heartbeat checks to each agent every 30 seconds; detect
   timeouts or failures; redistribute tasks from failed nodes within 60 seconds.

5. **Aggregate results**: Collect outputs from all distributed agents; resolve conflicts
   using designated merge strategy (majority vote, leader, or union).

6. **Emit telemetry**: Record distributed.task.completed event with node map, per-node
   latency, total cost, and result quality score.

## Output Format

Aggregated task result with: merged output from all nodes, per-node execution summary,
total duration, cost breakdown, and any fault events with recovery actions.

## References

- `references/node-topology.md` — cluster node registry, capability profiles, network locality map
- `references/task-routing-policy.md` — routing rules, load balancing strategy, fault tolerance configuration