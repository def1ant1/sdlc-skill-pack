# Resource Arbitration Policy

## Overview

The `economic-coordination` skill enforces this policy for all compute resource allocation
decisions across agents and workflows in the Autonomous OS.

---

## Priority Weight Table

| Task Class | Priority Weight | Rationale |
|---|---|---|
| P0 — Production incident response | 100 | System health; blocks everything else |
| P0 — Safety and alignment checks | 95 | Mandatory; cannot be deferred |
| P1 — Customer-facing workflow | 75 | Revenue and retention impact |
| P1 — Governance and compliance | 70 | Regulatory obligation |
| P2 — Engineering SDLC workflows | 50 | Core business function |
| P2 — Business operations workflows | 45 | Operational continuity |
| P3 — Analytics and reporting | 25 | Important but deferrable |
| P3 — Self-improvement and evolution | 20 | Background optimization |
| Background — Telemetry collection | 5 | Minimal resource requirement |

---

## Quota Defaults per Agent Tier

| Agent Tier | CPU Budget (cores/period) | GPU Budget (VRAM-hours/period) | Max Concurrent Agents |
|---|---|---|---|
| Background | 0.5 | 0 | 2 |
| Standard | 4 | 2 | 4 |
| Elevated | 16 | 8 | 2 |
| Privileged | Unlimited (period budget applies) | 32 | 1 |
| System | Unlimited | Unlimited | Unlimited |

**Period:** 1 hour rolling window for CPU/GPU; daily for overall cost budget.

---

## Budget Enforcement Rules

### Rule BE-001: Priority Preemption

When total demand exceeds available capacity, tasks are preempted in reverse priority order:
lowest priority first, until capacity is available for the requesting task.

**Exception:** Tasks within 5 minutes of completion are not preempted (completion is cheaper
than re-execution from checkpoint).

### Rule BE-002: Quota Cap

No single agent may consume more than 25% of total cluster capacity in any 1-hour period,
regardless of task priority — unless it is a P0 incident response agent.

### Rule BE-003: Budget Period Reset

At the start of each budget period (00:00 UTC daily for cost; rolling hourly for CPU/GPU):
- All quota counters reset to zero
- Suspended tasks are re-evaluated for scheduling

### Rule BE-004: Starvation Prevention

A task that has been waiting for resources for more than its class timeout is escalated:

| Priority Class | Starvation Timeout | Escalation Action |
|---|---|---|
| P0 | 60 seconds | Force preempt lowest-priority task |
| P1 | 5 minutes | Alert operator; preempt P3 tasks |
| P2 | 30 minutes | Alert in weekly report |
| P3 | 4 hours | Acceptable; no escalation |

### Rule BE-005: Budget Exhaustion

When the daily cost budget is 80% consumed by 18:00 UTC:
1. Suspend all P3 and background tasks
2. Alert operator with current consumption and projection
3. Operator may approve budget extension for the remainder of the period

At 100% consumption: suspend all P2 and below tasks; P0/P1 continue with escalating alerts.

---

## Override Mechanisms

### Emergency Override

A human operator may issue an emergency override that temporarily lifts all quota restrictions
for a specific agent or workflow. Emergency overrides:
- Expire automatically after 4 hours
- Are logged with operator identity and justification
- Trigger a budget reconciliation report at override expiry

### Operator Budget Extension

Operators may extend the daily compute budget by up to 2× via hitl-dashboard. Extensions
require Level-2 approval and are logged for cost accounting.

---

## Cost Accounting

Every resource allocation produces a cost record:

```yaml
allocation_record:
  period: "YYYY-MM-DD HH:00"
  agent_id: "AGT-NNN"
  agent_tier: "standard"
  workflow_id: "WF-YYYYMMDD-NNN"
  task_class: "P2"
  cpu_core_seconds_allocated: N
  gpu_vram_gb_seconds_allocated: N
  estimated_cost_usd: X.XXXX
  actual_cost_usd: X.XXXX   # computed at period end
```

Cost records feed runtime-economics reporting and budget forecasting for future periods.