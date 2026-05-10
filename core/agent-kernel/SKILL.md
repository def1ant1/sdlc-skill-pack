---
name: agent-kernel
description: Manages agent process isolation, resource quota enforcement, and lifecycle state transitions for all agents running in the Autonomous OS, providing cgroups-based compute boundary enforcement.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: platform
  maturity: alpha
  dependencies: [economic-coordination, event-bus, telemetry]

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

Agent process manager and resource enforcement layer for the Autonomous OS. Spawns, monitors,
suspends, and terminates agent processes; enforces per-agent resource quotas (CPU, GPU, memory,
duration) via cgroups v2; manages the 7-state agent lifecycle; and integrates with
economic-coordination for priority-based resource arbitration.

## Activation Triggers

- Cognitive-runtime or sdlc-orchestration requests a new agent spawn
- Resource quota breach detected on a running agent
- Agent heartbeat timeout triggers health check and potential suspension
- Economic-coordination signals a preemption request for a lower-priority agent

## Execution Protocol

1. **Spawn agent**: Validate the agent identity, capability tier, and available quota; create
   an isolated process namespace; apply cgroups v2 limits per the resource-quota-policy;
   transition to SPAWNING → RUNNING state.

2. **Monitor resource usage**: Sample CPU, GPU, and memory usage at 1-second intervals;
   compare against tier quota limits; enforce soft limits (throttle) before hard limits (kill).

3. **Manage lifecycle transitions**: Process state transition events — SUSPEND (save state,
   pause execution), RESUME (restore state, continue), PREEMPT (save state, yield resources),
   DRAIN (complete current unit, then terminate gracefully), TERMINATE (immediate stop).

4. **Enforce duration limits**: Track cumulative execution time per session; terminate agents
   that exceed their tier duration quota; emit quota-exceeded events for accounting.

5. **Handle failures**: On FAILED state, capture final state and error context; emit
   `agent.failed` event; notify runtime-recovery for workflow-level recovery if applicable.

6. **Account resource usage**: Produce a cost record per session for economic-coordination;
   record actual CPU/GPU/duration consumed for budget reconciliation.

## Output Format

Agent execution record with: `agent_id`, `agent_tier`, `lifecycle_states_traversed` (list),
`cpu_core_seconds`, `gpu_vram_gb_seconds`, `peak_memory_mb`, `duration_ms`,
`termination_reason`, and per-session cost record.

## References

- `references/agent-lifecycle-states.md` — 7-state lifecycle machine with telemetry events per transition
- `references/resource-quota-policy.md` — 5 quota tiers, enforcement mechanisms, cost accounting