# Topic Routing Policy

## Overview

Defines topic naming conventions, routing rules, subscription models, dead-letter queue
policy, and retention settings for all event-bus topics in the Autonomous OS.

---

## Topic Naming Conventions

Topics follow the dot-separated hierarchical format: `<domain>.<entity>.<action>`

```
workflow.step.completed
agent.kernel.preempted
checkpoint.storage.created
alignment.output.blocked
telemetry.gpu.utilization
```

**Rules:**
- All segments lowercase, hyphens allowed within segments (e.g., `agent-kernel`)
- Maximum 5 segments per topic name
- Wildcards permitted in subscription patterns only, not in publish topics

---

## Routing Rules

### Wildcard Subscription Patterns

| Pattern | Matches | Example Matches |
|---|---|---|
| `workflow.*` | All direct children | `workflow.started`, `workflow.completed` |
| `workflow.#` | All descendants | `workflow.step.completed`, `workflow.step.failed` |
| `*.failed` | Any entity failure event | `workflow.failed`, `agent.failed` |
| `alignment.#` | All alignment events | `alignment.output.blocked`, `alignment.audit.completed` |

### Priority Routing

Events from P0 tasks are routed to a dedicated high-priority queue lane that bypasses
standard consumer queue depth limits. P0 events are delivered within 100ms regardless
of normal queue backlog.

| Priority Class | Routing Lane | Delivery SLO |
|---|---|---|
| P0 | priority-lane-0 | 100 ms |
| P1 | priority-lane-1 | 500 ms |
| P2 | standard | 2,000 ms |
| P3 | standard | 5,000 ms |

---

## Subscription Models

### Durable Subscription

- Consumer registers a named subscription with a starting offset
- Events are retained and redeliverable even if consumer is offline
- Consumer acknowledges each event; unacknowledged events are redelivered after timeout
- Suitable for: workflow orchestration, audit logging, governance consumers

```yaml
subscription:
  name: "compliance-audit-consumer"
  topic_pattern: "alignment.#"
  model: durable
  ack_timeout_s: 30
  max_redelivery_attempts: 5
  starting_offset: latest  # latest | earliest | specific_sequence
```

### Ephemeral Subscription

- Consumer receives events only while connected; no replay on reconnect
- No acknowledgment required; fire-and-forget delivery
- Suitable for: dashboards, real-time monitoring, low-stakes notifications

```yaml
subscription:
  name: "dashboard-live-feed"
  topic_pattern: "telemetry.#"
  model: ephemeral
```

### Broadcast Subscription

- All registered consumers receive every event on the topic (fan-out)
- Each consumer maintains its own offset pointer
- Suitable for: cache invalidation, configuration change notifications

---

## Dead-Letter Queue Policy

Events are routed to the dead-letter queue (DLQ) when:

1. Maximum redelivery attempts exceeded (default: 5)
2. Consumer returns a permanent rejection (not a transient failure)
3. Message TTL expires before acknowledgment

DLQ topic naming: `dlq.<original_topic>` (e.g., `dlq.workflow.step.completed`)

**DLQ retention:** 30 days
**DLQ monitoring:** Operator is alerted when any DLQ depth exceeds 100 messages
**DLQ replay:** Operator can replay DLQ events to the original topic after investigating

---

## Retention Settings Per Topic Category

| Topic Category | Retention Period | Compaction | Max Message Size |
|---|---|---|---|
| `workflow.*` | 90 days | No | 1 MB |
| `agent.*` | 30 days | No | 256 KB |
| `checkpoint.*` | 90 days | No | 4 MB |
| `alignment.*` | 365 days | No | 512 KB |
| `telemetry.*` | 7 days | Yes (last value per key) | 64 KB |
| `operator.*` | 365 days | No | 256 KB |
| `dlq.*` | 30 days | No | Same as source |

---

## Ordering Guarantees

- **Within a partition:** Strict FIFO ordering guaranteed
- **Partition key:** Set by the producer (default: `workflow_id` or `agent_id`)
- **Across partitions:** No ordering guarantee — consumers must handle out-of-order delivery
- **Sequence gap detection:** Consumer libraries detect gaps in sequence numbers and
  trigger automatic replay requests before processing later events

---

## Topic Creation Policy

New topics may only be created by:
- Platform team via the governance approval workflow
- Automated topic creation for well-known DLQ patterns

Ad-hoc topic creation by individual skills is prohibited to prevent topic sprawl.
Skills must request new topics through the topic registry.