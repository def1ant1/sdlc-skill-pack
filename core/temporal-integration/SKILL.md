---
name: temporal-integration
description: Integrates Temporal.io cluster for durable workflow signals, queries, schedules, namespace isolation, and workflow visibility with a migration path from the bespoke workflow-runtime.
metadata:
  version: "0.1.0"
  category: infrastructure
  owner: platform
  maturity: draft
  dependencies: ['workflow-runtime', 'event-bus', 'telemetry']
---

## Role

Enterprise-grade durable workflow engine integration. Manages the Temporal cluster, registers
workflow and activity workers, routes long-running enterprise workflows to Temporal for
guarantee of execution, and exposes workflow signals, queries, and schedule management.
Provides a migration path from the platform's bespoke `workflow-runtime` for workflows
requiring Temporal's stronger durability guarantees.

## Activation Triggers

- A workflow is submitted with `durability: temporal` in its execution spec
- A Temporal workflow requires an external signal injection (e.g., human approval received)
- A schedule is due to trigger a recurring workflow
- `workflow-runtime` detects a workflow that has exceeded its checkpoint recovery attempts
  (escalate to Temporal for guaranteed completion)
- A namespace isolation policy change requires worker redeployment
- Operator queries workflow history or visibility for audit/debug

## Execution Protocol

1. **Namespace management**: Each enterprise business unit or security domain gets an isolated
   Temporal namespace. Enforce namespace-level authorization via Temporal's namespace policies.
   Create namespaces via Temporal Cloud or self-hosted Temporal server API.

2. **Worker fleet management**: Deploy Temporal workers as Kubernetes deployments.
   Each worker registers: `task_queue`, `workflow_types`, `activity_types`.
   Scale worker replicas based on task queue backlog depth from Temporal metrics API.

3. **Workflow registration**: Register workflow and activity definitions with type-safe
   schemas. Validate that workflow definitions match the registered task queue and namespace.

4. **Workflow execution**: Start workflows via Temporal client:
   - `workflow_id`: deterministic ID (idempotent — re-submission returns existing run)
   - `task_queue`: target worker pool
   - `input`: typed workflow input payload
   - `execution_timeout` and `task_timeout` from workflow spec
   Return `workflow_id` + `run_id` for tracking.

5. **Signal & query**: Route incoming signals (human approvals, external events) to the
   correct running workflow. Execute workflow queries for current state read-outs.

6. **Visibility**: Surface workflow execution history, event timeline, and failure reasons
   via the Temporal visibility API. Feed into `operator-console` for observability.

## Output Format

```yaml
temporal_workflow:
  workflow_id: "enterprise-workflow-PROJ123-phase2"
  run_id: "01906xxx-xxxx-xxxx-xxxx"
  namespace: "engineering"
  task_queue: "sdlc-workers"
  status: RUNNING | COMPLETED | FAILED | CANCELLED | TIMED_OUT
  started_at: "2026-05-07T10:00:00Z"
  completed_at: null
  history_length: 0
  visibility_url: "http://temporal-ui/namespaces/engineering/workflows/..."
```

## References

- `references/` — Namespace policy schema, worker deployment spec, workflow registration contract
