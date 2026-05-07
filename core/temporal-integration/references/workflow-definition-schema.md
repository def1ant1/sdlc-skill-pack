# Temporal Integration — Workflow Definition Schema

## Workflow Registration Schema

```yaml
temporal_workflow:
  workflow_id: "apotheon.sdlc.code-review"
  workflow_type: "CodeReviewWorkflow"
  task_queue: "apotheon-sdlc"
  namespace: "apotheon-prod"

  execution_config:
    workflow_execution_timeout: "24h"
    workflow_run_timeout: "4h"
    workflow_task_timeout: "60s"

  retry_policy:
    initial_interval: "1s"
    backoff_coefficient: 2.0
    maximum_interval: "5m"
    maximum_attempts: 5
    non_retryable_error_types:
      - "ValidationError"
      - "PolicyViolationError"

  search_attributes:
    skill_name: keyword
    phase: keyword
    initiated_by: keyword
    priority: keyword
```

---

## Activity Definition Schema

```yaml
temporal_activity:
  activity_type: "RunInferenceActivity"
  task_queue: "apotheon-sdlc"

  schedule_to_close_timeout: "30m"
  schedule_to_start_timeout: "5m"
  start_to_close_timeout: "25m"
  heartbeat_timeout: "60s"

  retry_policy:
    initial_interval: "2s"
    backoff_coefficient: 2.0
    maximum_interval: "2m"
    maximum_attempts: 3
    non_retryable_error_types:
      - "AuthenticationError"
      - "QuotaExceededError"
```

---

## Standard SDLC Workflow Patterns

### Sequential Phase Workflow

```python
@workflow.defn
class SDLCPhaseWorkflow:
    @workflow.run
    async def run(self, input: SDLCInput) -> SDLCOutput:
        # Gate: validate input
        validated = await workflow.execute_activity(
            validate_input,
            input,
            start_to_close_timeout=timedelta(seconds=30),
        )

        # Core: run primary skill
        result = await workflow.execute_activity(
            run_skill,
            SDLCSkillInput(skill=input.skill, payload=validated),
            start_to_close_timeout=timedelta(minutes=20),
            heartbeat_timeout=timedelta(seconds=60),
        )

        # Gate: HITL review if required
        if result.requires_human_review:
            approved = await workflow.execute_activity(
                request_hitl_approval,
                result,
                schedule_to_close_timeout=timedelta(hours=24),
            )
            if not approved:
                raise ApplicationError("Human reviewer rejected output")

        return result
```

### Fan-Out / Fan-In Workflow

```python
@workflow.defn
class MultiModalWorkflow:
    @workflow.run
    async def run(self, inputs: list[ModalInput]) -> UnifiedContext:
        # Fan-out: process all modalities in parallel
        tasks = [
            workflow.execute_activity(
                process_modality,
                inp,
                start_to_close_timeout=timedelta(minutes=30),
            )
            for inp in inputs
        ]
        results = await asyncio.gather(*tasks)

        # Fan-in: merge into unified context
        return await workflow.execute_activity(
            assemble_context,
            results,
            start_to_close_timeout=timedelta(minutes=5),
        )
```

---

## Cron Workflow Schema

```yaml
cron_workflow:
  workflow_id: "apotheon.compliance.daily-scan"
  workflow_type: "ComplianceScanWorkflow"
  cron_schedule: "0 2 * * *"   # 2 AM UTC daily
  task_queue: "apotheon-compliance"

  execution_config:
    workflow_run_timeout: "2h"

  overlap_policy: skip   # skip | allow | terminate_other
```

---

## Signal & Query Definitions

| Signal Name | Direction | Purpose |
|-------------|-----------|---------|
| `cancel_workflow` | External → Workflow | Graceful cancellation |
| `inject_context` | External → Workflow | Add mid-run context |
| `hitl_decision` | External → Workflow | Human review response (approve/reject) |
| `pause` | External → Workflow | Pause execution at next activity boundary |
| `resume` | External → Workflow | Resume after pause |

| Query Name | Returns | Purpose |
|------------|---------|---------|
| `get_status` | `WorkflowStatus` | Current phase + progress |
| `get_output` | `PartialOutput` | Best available output so far |
| `get_audit_trail` | `list[AuditEvent]` | Activity history |

---

## Workflow Error Taxonomy

| Error Type | Retryable | Behavior |
|-----------|-----------|----------|
| `TransientError` | Yes | Retry with backoff |
| `ValidationError` | No | Fail immediately; surface to caller |
| `PolicyViolationError` | No | Fail + escalate to security agent |
| `QuotaExceededError` | No | Fail + alert ops |
| `HITLRejectionError` | No | Fail + notify requester |
| `TimeoutError` | Yes (limited) | Retry up to `maximum_attempts` |
| `AuthenticationError` | No | Fail + alert security |

---

## Namespace Configuration

```yaml
temporal_namespace:
  name: "apotheon-prod"
  retention_period: "30d"
  history_archival_state: enabled
  visibility_archival_state: enabled
  archival_uri: "gs://apotheon-temporal-archive/"
```