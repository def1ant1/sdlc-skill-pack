# Agent Lifecycle States

## Overview

Every agent process managed by `agent-kernel` transitions through a defined set of lifecycle
states. The state machine enforces resource accounting, safety gates, and cleanup at each
transition.

---

## State Definitions

### SPAWNING

The agent process is being initialized. Resources are being allocated; the execution context
is being configured; the sandbox profile is being applied.

**Entry action:** Resource quota check; sandbox provisioning; agent-id assignment.
**Exit condition:** Initialization complete (→ RUNNING) or initialization failed (→ FAILED).
**Max duration:** 30 seconds. Exceeding triggers automatic transition to FAILED.

---

### RUNNING

The agent is actively executing. Heartbeat checks occur every 15 seconds. Resource consumption
is monitored against quotas.

**Entry action:** Emit `agent.spawned` telemetry event.
**Exit conditions:**
- Task completed → DRAINING
- Quota violated → PREEMPTED
- Heartbeat missed (×3) → SUSPENDED
- Shutdown signal received → DRAINING
- Unrecoverable error → FAILED

---

### SUSPENDED

The agent's execution has been paused due to missed heartbeats or resource contention.
State is preserved in-memory. The agent may be resumed.

**Entry action:** Preserve execution context snapshot; release CPU quota (retain memory).
**Exit conditions:**
- Heartbeat resumed within 60s → RUNNING (auto-resume)
- Resume signal received → RUNNING
- Suspend duration >5 min → TERMINATED (context evicted)

---

### PREEMPTED

The agent has been paused by the scheduler to free resources for a higher-priority agent.
Unlike SUSPENDED, preemption is scheduler-initiated and the agent will resume when resources
are available.

**Entry action:** Flush in-progress step state to checkpoint; release CPU and GPU quota.
**Exit conditions:**
- Resources available → RUNNING
- Preemption duration >15 min → operator alert; decision required

---

### DRAINING

The agent has received a shutdown signal and is completing its current step before terminating.
No new tasks may be accepted.

**Entry action:** Set `accepting_work = false`; allow current step to complete.
**Exit condition:** Current step completed → TERMINATED.
**Max drain duration:** 60 seconds. Hard termination after timeout.

---

### TERMINATED

The agent process has exited normally. All resources have been released and the execution
context has been cleaned up.

**Entry action:** Flush final state to knowledge-graph; release all resources; emit `agent.completed`.
**Terminal state:** No further transitions.

---

### FAILED

The agent process has exited abnormally due to an unrecoverable error.

**Entry action:** Capture error context and stack trace; release all resources; emit `agent.failed`.
**Terminal state:** Failed agents are logged to the post-mortem queue for operator review.

---

## State Transition Diagram

```
               ┌──────────────┐
               │   SPAWNING   │
               └──────┬───────┘
          success ↓       ↓ timeout/error
               ┌──────┴───────┐        ┌────────┐
               │   RUNNING    │──────→ │ FAILED │
               └──────┬───────┘ error  └────────┘
     quota ↓  miss×3 ↓  signal ↓
  ┌──────────┐ ┌───────────┐ ┌───────────┐
  │PREEMPTED │ │ SUSPENDED │ │  DRAINING │
  └────┬─────┘ └─────┬─────┘ └─────┬─────┘
  avail ↓       resume ↓       done ↓
       └──────────────┘     ┌────────────┐
              (RUNNING)     │ TERMINATED │
                            └────────────┘
```

---

## Telemetry Events per Transition

| Transition | Event Type | Level |
|---|---|---|
| SPAWNING → RUNNING | `agent.spawned` | info |
| RUNNING → SUSPENDED | `agent.suspended` | warn |
| RUNNING → PREEMPTED | `agent.preempted` | warn |
| RUNNING → DRAINING | `agent.draining` | info |
| RUNNING → FAILED | `agent.failed` | error |
| DRAINING → TERMINATED | `agent.completed` | info |
| Any → FAILED | `agent.failed` | error |

---

## Resource Release on Termination

On any terminal state (TERMINATED, FAILED), the agent-kernel:

1. Releases CPU quota back to the economic-coordination pool
2. Releases GPU/VRAM allocation
3. Closes network policy (removes firewall rules for agent process)
4. Deletes ephemeral memory allocation
5. Flushes persistent memory to knowledge-graph (TERMINATED only; FAILED flushes error context)
6. Removes agent-id from active registry