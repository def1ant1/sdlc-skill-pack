# Assistant Workspace UX Architecture

## Purpose

`apps/assistant-workspace/` is the primary operator entrypoint for cross-surface assistant execution. It consolidates existing chat/workflow/memory capabilities into a persistent panel workspace with a shared session context.

## Primary surfaces

- Assistant Home
- Plan Builder
- Workflow Studio
- Skill Library
- Knowledge Base
- Task & Schedule Center

Navigation is modeled as a single active surface state in `st.session_state.workspace["active_nav"]`.

## Persistent panel layout

The workspace renders four synchronized panels:

1. Conversation
2. Working Plan
3. Artifacts
4. Knowledge / Memory

Each panel reads and writes through the same `st.session_state.workspace` object so user actions in chat are immediately reflected in planning, artifact creation, and memory capture.

## Panel synchronization contract

`_sync_action()` acts as the local synchronization hook for chat-driven updates:

- appends user + assistant messages to `conversation`
- updates session context (`goal`, `last_action`, `updated_at`)
- advances `plan` status and appends executable steps
- adds generated plan artifacts to `artifacts`
- stores reusable notes in `knowledge`

This creates deterministic, session-scoped consistency across all workspace panes without requiring page reload or cross-app navigation.

## Assistant action chips UX contract

The assistant workspace supports deterministic action chips generated from response context and active artifacts.

### Supported chip set

- Create plan
- Convert to workflow
- Break into tasks
- Save as skill
- Schedule recurrence
- Add to knowledge
- Run dry-run
- Request approval
- Show dependencies
- Show risks
- Generate report

### Explainability and reversibility requirements

Each chip must include:

- `explain_why`: a user-facing reason describing why the chip is shown.
- `reversible`: explicit controls for `undo`, `cancel`, and `edit_before_execute`.

### Audit event requirements

When a chip is triggered, the system records an auditable event with:

- `conversation_id`
- `message_id`
- `chip_key`
- `action`
- `timestamp`
- optional `artifact_id`

These events provide traceability for operator review and governance evidence.

## Dry-run preview and approval-center integration (2026-05-12)

Assistant Home and Workflow Studio now expose a shared dry-run preview contract before execution:

- Step-by-step execution preview.
- Explicit gate type per step (`none`, `soft_hitl`, `hard_hitl`).
- Side-effect class per step (`read`, `analysis`, `external_write`).
- Missing-input surfacing before run dispatch.

### Unified execution pathways

Scheduled and direct execution triggers both construct the same candidate-run preview payload and flow into the same approval + evidence pathway. This prevents governance drift between trigger origins.

### Approval Center actions

Approval Center now presents:

- pending approvals queue
- risk reason
- policy context
- actions: approve, reject, edit, request detail

Approval decisions are linked to runtime control transitions and recorded in the pause/resume audit trail (`runtime.paused_for_hitl`, `runtime.resumed`, `runtime.cancelled`).
