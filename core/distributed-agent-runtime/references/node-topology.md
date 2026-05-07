# Node Topology Reference

## Overview

Defines the multi-node agent cluster topology schema, node roles, health check protocol,
node registration format, and failure detection thresholds for the distributed-agent-runtime.

---

## Node Roles

| Role | Description | Min Count | Max Agents |
|---|---|---|---|
| coordinator | Routes tasks, monitors health, manages agent registry | 1 (3 for HA) | N/A |
| worker | Executes agent processes; primary compute | 1+ | Per quota tier |
| observer | Read-only health and telemetry monitoring | 0+ | N/A |
| gateway | Handles external task ingestion and result delivery | 1+ | N/A |

---

## Node Registration Format

Nodes self-register with the coordinator on startup:

```yaml
node_registration:
  node_id: "DNODE-20260507-001"        # Assigned by coordinator on registration
  hostname: "agent-worker-01.internal"
  role: worker
  registered_at: "2026-05-07T10:00:00Z"

  capabilities:
    cpu_cores: 32
    ram_gb: 256
    gpu_count: 0
    supported_agent_tiers: [background, standard, elevated]
    max_concurrent_agents: 8

  network:
    internal_ip: "10.1.2.10"
    agent_port: 8080
    health_port: 8081
    datacenter: "DC-West"
    rack: "R07"

  labels:
    region: "us-west-2"
    environment: "production"
    specialization: "general"           # general | gpu | memory-optimized
```

---

## Health Check Protocol

### Heartbeat (Active Health Check)

Each worker node sends a heartbeat to the coordinator every 15 seconds:

```yaml
heartbeat:
  node_id: "DNODE-20260507-001"
  timestamp: "2026-05-07T14:23:00Z"
  status: healthy                        # healthy | degraded | draining
  active_agents: 3
  queued_tasks: 1
  resource_utilization:
    cpu_percent: 45.2
    ram_percent: 62.1
    agent_slots_used: 3
    agent_slots_total: 8
```

### Passive Health Check (Coordinator-Initiated)

The coordinator probes each node every 30 seconds via HTTP GET `/health`:

```json
{
  "status": "healthy",
  "uptime_seconds": 86400,
  "active_agents": 3,
  "last_successful_task_at": "2026-05-07T14:22:55Z"
}
```

---

## Failure Detection Thresholds

| Condition | Threshold | Action |
|---|---|---|
| Heartbeat missing | > 30 seconds | Mark node SUSPECT; redirect new tasks |
| Heartbeat missing | > 60 seconds | Mark node UNREACHABLE; migrate running agents |
| Health probe fails | 3 consecutive failures | Mark node DEGRADED; reduce task allocation |
| High error rate | > 10% task failures in 5 min | Mark node DEGRADED |
| Resource saturation | CPU > 95% OR RAM > 95% for 60s | Mark node SATURATED; no new tasks |
| Node recovery | Heartbeat resumes after UNREACHABLE | Mark RECOVERING; gradual ramp-up |

---

## Agent Migration on Node Failure

When a node is marked UNREACHABLE:

1. Coordinator identifies all agents running on the failed node
2. For each agent with a valid checkpoint: spawn replacement on a healthy node;
   restore from checkpoint; resume execution
3. For agents without checkpoints: emit `agent.failed` event; trigger
   runtime-recovery workflow
4. Update task routing table to exclude the failed node
5. Alert operator if > 2 nodes fail within 10 minutes (potential cascade)

---

## Load Balancing Strategy

The coordinator uses a **weighted round-robin** strategy with these weights:

```
node_score = (available_agent_slots / max_agent_slots) × 0.40
           + (1 - cpu_utilization) × 0.30
           + (1 - ram_utilization) × 0.20
           + affinity_score × 0.10
```

**Affinity rules (highest priority):**
- Task requires GPU → route only to nodes with `gpu_count > 0`
- Task has data locality tag → prefer nodes in same datacenter as data source
- Task has `specialization` label → prefer matching node `specialization`

---

## Coordinator High-Availability

In HA mode, 3 coordinator nodes form a Raft consensus group:
- Leader handles all routing and registration writes
- Followers replicate state and can serve read queries
- Leader election completes within 5 seconds of leader failure
- No task routing interruption for leader elections < 5 seconds