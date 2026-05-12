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


## Workspace-primary phased execution plan (2026-05-12)

Execution now follows a workspace-primary rollout model with explicit phase scope and exit gates.

### P0 — Orchestrator, intake, and artifacts foundation

Scope:
- Route all new sessions through the conversation orchestrator as the default workspace entrypoint.
- Apply adaptive intake + interruption directives (`pause`, `switch`, `forget`, `resume`) before domain dispatch.
- Normalize assistant-created outputs into artifact envelope types (plan/workflow/task/knowledge/approval).

Release gate:
- **Schema validation:** all generated artifacts validate against `schemas/artifacts/*.schema.json` and shared envelope contract.
- **Routing quality checks:** intent-router benchmark pass-rate meets acceptance threshold for single-domain and multi-domain prompts.
- **Interruption handling:** pause/switch/resume flows preserve session consistency and do not lose pending approvals or plan state.

### P1 — Plan + knowledge + tasks convergence

Scope:
- Use conversation-to-plan as the canonical planning path.
- Integrate knowledge-note proposal/lifecycle workflow during planning.
- Add deterministic plan→workflow and plan→tasks converters as first-class actions.

Release gate:
- **Schema validation:** plan/task/workflow artifacts and conversion outputs pass validation.
- **Routing quality checks:** planner dispatch and conversion routing remain policy-safe with no ambiguous fall-through.
- **UX acceptance criteria:** operators can produce, edit, and approve a living plan and derive tasks without leaving workspace.

### P2 — Chips + preview + approvals hardening

Scope:
- Enable deterministic action chips with explainability and reversibility.
- Unify dry-run preview payloads for scheduled and direct execution.
- Converge all high-impact paths into Approval Center with auditable runtime transitions.

Release gate:
- **Approval safety:** all external-write paths require explicit approval and preserve policy context + rationale.
- **Interruption handling:** runtime pause/resume/cancel states remain recoverable from audit/history artifacts.
- **UX acceptance criteria:** chip actions, preview transparency, and approval decisions are understandable and reversible.

### P3 — Conversational skill creation

Scope:
- Provide conversational reusable-skill drafting from workspace context.
- Enforce validator-gated promotion before any draft is persisted/published.
- Require review-first artifact preview + explicit write approval.

Release gate:
- **Schema validation:** generated skill artifacts/manifests pass contract validation.
- **Approval safety:** no skill persistence/promotion without explicit operator approval.
- **UX acceptance criteria:** users can draft, inspect, revise, and promote skills with clear provenance and guardrails.

## Migration notes: legacy chat/workflow entrypoints to workspace-primary

- `apps/assistant-workspace/streamlit_app.py` is the default operator surface for new sessions.
- Existing `apps/chat-ui/streamlit_app.py` and standalone workflow entrypoints remain available for backward compatibility, but should be treated as legacy interfaces.
- Migration recommendation:
  1. Start new workflows in Assistant Workspace.
  2. Use Plan Builder + Workflow Studio within the same session context rather than cross-app handoff.
  3. Route all approval-requiring operations through Approval Center.
  4. Use legacy entrypoints only for regression checks or transitional runbooks.

## Telemetry checkpoints for workspace-primary adoption

Track the following checkpoints each release cycle:

- **Adoption:** percent of new operator sessions started in Assistant Workspace vs legacy chat/workflow entrypoints.
- **Completion rate:** percent of workspace-started runs that reach terminal success state without manual restart.
- **Clarification-rate reduction:** average clarification questions per run compared with baseline from pre-workspace intake behavior.
- **Approval latency and safety:** decision latency distribution for approval requests and policy-blocked action rate.
- **Interruption recovery quality:** percent of paused/interrupted runs successfully resumed without data/state loss.
