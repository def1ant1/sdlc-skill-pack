# Resource Quota Policy

## Overview

Every agent spawned by `agent-kernel` operates within a resource quota. Quotas prevent any
single agent from starving others and enforce the economic-coordination budget policies.

---

## Default Quota Tiers

| Agent Tier | CPU Cores | RAM | GPU VRAM | Max Duration | Max Parallel Tasks |
|---|---|---|---|---|---|
| background | 0.5 | 512 MB | 0 | 30 min | 1 |
| standard | 2 | 4 GB | 2 GB | 2 hours | 4 |
| elevated | 8 | 16 GB | 8 GB | 8 hours | 8 |
| privileged | 32 | 64 GB | 32 GB | 24 hours | unlimited |
| system | unlimited | unlimited | unlimited | unlimited | unlimited |

**Tier assignment rules:**
- Background: telemetry collectors, monitoring agents, scheduled reporting
- Standard: most domain skill invocations, search, retrieval, analysis
- Elevated: code execution, model inference, large data processing
- Privileged: multi-agent orchestration, production deployment, cluster management
- System: agent-kernel itself, alignment-engine, governance core skills

---

## Quota Override Rules

Quotas may be increased by:

1. **Operator override (Level 2):** Temporary quota increase for a specific agent session.
   Requires written justification and auto-expires after session ends.

2. **Economic-coordination approval:** If compute budget is available and priority is high,
   economic-coordination may grant a quota bump without operator involvement.

3. **Emergency escalation (Level 3):** P0 incident response agents receive privileged quota
   automatically until incident resolved.

**Quota decreases** may be applied by economic-coordination to rebalance during contention.
Agent is notified via `quota.adjusted` event and given 60 seconds to adapt before enforcement.

---

## Enforcement Mechanisms

### CPU Throttling

Applied via cgroups v2 CPU quota. When agent exceeds its CPU allocation for >30 seconds:
1. CPU is throttled to quota limit (not preempted)
2. Warn event emitted: `agent.quota_exceeded {resource: "cpu"}`
3. If throttled for >5 minutes: escalate to PREEMPTED state

### Memory Enforcement

Applied via cgroups v2 memory limit. OOM within cgroup:
1. Agent process receives SIGTERM
2. Kernel OOM killer contained to agent cgroup
3. Agent transitions to FAILED state
4. OOM event logged with memory usage history

### GPU/VRAM Enforcement

Managed by vLLM or Ollama server quotas. VRAM allocation is reserved at spawn time.
If requested VRAM exceeds available:
1. Spawn request is queued
2. Queue timeout: 5 minutes → spawn failure

### Duration Enforcement

Maximum duration is enforced via watchdog timer:
1. At 80% of max duration: warn event; agent receives `quota.time_warning`
2. At 100% of max duration: SIGTERM → DRAINING state → TERMINATED

---

## Quota Monitoring

Quota consumption is sampled every 15 seconds and emitted as `agent.resource_sample` events
containing: cpu_percent, ram_mb, vram_mb, elapsed_seconds.

Aggregate quota consumption is reported to economic-coordination every 5 minutes for budget
accounting and per-period cost allocation.

---

## Per-Session Quota Accounting

Each agent session (from SPAWNING to TERMINATED) produces a cost record:

```yaml
agent_session_cost:
  agent_id: "AGT-20260507-001"
  tier: standard
  workflow_id: "WF-20260507-001"
  cpu_core_seconds: 120.5
  ram_gb_seconds: 480.0
  vram_gb_seconds: 0.0
  duration_seconds: 240
  compute_cost_usd: 0.0042
  period: "2026-05-07"
```

These records feed the runtime-economics cost-per-workflow reporting.