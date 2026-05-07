# Workflow DSL

## Overview

The Workflow DSL (Domain-Specific Language) defines how to author workflow DAGs
in YAML. Workflows are validated by the workflow-engine before execution.

---

## Workflow Document Structure

```yaml
workflow:
  id: "WF-<unique-id>"
  name: "<human-readable name>"
  version: "1.0.0"
  description: "<purpose of this workflow>"
  template_id: "<template name if derived from template>"
  trigger:
    type: manual | scheduled | event | workflow
    schedule: "0 17 * * 5"     # cron (for scheduled)
    event: "<event name>"        # for event-triggered
    workflow: "<workflow id>"    # for workflow-triggered (on completion)
  timeout_minutes: 120
  on_timeout: fail | notify | continue
  inputs:
    - name: "<input name>"
      type: string | number | boolean | object
      required: true | false
      default: <value>
      description: "<what this input is>"
  steps:
    - id: "step-1"
      name: "<step name>"
      skill: "<skill name>"
      inputs:
        <key>: "<value or {{context.variable}}>"
      outputs:
        - name: "<output name>"
          from: "<expression>"
      timeout_minutes: 15
      retry:
        max_attempts: 3
        backoff: exponential | fixed
        backoff_seconds: 30
      on_error: fail | skip | fallback
      fallback_step: "<step id>"
      approval_gate:
        required: true
        level: level-2 | level-3
        timeout_hours: 24
        escalate_after_hours: 8
      condition: "{{context.step1.output.status == 'success'}}"
      depends_on: ["step-0"]
```

---

## Context Variables

Within step inputs, conditions, and output mappings, use `{{context.variable}}` syntax:

| Variable | Description |
|---|---|
| `{{context.inputs.<name>}}` | Workflow-level input |
| `{{context.<step_id>.outputs.<name>}}` | Output from a previous step |
| `{{context.workflow.id}}` | Current workflow ID |
| `{{context.workflow.started_at}}` | Workflow start time (ISO8601) |
| `{{context.now}}` | Current timestamp (ISO8601) |
| `{{context.operator}}` | Operator who triggered the workflow |

---

## Condition Expressions

Step conditions control whether a step executes. They must evaluate to true/false:

```yaml
# Run step only if previous step succeeded
condition: "{{context.step1.status == 'succeeded'}}"

# Run step only if output meets threshold
condition: "{{context.eval_step.outputs.score >= 0.80}}"

# Always run (default — omit condition)
condition: "true"

# Skip step in dry-run mode
condition: "{{context.inputs.dry_run != true}}"
```

---

## Approval Gate Configuration

```yaml
approval_gate:
  required: true
  level: level-3              # minimum level required to approve
  description: "Production deployment approval required"
  context_fields:             # fields from step outputs to show in approval UI
    - field: "outputs.deployment_summary"
      label: "Deployment Summary"
    - field: "outputs.test_results"
      label: "Test Results"
  timeout_hours: 24           # auto-fail if no response
  escalate_after_hours: 8     # ping escalation contact after N hours
  auto_approve_condition: "{{context.deployment.risk_level == 'low'}}"
```

---

## Error Handling Patterns

### Pattern 1 — Fail Fast

```yaml
on_error: fail
# Workflow halts immediately; operator is notified
```

### Pattern 2 — Skip and Continue

```yaml
on_error: skip
# Step is skipped; workflow continues with next step
# Use only for non-critical steps
```

### Pattern 3 — Fallback Step

```yaml
on_error: fallback
fallback_step: "rollback-step"
# On failure: execute the named fallback step, then halt
```

### Pattern 4 — Retry

```yaml
retry:
  max_attempts: 3
  backoff: exponential
  backoff_seconds: 30
# Retries: 30s, 60s, 120s — then falls to on_error behavior
```

---

## Complete Example — Model Promotion Workflow

```yaml
workflow:
  id: "WF-model-promotion"
  name: "LoRA Model Promotion"
  version: "1.0.0"
  description: "Evaluate, benchmark, and promote a LoRA adapter to production"
  trigger:
    type: event
    event: "lora.training.completed"
  timeout_minutes: 240
  inputs:
    - name: model_id
      type: string
      required: true
    - name: adapter_path
      type: string
      required: true
  steps:
    - id: "evaluate"
      name: "Evaluate adapter"
      skill: "model-evaluation"
      inputs:
        model_id: "{{context.inputs.model_id}}"
        adapter_path: "{{context.inputs.adapter_path}}"
      outputs:
        - name: eval_score
          from: "outputs.overall_score"
        - name: eval_decision
          from: "outputs.decision"
      timeout_minutes: 60
      retry:
        max_attempts: 2
        backoff: fixed
        backoff_seconds: 60
      on_error: fail

    - id: "check-threshold"
      name: "Check promotion threshold"
      skill: "lora-lifecycle"
      condition: "{{context.evaluate.outputs.eval_decision == 'PROMOTE'}}"
      inputs:
        model_id: "{{context.inputs.model_id}}"
        eval_score: "{{context.evaluate.outputs.eval_score}}"
      depends_on: ["evaluate"]
      on_error: fail

    - id: "approval-gate"
      name: "Level-2 promotion approval"
      skill: "hitl-dashboard"
      depends_on: ["check-threshold"]
      approval_gate:
        required: true
        level: level-2
        timeout_hours: 24
        escalate_after_hours: 8

    - id: "promote"
      name: "Promote to production"
      skill: "lora-lifecycle"
      depends_on: ["approval-gate"]
      inputs:
        model_id: "{{context.inputs.model_id}}"
        action: "promote"
      on_error: fail

    - id: "audit-log"
      name: "Write audit entry"
      skill: "telemetry"
      depends_on: ["promote"]
      inputs:
        event: "model.promoted"
        model_id: "{{context.inputs.model_id}}"
        eval_score: "{{context.evaluate.outputs.eval_score}}"
      on_error: skip    # audit logging failure should not block
```