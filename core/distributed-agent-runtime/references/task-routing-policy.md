# Task Routing Policy

## Overview

Defines task routing rules, load balancing strategies, affinity rules, failover policy,
and routing decision log format for the distributed-agent-runtime coordinator.

---

## Routing Decision Algorithm

For each incoming task, the coordinator applies rules in priority order:

```
1. Hard constraint filtering  → Remove ineligible nodes
2. Affinity scoring           → Rank remaining nodes
3. Load balancing             → Apply weighted selection
4. Failover guard             → Verify node health before committing
```

---

## Hard Constraint Rules (Eliminate Before Scoring)

| Rule | Condition | Elimination Trigger |
|---|---|---|
| TIER-001 | Task requires agent tier T | Exclude nodes that don't support tier T |
| GPU-001 | Task requires GPU acceleration | Exclude nodes with gpu_count = 0 |
| CAP-001 | Task requires specialization S | Exclude nodes where specialization ≠ S |
| HEALTH-001 | Node health status | Exclude UNREACHABLE and SATURATED nodes |
| SLOT-001 | Agent slot availability | Exclude nodes with available_slots = 0 |
| BUDGET-001 | Cost tier constraint | Exclude cloud nodes if local capacity available |

---

## Affinity Scoring Rules

After hard filtering, score remaining nodes 0–100:

| Rule | Score Contribution | Description |
|---|---|---|
| DATA-LOCALITY | +30 if same datacenter as task data source | Minimize data transfer |
| LABEL-MATCH | +20 per matching task/node label pair | Environment, region match |
| PRIOR-SESSION | +15 if node has existing agent session for this workflow | State locality |
| LOW-LOAD | +10 × (1 - cpu_utilization) | Prefer less-loaded nodes |
| THERMAL | +5 if no GPU throttling on node | Thermal headroom |

---

## Load Balancing Strategies

### Weighted Round-Robin (Default)

Weight = available_slots / max_slots. Nodes with more headroom receive proportionally
more tasks. Recalculated every 30 seconds.

### Least-Connections

Select the node with the fewest active agents. Used for long-running tasks where
completion time is unpredictable.

**Activation:** Task estimated duration > 300 seconds → use least-connections.

### Sticky Session

Route all tasks from the same workflow to the same node (within capacity).
Maximizes KV cache locality and reduces context reload overhead.

**Activation:** Task carries `sticky_session: true` label.

---

## Failover Policy

### Primary Failover

If the selected primary node fails before task completion:

1. Check if task has a checkpoint → Yes: route to next-best healthy node, restore from checkpoint
2. No checkpoint → Check task idempotency flag:
   - `idempotent: true`: Restart task on next-best node
   - `idempotent: false`: Emit `task.failed`; trigger runtime-recovery for workflow-level decision

### Coordinator Failover

When the leader coordinator fails, the Raft group elects a new leader within 5 seconds.
In-flight routing decisions may be retried by the client (task submission includes a
client-side idempotency key). Tasks not yet acknowledged are requeued by the new leader.

---

## Routing Decision Log Format

Every routing decision is logged for audit and optimization feedback:

```yaml
routing_decision:
  decision_id: "RD-20260507-004521"
  task_id: "TASK-WF-042-008"
  workflow_id: "WF-20260507-042"
  timestamp: "2026-05-07T14:23:00.456Z"

  candidates_evaluated: 5
  candidates_eliminated:
    - node_id: "DNODE-003"
      reason: "HEALTH-001: SATURATED"
    - node_id: "DNODE-004"
      reason: "GPU-001: no GPU"

  scored_candidates:
    - node_id: "DNODE-001"
      affinity_score: 75
      load_score: 82
      composite_score: 79
    - node_id: "DNODE-002"
      affinity_score: 60
      load_score: 91
      composite_score: 76

  selected_node: "DNODE-001"
  routing_strategy: "weighted-round-robin"
  sticky_session: false
  decision_latency_ms: 2
```

---

## Routing Timeout Policy

| Phase | Timeout | On Timeout |
|---|---|---|
| Node selection | 100 ms | Use default round-robin; log warning |
| Node acknowledgment | 2,000 ms | Retry on next-best node |
| Task handoff | 5,000 ms | Mark as routing failure; escalate |

---

## Anti-Flapping Rules

To prevent rapid back-and-forth routing between nodes:

- A node that was de-selected due to SATURATED status is excluded from routing for
  60 seconds after recovering to healthy status (ramp-up period)
- A node that caused 3 consecutive task failures is quarantined for 300 seconds before
  being re-admitted to the routing pool
- Routing table updates are batched at 30-second intervals to prevent thrashing