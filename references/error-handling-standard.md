# Error Handling Standard

All runtime, planner, scheduler, and connector failures must emit a standard **error envelope**.

## Envelope Semantics

| Field | Meaning |
|---|---|
| `error_id` | Unique per emitted error instance. |
| `correlation_id` | Trace identifier shared across a request/workflow path. |
| `workflow_run_id` | Workflow execution ID (`n/a` if not in workflow context). |
| `schedule_run_id` | Schedule execution ID (`n/a` when not scheduled). |
| `skill` | Skill/module emitting error (`planner`, `scheduler`, `connector:*`, etc.). |
| `step` | Workflow step index or named phase. |
| `severity` | `info`, `warning`, `error`, `critical`. |
| `category` | Taxonomy category from backlog schema. |
| `retryable` | Whether automated retry is safe and recommended. |
| `user_action_required` | Whether operator/end-user action is required. |
| `message` | User-facing summary. |
| `technical_detail` | Technical context for logs and diagnosis. |
| `root_cause_hint` | Probable cause hypothesis. |
| `remediation` | **Required next-step guidance**. |
| `source_exception` | Original exception class/message snapshot. |
| `created_at` | UTC RFC3339 timestamp. |

## Rules

1. `remediation` must always be present and actionable for user-facing errors.
2. `correlation_id` must be logged with the envelope.
3. Use `retryable=true` only when the operation is safe to retry.
4. Use `workflow_run_id`/`schedule_run_id` as `n/a` if unknown.

## Example

```json
{
  "error_id": "err-2e0e8ef8",
  "correlation_id": "corr-10f6f72e",
  "workflow_run_id": "RUN-1715400000-ab12cd34",
  "schedule_run_id": "n/a",
  "skill": "connector:salesforce",
  "step": 3,
  "severity": "error",
  "category": "auth",
  "retryable": false,
  "user_action_required": true,
  "message": "Connector authentication failed.",
  "technical_detail": "HTTP 401 from Salesforce token endpoint",
  "root_cause_hint": "Expired or revoked API credentials",
  "remediation": "Rotate connector credentials and re-run the workflow step.",
  "source_exception": "RuntimeError: HTTP 401 POST ...",
  "created_at": "2026-05-11T00:00:00Z"
}
```
