# Event Schema Registry

## Overview

All events published to the Autonomous OS event-bus must conform to a registered schema.
This registry defines the standard event envelope, all built-in event types, and the
versioning policy for schema evolution.

---

## Standard Event Envelope

All events share this base structure regardless of type:

```yaml
event:
  event_id: "EVT-20260507-001234"      # Unique monotonic ID
  event_type: "workflow.step.completed" # Dot-separated type path
  schema_version: "1.0"                 # Semver of this event type's schema
  producer_id: "WF-20260507-042"        # ID of the producing skill or agent
  timestamp: "2026-05-07T14:23:00.123Z" # ISO 8601 UTC
  correlation_id: "COR-20260507-009"    # Links related events in a flow
  partition_key: "WF-20260507-042"      # Determines ordering partition
  payload: {}                            # Event-type-specific payload (see below)
```

---

## Built-in Event Types

### Workflow Events

#### `workflow.started`
```yaml
payload:
  workflow_id: string
  definition_id: string
  definition_version: string
  triggered_by: string     # agent_id or "operator"
  priority_class: string   # P0 | P1 | P2 | P3
```

#### `workflow.step.completed`
```yaml
payload:
  workflow_id: string
  step_index: integer
  step_name: string
  duration_ms: integer
  output_summary: string   # max 512 chars
```

#### `workflow.completed`
```yaml
payload:
  workflow_id: string
  total_steps: integer
  duration_ms: integer
  checkpoints_created: integer
  final_status: string     # COMPLETED | FAILED | SUSPENDED
```

#### `workflow.failed`
```yaml
payload:
  workflow_id: string
  failed_step_index: integer
  failure_type: string     # transient | permanent | resource | authorization | corruption
  error_message: string
  recovery_attempted: boolean
  escalation_id: string    # hitl-dashboard escalation ID if raised
```

### Checkpoint Events

#### `checkpoint.created`
```yaml
payload:
  checkpoint_id: string    # CHK-YYYYMMDD-NNN
  workflow_id: string
  step_index: integer
  storage_backend: string  # redis | postgres | s3
  payload_size_bytes: integer
  payload_hash: string     # SHA-256 hex
  write_latency_ms: integer
```

#### `checkpoint.verified`
```yaml
payload:
  checkpoint_id: string
  verification_result: string  # VALID | CORRUPT | MISSING
  hash_match: boolean
```

### Agent Events

#### `agent.spawned`
```yaml
payload:
  agent_id: string
  agent_type: string
  agent_tier: string       # background | standard | elevated | privileged | system
  workflow_id: string
  resource_quota:
    cpu_cores: number
    vram_gb: number
    duration_limit_s: integer
```

#### `agent.completed`
```yaml
payload:
  agent_id: string
  final_state: string      # TERMINATED | FAILED
  cpu_core_seconds: number
  gpu_vram_gb_seconds: number
  duration_ms: integer
```

#### `agent.preempted`
```yaml
payload:
  agent_id: string
  preempting_agent_id: string
  reason: string           # quota_exceeded | higher_priority | operator_request
  state_saved: boolean
```

#### `agent.failed`
```yaml
payload:
  agent_id: string
  failure_reason: string
  last_known_state: string  # lifecycle state at failure
  recovery_eligible: boolean
```

### Alignment Events

#### `alignment.output.approved`
```yaml
payload:
  output_id: string
  agent_id: string
  compliance_score: number  # 0-100
  behavioral_category: string
```

#### `alignment.output.blocked`
```yaml
payload:
  output_id: string
  agent_id: string
  compliance_score: number
  violations: [string]
  escalation_id: string
```

### Telemetry Events

#### `telemetry.metric`
```yaml
payload:
  metric_name: string
  metric_value: number
  unit: string
  labels: {}
  source_id: string
```

---

## Event Type Versioning Policy

- Schema versions follow semantic versioning: `MAJOR.MINOR`
- **MINOR bump**: additive changes (new optional fields) — backward compatible
- **MAJOR bump**: breaking changes (removed fields, type changes) — requires consumer migration
- A 90-day deprecation window applies before a MAJOR version is retired
- Consumers must specify the minimum schema version they support on subscription

---

## Reserved Topic Namespaces

| Namespace | Description | Retention |
|---|---|---|
| `workflow.*` | Workflow lifecycle events | 90 days |
| `agent.*` | Agent lifecycle events | 30 days |
| `checkpoint.*` | Checkpoint events | 90 days |
| `alignment.*` | Safety and alignment events | 365 days (audit) |
| `telemetry.*` | Metrics and observability | 7 days |
| `operator.*` | Human operator actions | 365 days (audit) |
| `dlq.*` | Dead-letter queue events | 30 days |