# Plan-First Workflow Experience

## UX goals
- Make planning the default interaction before task/workflow execution.
- Preserve full plan revision history so operators can inspect intent drift.
- Keep approvals and lifecycle transitions explicit (`draft -> in_review -> approved -> archived`).

## Plan workspace editing
The plan editing interface (`apps/chat-ui/plan_workspace.py`) provides:
- Metadata strip with Plan ID, status, and version.
- Editable title/objectives and JSON editors for `phases` + `cost_assumptions`.
- Revision save that creates immutable history snapshots.
- Status controls for plan approval/archive lifecycle transitions.
- Revision inspector with event log and point-in-time snapshots.

## Conversion preview expectations
Conversion previews now expose operator-critical dimensions before execution handoff:
- **Skills**: union of required skills extracted from approved tasks.
- **Gates**: review/approval checkpoints that must pass before execution.
- **Cost assumptions**: inherited defaults and per-task overrides.
- **Dependencies**: `depends_on` graph for sequencing.

## Operator journey
1. Draft and refine plan in workspace.
2. Review revision diff/history for governance.
3. Move to `approved` status.
4. Convert to tasks or workflow using artifact scripts.
5. Validate preview sections (skills, gates, costs, dependencies).
6. Hand off to runtime execution.
