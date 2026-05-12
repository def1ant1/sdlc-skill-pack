# MASTER UX BACKLOG — Apotheon Conversational Operating Environment

**Status:** Canonical UX/product backlog  
**Created:** 2026-05-12  
**Purpose:** Define the complete UI/UX, conversational workflow, assistant workspace, artifact, memory, task, schedule, execution, trust, and enterprise operating backlog for the Apotheon AI Company OS / SDLC Skill Pack.

---

## 0. Product North Star

Apotheon should evolve from a skill/workflow launcher into a **Conversational Operating Environment** where users can naturally collaborate with the assistant across planning, execution, scheduling, knowledge curation, governance, reporting, and continuous improvement.

The user experience should feel like:

```text
Conversation → visible working state → plan → tasks → workflow → execution → knowledge → improvement
```

The assistant should not force every new conversation through a rigid intake form. It should infer intent, draft useful starting points, ask only necessary questions, expose assumptions, and convert conversation into structured operational artifacts.

---

## 1. UX Principles

1. **Conversation first, structure second** — Users should talk naturally; structure should emerge from the conversation.
2. **Draft before interrogation** — Produce a useful first draft before asking refinement questions unless safety or correctness requires clarification.
3. **Visible cognition, not hidden magic** — Show goals, assumptions, risks, open questions, selected skills, and next actions in editable form.
4. **Artifact-centric collaboration** — Plans, workflows, tasks, schedules, skills, decisions, knowledge notes, approvals, and reports are first-class objects.
5. **Progressive automation** — Let interactions evolve from idea → plan → task → workflow → schedule → autonomous operation.
6. **Interruptibility** — Users can pause, redirect, branch, skip, rollback, or modify workflows at any time.
7. **Trust through provenance** — Every memory, task, decision, and recommendation should link to its source conversation, artifact, policy, or run.
8. **Governed autonomy** — Read-only and planning actions should be fluid; risky actions require approval and audit trails.
9. **Adaptive complexity** — Beginners get simple chat and guided actions; power users get DAGs, telemetry, graph views, policies, and advanced controls.
10. **Operational continuity** — Users should be able to resume an initiative, not restart a conversation.

---

# P0 — Foundational Conversational Operating Environment

## UX-P0-001 — Build persistent assistant workspace

**Status:** Open  
**Priority:** P0  
**Theme:** Workspace continuity

Create a persistent workspace model that connects conversations, plans, workflows, tasks, schedules, knowledge, decisions, reports, skills, approvals, and execution runs.

Create or harden:

```text
core/workspace/
schemas/workspace.schema.json
schemas/workspace-state.schema.json
schemas/conversation-session.schema.json
apps/chat-ui/workspace_state.py
apps/chat-ui/workspace_views.py
docs/architecture/assistant-workspace.md
```

Acceptance criteria:

- Every conversation belongs to a workspace.
- Workspace context persists across sessions.
- User can resume prior initiatives without restating context.
- Workspace links conversations, plans, workflows, tasks, schedules, decisions, knowledge notes, approvals, reports, and execution runs.
- Assistant references active workspace state before asking clarifying questions.
- Workspace state is inspectable, exportable, and schema-validated.

---

## UX-P0-002 — Replace rigid intake with adaptive conversation orchestration

**Status:** Open  
**Priority:** P0  
**Theme:** Conversation fluidity

Implement a conversation orchestrator that classifies intent, determines next safe action, and asks only necessary questions.

Create or harden:

```text
core/conversation-orchestrator/
core/conversation-orchestrator/SKILL.md
schemas/conversation-state.schema.json
schemas/conversation-intent.schema.json
scripts/orchestration/route_conversation_intent.py
docs/reference/adaptive-intake-policy.md
```

Acceptance criteria:

- Assistant supports freeform chat, brainstorming, planning, task creation, workflow generation, skill creation, scheduling, knowledge curation, reporting, and execution.
- Fixed multi-question intake is no longer required for workflow creation.
- Assistant asks no more than one clarifying question at a time unless a regulated/high-risk workflow requires structured intake.
- Assistant can proceed with explicit assumptions when the user says to use best assumptions.
- Missing information is represented as editable assumptions or open questions.

---

## UX-P0-003 — Add visible cognition panel

**Status:** Open  
**Priority:** P0  
**Theme:** Trust and control

Expose the assistant's user-safe working state as editable UI objects.

Create or harden:

```text
apps/chat-ui/visible_cognition_panel.py
schemas/assistant-working-state.schema.json
schemas/assumption.schema.json
schemas/constraint.schema.json
schemas/open-question.schema.json
schemas/risk.schema.json
docs/ux/visible-cognition.md
```

Acceptance criteria:

- UI shows active goal, assumptions, constraints, risks, open questions, pending decisions, selected skills, and next action.
- User can edit assumptions and constraints directly.
- Assistant updates plans/workflows when visible state changes.
- Visible cognition exposes concise working summaries, not private chain-of-thought.
- Every assumption includes source, confidence, and inferred/user-provided status.

---

## UX-P0-004 — Add artifact-first workspace model

**Status:** Open  
**Priority:** P0  
**Theme:** Structured collaboration

Make plans, workflows, tasks, schedules, skills, decisions, knowledge notes, approval requests, reports, and execution runs first-class UI objects.

Create or harden:

```text
core/artifact-system/
schemas/artifacts/plan.schema.json
schemas/artifacts/workflow.schema.json
schemas/artifacts/task.schema.json
schemas/artifacts/schedule.schema.json
schemas/artifacts/skill-proposal.schema.json
schemas/artifacts/decision.schema.json
schemas/artifacts/knowledge-note.schema.json
schemas/artifacts/approval-request.schema.json
schemas/artifacts/report.schema.json
schemas/artifacts/execution-run.schema.json
apps/chat-ui/artifact_panel.py
docs/architecture/artifact-first-workspace.md
```

Acceptance criteria:

- Assistant can create, update, version, link, and archive artifacts from chat.
- Every artifact has ID, type, title, status, owner, source conversation/message IDs, version, content, and relationships.
- User can reference artifacts naturally: “update the plan,” “schedule that workflow,” “turn step 3 into a task.”
- Artifact edits are auditable and reversible.

---

## UX-P0-005 — Add conversation-to-structure extraction

**Status:** Open  
**Priority:** P0  
**Theme:** Conversation intelligence

Continuously extract useful operational objects from conversation.

Create or harden:

```text
core/conversation-extraction/
scripts/orchestration/extract_conversation_structure.py
schemas/conversation-extraction.schema.json
schemas/extracted-requirement.schema.json
schemas/extracted-risk.schema.json
schemas/extracted-decision.schema.json
schemas/extracted-task.schema.json
schemas/extracted-entity.schema.json
docs/architecture/conversation-to-structure.md
```

Acceptance criteria:

- Assistant extracts tasks, requirements, decisions, risks, assumptions, entities, deadlines, dependencies, and policy references from chat.
- Extracted objects are shown as suggestions before durable persistence.
- User can approve, edit, reject, or merge extracted objects.
- Extraction links every object to source conversation and message IDs.
- Extraction supports plan, workflow, task, knowledge, decision, and requirement creation.

---

## UX-P0-006 — Build plan-first workflow experience

**Status:** Open  
**Priority:** P0  
**Theme:** Planning usability

Separate human-readable plans from executable workflows and make conversion explicit.

Create or harden:

```text
apps/chat-ui/plan_workspace.py
core/plan-system/
scripts/artifacts/plan_to_tasks.py
scripts/artifacts/plan_to_workflow.py
schemas/plan-version.schema.json
docs/ux/plan-first-workflow-experience.md
```

Acceptance criteria:

- Assistant can create a plan without immediately creating a workflow.
- User can edit plan objective, assumptions, phases, tasks, risks, dependencies, outputs, and success criteria.
- User can convert a plan to tasks, workflow, schedule, or template.
- Plans maintain version history.
- Plan-to-workflow conversion shows selected skills, gates, costs, and assumptions.

---

## UX-P0-007 — Add assistant action chips and quick actions

**Status:** Open  
**Priority:** P0  
**Theme:** Low-friction interaction

Show context-aware actions after assistant messages and on artifacts.

Create or harden:

```text
apps/chat-ui/action_chips.py
core/action-suggestions/
schemas/assistant-action.schema.json
schemas/action-event.schema.json
scripts/actions/generate_action_chips.py
docs/ux/assistant-action-chips.md
```

Acceptance criteria:

- Suggested actions include Create Plan, Convert to Workflow, Break into Tasks, Save as Skill, Schedule, Add to Knowledge, Run Dry-Run, Request Approval, Show Risks, Generate Report.
- Actions are explainable, reversible where possible, and audit logged.
- Actions respect governance policies and current workspace state.
- User can disable or hide noisy action types.

---

## UX-P0-008 — Add ambient assistant intelligence rail

**Status:** Open  
**Priority:** P0  
**Theme:** Proactive assistance

Add a non-intrusive insight rail for risks, gaps, stale knowledge, duplicates, missing approvals, cost issues, and automation opportunities.

Create or harden:

```text
core/assistant-insights/
apps/chat-ui/assistant_insights_rail.py
schemas/assistant-insight.schema.json
scripts/insights/generate_workspace_insights.py
docs/ux/assistant-insights-rail.md
```

Acceptance criteria:

- UI shows actionable suggestions without interrupting the main conversation.
- Insights include type, rationale, confidence, source, affected artifacts, and recommended action.
- Insight types include risk, gap, duplicate, stale knowledge, automation opportunity, missing approval, cost warning, connector issue, and skill improvement.
- User can convert an insight into a task, workflow, knowledge note, or approval request.
- Insights are suppressible and auditable.

---

## UX-P0-009 — Add interruptible workflow control UX

**Status:** Open  
**Priority:** P0  
**Theme:** Workflow control

Allow users to inspect and manipulate planned or running workflows conversationally and through UI controls.

Create or harden:

```text
apps/chat-ui/workflow_control_panel.py
core/workflow-control/
schemas/workflow-control-command.schema.json
scripts/workflows/pause_workflow.py
scripts/workflows/resume_workflow.py
scripts/workflows/modify_workflow_run.py
docs/architecture/interruptible-workflows.md
```

Acceptance criteria:

- User can pause, resume, cancel, skip step, retry step, branch workflow, inject context, add approval gate, or convert to dry-run.
- All workflow changes produce audit events.
- High-risk modifications require approval.
- Running workflow state is visible in chat UI.
- Assistant explains consequences before applying workflow changes.

---

## UX-P0-010 — Add execution streaming narration

**Status:** Open  
**Priority:** P0  
**Theme:** Execution transparency

Stream workflow execution progress into the UI in human-readable form.

Create or harden:

```text
core/execution-stream/
schemas/execution-stream-event.schema.json
apps/chat-ui/execution_stream.py
scripts/runtime/stream_workflow_events.py
docs/ux/execution-streaming.md
```

Acceptance criteria:

- UI streams step started, step completed, approval required, failure, retry, cost update, memory retrieval, and artifact creation events.
- Streaming events are correlated to workflow run IDs.
- User can expand any event for details.
- Streaming works for dry-run and live execution.
- Failures include actionable remediation.

---

## UX-P0-011 — Add unified operational timeline

**Status:** Open  
**Priority:** P0  
**Theme:** Auditability and continuity

Create a workspace timeline unifying conversation, plans, workflow runs, approvals, tasks, decisions, knowledge notes, schedules, and reports.

Create or harden:

```text
core/timeline/
schemas/timeline-event.schema.json
apps/chat-ui/timeline_view.py
scripts/timeline/build_workspace_timeline.py
docs/ux/operational-timeline.md
```

Acceptance criteria:

- Timeline shows chronological operational history.
- Events link to source artifacts and messages.
- Timeline supports filtering by project, workflow, skill, agent, approval status, risk level, and date.
- Timeline can be exported as an audit report.
- Timeline supports “what changed since last time?” summaries.

---

## UX-P0-012 — Add task and schedule center UX

**Status:** Open  
**Priority:** P0  
**Theme:** Operational management

Unify assistant-created tasks, schedules, recurring workflows, reminders, and automation triggers into a single operational center.

Create or harden:

```text
apps/chat-ui/task_schedule_center.py
core/task-schedule-center/
schemas/task-board-state.schema.json
schemas/recurring-automation.schema.json
docs/ux/task-schedule-center.md
```

Acceptance criteria:

- User can view tasks by status, priority, source, due date, assignee, and related artifact.
- User can convert plans into tasks and tasks into workflows.
- User can schedule workflows from conversation.
- Schedules show next run, last run, risk level, approval requirement, and failure state.
- User can pause, resume, edit, or archive schedules.

---

## UX-P0-013 — Add approval center UX

**Status:** Open  
**Priority:** P0  
**Theme:** Governed autonomy

Create a dedicated approval queue for HITL items, high-risk actions, workflow modifications, external writes, and scheduled automations.

Create or harden:

```text
apps/chat-ui/approval_center.py
core/approval-center/
schemas/approval-queue-state.schema.json
schemas/approval-decision-event.schema.json
scripts/governance/list_pending_approvals.py
scripts/governance/resolve_approval.py
docs/ux/approval-center.md
```

Acceptance criteria:

- User can approve, reject, edit, defer, or request more detail.
- Approval items show risk level, policy reason, source artifact, proposed action, expected side effects, and rollback options.
- Approval decisions are audit logged.
- Approval queue can be filtered by workspace, risk, workflow, skill, and due date.
- Scheduled automations show next approval requirement before execution.

---

## UX-P0-014 — Add workflow dry-run and simulation preview UX

**Status:** Open  
**Priority:** P0  
**Theme:** Trust before execution

Before workflow execution, show likely steps, costs, risks, approvals, dependencies, and failure points.

Create or harden:

```text
core/execution-simulation/
apps/chat-ui/workflow_preview.py
schemas/workflow-simulation.schema.json
scripts/workflows/simulate_workflow.py
docs/ux/workflow-simulation-preview.md
```

Acceptance criteria:

- Preview shows estimated runtime, token/cost estimate, risk level, external dependencies, required approvals, and likely failure points.
- User can approve, edit, or cancel from preview.
- Preview uses dry-run-safe behavior.
- Preview highlights missing credentials, missing inputs, policy gates, and quota issues.
- Simulation output is stored as an artifact linked to workflow version.

---

## UX-P0-015 — Add memory curation review flow

**Status:** Open  
**Priority:** P0  
**Theme:** Trustworthy memory

The assistant should propose durable knowledge instead of silently storing everything.

Create or harden:

```text
core/knowledge-curation-assistant/
core/knowledge-curation-assistant/SKILL.md
apps/chat-ui/knowledge_review_queue.py
schemas/knowledge-candidate.schema.json
schemas/knowledge-curation-decision.schema.json
scripts/memory/propose_knowledge_notes.py
scripts/memory/approve_knowledge_note.py
docs/ux/knowledge-curation-review.md
```

Acceptance criteria:

- Assistant proposes durable memories from conversations, workflow outputs, decisions, and reports.
- User can approve, edit, reject, merge, archive, or mark as temporary.
- Knowledge notes include source, confidence, scope, expiry/staleness, affected artifacts, and conflict status.
- Sensitive or regulated facts require explicit approval before durable persistence.
- Memory curation actions are audit logged.

---

# P1 — Advanced Workspace UX and Power User Capability

## UX-P1-001 — Add command palette for assistant operations

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Power navigation

Create a universal command palette for fast workspace navigation and assistant actions.

Create or harden:

```text
apps/chat-ui/command_palette.py
schemas/command-palette-action.schema.json
core/command-router/
docs/ux/command-palette.md
```

Acceptance criteria:

- `Ctrl/Cmd+K` opens command palette.
- Commands include create plan, create workflow, run skill, search knowledge, create task, schedule workflow, summarize workspace, show approvals, inspect memory, show active goals, and generate report.
- Commands are permission-aware and governance-aware.
- Command execution produces traceable assistant action events.

---

## UX-P1-002 — Add multi-agent visibility and collaboration UI

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Multi-agent transparency

Expose specialist agents and their contributions in the UI.

Create or harden:

```text
apps/chat-ui/agent_panel.py
core/agent-collaboration-ui/
schemas/agent-contribution.schema.json
schemas/agent-review.schema.json
docs/ux/multi-agent-visibility.md
```

Acceptance criteria:

- UI shows which agents contributed to a plan, workflow, review, or decision.
- Agent outputs are collapsible and attributable.
- User can ask for a specific agent review.
- Assistant can summarize consensus and disagreements.
- Agent contributions link to skills, evidence, and workflow steps.

---

## UX-P1-003 — Add AI memory inspector

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Memory transparency

Expose durable memory and knowledge in a user-controllable inspector.

Create or harden:

```text
apps/chat-ui/memory_inspector.py
core/memory-inspector/
schemas/memory-inspector-record.schema.json
scripts/memory/list_memory.py
scripts/memory/update_memory_record.py
docs/ux/memory-inspector.md
```

Acceptance criteria:

- User can view what the assistant remembers.
- Memory records show source, confidence, last updated, last used, affected artifacts, and expiry/staleness.
- User can edit, archive, pin, invalidate, or protect memory.
- Conflicting or stale memories are flagged.
- Memory changes are audit logged.

---

## UX-P1-004 — Add knowledge graph visualization

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Visual knowledge

Visualize relationships among projects, workflows, skills, tasks, decisions, APIs, clients, constraints, reports, and knowledge notes.

Create or harden:

```text
apps/chat-ui/knowledge_graph_view.py
scripts/knowledge/export_graph_view.py
schemas/knowledge-graph-view.schema.json
docs/ux/knowledge-graph-visualization.md
```

Acceptance criteria:

- User can navigate entity relationships visually.
- Graph nodes link back to artifacts and source conversations.
- Graph supports filtering by entity type and workspace.
- Graph highlights conflicts, stale nodes, high-risk dependencies, and reuse opportunities.
- Graph can export Mermaid/JSON.

---

## UX-P1-005 — Add workspace health dashboard

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Operational intelligence

Add operational health metrics for the workspace.

Create or harden:

```text
apps/dashboard/workspace_health.py
core/workspace-health/
schemas/workspace-health-report.schema.json
scripts/reports/generate_workspace_health.py
reports/workspace_health.md
reports/workspace_health.json
docs/ux/workspace-health.md
```

Acceptance criteria:

- Dashboard shows workflow success rate, failed runs, pending approvals, stale plans, open risks, knowledge conflicts, skill gaps, connector health, budget status, and automation opportunities.
- Assistant can summarize workspace health conversationally.
- Health findings can be converted into tasks or workflows.
- Health report is generated deterministically.

---

## UX-P1-006 — Add relationship-aware navigation

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Contextual navigation

Make every visible object navigable through its relationships.

Create or harden:

```text
core/relationship-index/
apps/chat-ui/relationship_drawer.py
schemas/artifact-relationship.schema.json
scripts/artifacts/build_relationship_index.py
docs/architecture/relationship-aware-navigation.md
```

Acceptance criteria:

- Every task, workflow, decision, memory, schedule, report, and approval shows related objects.
- User can navigate from task → source conversation → plan → workflow → execution run → decision → knowledge note.
- Broken or stale links are reported.
- Relationship index is queryable by assistant and UI.

---

## UX-P1-007 — Add operating modes

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Adaptive assistant behavior

Support assistant behavior modes for different user needs.

Create or harden:

```text
core/operating-modes/
schemas/assistant-operating-mode.schema.json
apps/chat-ui/operating_mode_selector.py
docs/reference/assistant-operating-modes.md
```

Modes:

```text
strategic
builder
research
operator
governance
autonomous
```

Acceptance criteria:

- Mode affects verbosity, planning depth, autonomy, risk sensitivity, and default suggested actions.
- Governance mode is conservative and approval-heavy.
- Builder mode favors concise execution.
- Research mode favors citations, evidence, and uncertainty.
- Autonomous mode requires explicit policy boundaries and approval configuration.

---

## UX-P1-008 — Add explainability affordances everywhere

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Trust and reasoning transparency

Add “why this?” explanations across plans, skills, workflows, tasks, memories, schedules, and insights.

Create or harden:

```text
core/explainability/
schemas/explanation.schema.json
apps/chat-ui/explanation_drawer.py
docs/ux/explainability-affordances.md
```

Acceptance criteria:

- User can expand rationale for selected skills, workflow steps, tasks, assumptions, memories, schedules, and recommendations.
- Explanations cite source artifact/message IDs where available.
- Explanations distinguish user-provided facts, inferred assumptions, policy requirements, and model recommendations.
- Explanation records are concise and safe to show.

---

## UX-P1-009 — Add reusable operational templates

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Reuse and scale

Allow users to save recurring operating patterns as templates.

Create or harden:

```text
core/operational-templates/
schemas/operational-template.schema.json
apps/chat-ui/template_library.py
scripts/templates/create_operational_template.py
docs/ux/operational-templates.md
```

Acceptance criteria:

- User can save plans, workflows, task sets, agent teams, approval chains, research sessions, and reports as reusable templates.
- Templates support variables and default assumptions.
- Templates can be instantiated into a workspace.
- Templates are versioned and validated.

---

## UX-P1-010 — Add adaptive UI complexity

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Progressive disclosure

Support beginner and advanced UI modes.

Create or harden:

```text
apps/chat-ui/ui_complexity.py
schemas/ui-preference.schema.json
docs/ux/adaptive-complexity.md
```

Acceptance criteria:

- Beginner view emphasizes chat, plans, tasks, and simple approvals.
- Advanced view exposes DAGs, telemetry, token budgets, dependency graphs, memory inspector, execution traces, and governance details.
- User can switch views without losing state.
- Assistant respects UI complexity in responses and suggested actions.

---

## UX-P1-011 — Add natural language artifact editing

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Conversational control

Allow users to edit plans, workflows, tasks, schedules, knowledge, and templates conversationally.

Create or harden:

```text
core/natural-language-editing/
scripts/artifacts/apply_natural_language_edit.py
schemas/artifact-edit-command.schema.json
schemas/artifact-patch.schema.json
docs/architecture/natural-language-artifact-editing.md
```

Acceptance criteria:

- User can say “move deployment before QA,” “make this weekly,” “split this workflow,” “use cheaper models,” or “archive old plans.”
- Assistant proposes a patch before applying destructive or high-risk edits.
- Patches are versioned and reversible.
- Edits preserve source links and audit traceability.

---

## UX-P1-012 — Add advanced search across workspace and knowledge

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Findability

Implement unified search across conversations, artifacts, workflows, tasks, schedules, knowledge, decisions, reports, and run history.

Create or harden:

```text
core/workspace-search/
apps/chat-ui/search_view.py
schemas/search-result.schema.json
scripts/search/build_workspace_index.py
scripts/search/query_workspace.py
docs/ux/workspace-search.md
```

Acceptance criteria:

- Search supports semantic and keyword queries.
- Search results include source type, snippet, relevance, timestamp, and relationships.
- User can filter by artifact type, date, workspace, project, skill, workflow, agent, risk level, and status.
- Assistant can use search results to answer “what did we decide?” or “find the ERP research workflow.”

---

## UX-P1-013 — Add inbox/triage experience

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Operational triage

Create an inbox for unprocessed conversation items, imported documents, connector events, failed runs, suggested tasks, and knowledge candidates.

Create or harden:

```text
apps/chat-ui/inbox.py
core/triage-inbox/
schemas/inbox-item.schema.json
scripts/inbox/generate_inbox_items.py
scripts/inbox/triage_item.py
docs/ux/triage-inbox.md
```

Acceptance criteria:

- Inbox items include type, source, urgency, suggested action, and owner.
- User can convert inbox items into tasks, knowledge notes, workflows, approvals, or archive them.
- Assistant can batch-triage low-risk items with approval.
- Inbox can group duplicates and related items.

---

## UX-P1-014 — Add workspace onboarding and guided setup

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Time-to-value

Create a guided first-run experience that sets up the workspace without forcing rigid workflow intake.

Create or harden:

```text
apps/chat-ui/onboarding.py
schemas/onboarding-profile.schema.json
company_templates/default/
docs/ux/workspace-onboarding.md
```

Acceptance criteria:

- User can select goals: SDLC, consulting, business ops, research, sales, governance, local automation, or all-in-one.
- Setup recommends starter workflows, skills, dashboards, schedules, and knowledge categories.
- User can skip onboarding and start chatting immediately.
- Onboarding creates editable assumptions and workspace defaults.

---

## UX-P1-015 — Add notification and attention management

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Focus and alerts

Add notification rules for approvals, failed workflows, stale tasks, schedule misfires, knowledge conflicts, and budget/rate-limit warnings.

Create or harden:

```text
core/notifications/
apps/chat-ui/notification_center.py
schemas/notification.schema.json
schemas/notification-preference.schema.json
scripts/notifications/generate_notifications.py
docs/ux/notification-center.md
```

Acceptance criteria:

- Notifications are grouped by urgency and workspace.
- User can mute, snooze, resolve, or convert notifications into tasks.
- Notifications include recommended action and source.
- Critical governance or failed execution notifications cannot be silently hidden without audit.

---

## UX-P1-016 — Add model/runtime selection UX

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Runtime control

Expose model/runtime routing decisions in a safe, understandable UI.

Create or harden:

```text
apps/chat-ui/runtime_selector.py
core/runtime-selection-ui/
schemas/runtime-choice.schema.json
docs/ux/model-runtime-selection.md
```

Acceptance criteria:

- User can choose default runtime mode: local-first, cloud-quality, cheapest, fastest, private, or governed.
- UI shows expected cost, latency, privacy, and quality tradeoffs.
- High-risk workflows can enforce approved model/runtime policies.
- Assistant can recommend runtime changes with rationale.

---

## UX-P1-017 — Add cost, token, and quota UX controls

**Status:** Completed (2026-05-12)  
**Priority:** P1  
**Theme:** Budget control

Expose budget, token, rate-limit, and quota management inside chat and dashboard.

Create or harden:

```text
apps/chat-ui/cost_quota_panel.py
schemas/user-budget-preference.schema.json
schemas/workflow-budget-guard.schema.json
scripts/reports/generate_cost_quota_summary.py
docs/ux/cost-quota-controls.md
```

Acceptance criteria:

- UI shows estimated cost before execution and actual cost after execution.
- User can set budget caps per workspace, workflow, schedule, model, or connector.
- Assistant warns before expensive actions.
- Workflows can degrade to cheaper models, cached context, or dry-run mode when budget caps are approached.

---

# P2 — Collaboration, Enterprise, and Governance UX

## UX-P2-001 — Add multi-user collaboration and roles UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Team collaboration

Support multiple users, roles, ownership, comments, approvals, and assignments.

Create or harden:

```text
core/collaboration/
apps/chat-ui/collaboration_panel.py
schemas/workspace-member.schema.json
schemas/comment.schema.json
schemas/role-permission.schema.json
docs/ux/team-collaboration.md
```

Acceptance criteria:

- Users can assign tasks, approvals, plans, workflows, and knowledge reviews.
- Comments can attach to artifacts and timeline events.
- Roles control who can approve, execute, edit memory, schedule automations, and change policies.
- Activity is audit logged by user.

---

## UX-P2-002 — Add client/project portfolio UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Consulting and multi-project operations

Create a portfolio view for multiple clients, projects, initiatives, and workspaces.

Create or harden:

```text
apps/dashboard/portfolio_view.py
schemas/client.schema.json
schemas/project.schema.json
schemas/initiative.schema.json
scripts/reports/generate_portfolio_status.py
docs/ux/portfolio-view.md
```

Acceptance criteria:

- User can view all clients/projects with status, health, risks, tasks, upcoming approvals, and active workflows.
- Assistant can generate portfolio summaries.
- Projects link to workspaces, artifacts, schedules, reports, and knowledge.
- Portfolio view supports consulting use cases and internal company operations.

---

## UX-P2-003 — Add report builder UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Communication and executive reporting

Allow users to generate reports from workspace state, timeline, tasks, workflows, and knowledge.

Create or harden:

```text
apps/chat-ui/report_builder.py
core/report-builder/
schemas/report-template.schema.json
schemas/generated-report.schema.json
scripts/reports/build_workspace_report.py
docs/ux/report-builder.md
```

Acceptance criteria:

- Report types include executive summary, project status, workflow run summary, risk report, approval audit, client update, skill gap report, cost report, and knowledge digest.
- Reports can be generated from templates.
- Reports cite source artifacts and timeline events.
- User can export Markdown, PDF-ready Markdown, JSON, and HTML.

---

## UX-P2-004 — Add policy authoring and governance UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Governance usability

Provide a UI for creating, editing, testing, and explaining governance policies.

Create or harden:

```text
apps/dashboard/policy_studio.py
core/policy-authoring-ui/
schemas/policy-draft.schema.json
schemas/policy-test-case.schema.json
scripts/governance/simulate_policy.py
docs/ux/policy-studio.md
```

Acceptance criteria:

- User can author policies in guided natural language and structured form.
- Policy simulation shows allowed, blocked, approval-required, and warning outcomes.
- Policies link to skills, workflows, actions, roles, and risk levels.
- Policy changes require approval and produce audit trail.

---

## UX-P2-005 — Add connector setup wizard UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Integration usability

Create guided connector setup, health testing, permissions review, and dry-run validation.

Create or harden:

```text
apps/dashboard/connector_wizard.py
schemas/connector-setup-state.schema.json
scripts/connectors/test_connector_setup.py
docs/ux/connector-setup-wizard.md
```

Acceptance criteria:

- Wizard supports credentials, scopes, dry-run tests, rate-limit policy, and permissions review.
- Connector setup explains what the assistant can and cannot do.
- Missing credentials and failing health checks produce actionable remediation.
- Connector permissions are visible in approval center and workflow previews.

---

## UX-P2-006 — Add data import and document ingestion UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Knowledge onboarding

Allow users to import files, notes, docs, spreadsheets, markdown, run logs, and exported data into workspace knowledge.

Create or harden:

```text
apps/chat-ui/import_center.py
core/document-ingestion-ui/
schemas/import-job.schema.json
schemas/imported-source.schema.json
scripts/imports/run_import_job.py
docs/ux/import-center.md
```

Acceptance criteria:

- User can upload/import documents and choose destination: knowledge, project, workflow, skill, or report source.
- Assistant summarizes imported content and proposes extracted tasks/decisions/knowledge notes.
- Import jobs show status, errors, source metadata, and provenance.
- Sensitive imports require classification and policy checks.

---

## UX-P2-007 — Add accessibility and keyboard-first UX pass

**Status:** Completed  
**Priority:** P2  
**Theme:** Accessibility

Ensure chat, workspace, command palette, artifact panels, timeline, graph, and dashboards are accessible and keyboard-friendly.

Create or harden:

```text
docs/ux/accessibility-standard.md
apps/chat-ui/accessibility_checks.py
scripts/validation/validate_accessibility_metadata.py
```

Acceptance criteria:

- UI supports keyboard navigation for core actions.
- Components have accessible labels and semantic structure.
- Color, focus, contrast, and screen-reader support are documented.
- Accessibility checks are part of release readiness.

---

## UX-P2-008 — Add mobile/tablet responsive UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Responsive use

Make the assistant workspace usable on smaller screens.

Create or harden:

```text
apps/chat-ui/responsive_layout.py
docs/ux/responsive-layout.md
```

Acceptance criteria:

- Chat, tasks, approvals, timeline, and artifacts are usable on tablet/mobile widths.
- Complex panels collapse into drawers or tabs.
- High-priority approvals and tasks remain easy to access.
- Execution streaming remains readable on small screens.

---

## UX-P2-009 — Add audit and compliance evidence UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Compliance operations

Make governance evidence, approvals, policy decisions, and execution records easy to inspect and export.

Create or harden:

```text
apps/dashboard/evidence_center.py
core/evidence-center/
schemas/evidence-item.schema.json
schemas/evidence-pack.schema.json
scripts/governance/build_evidence_pack.py
docs/ux/evidence-center.md
```

Acceptance criteria:

- Evidence center shows approvals, policy decisions, workflow runs, memory changes, external actions, and reports.
- User can build evidence packs by date, workspace, client, workflow, policy, or regulation.
- Evidence records include source links, timestamps, actor, action, rationale, and outcome.
- Export supports Markdown/JSON/HTML.

---

## UX-P2-010 — Add marketplace/template discovery UX

**Status:** Completed  
**Priority:** P2  
**Theme:** Reuse and distribution

Expose reusable skills, workflows, templates, dashboards, and company packs in a discoverable catalog.

Create or harden:

```text
apps/chat-ui/catalog.py
core/template-catalog/
schemas/catalog-item.schema.json
schemas/catalog-install-event.schema.json
scripts/catalog/build_catalog.py
docs/ux/catalog-marketplace.md
```

Acceptance criteria:

- Catalog supports skills, workflows, plans, templates, reports, dashboards, and company packs.
- Items show description, maturity, dependencies, governance level, install impact, and examples.
- User can preview before install.
- Installed items are versioned and linked to workspace.

---

# P3 — Differentiating UX and Advanced Intelligence

## UX-P3-001 — Add “what should I do next?” operating coach

**Status:** Open  
**Priority:** P3  
**Theme:** Executive assistance

Create a coaching layer that recommends the next best action across workspace state.

Create or harden:

```text
core/operating-coach/
apps/chat-ui/next_best_action.py
schemas/next-best-action.schema.json
scripts/coach/generate_next_best_actions.py
docs/ux/operating-coach.md
```

Acceptance criteria:

- Assistant recommends next actions based on goals, deadlines, risks, blocked tasks, stale plans, failed workflows, and opportunities.
- Recommendations include expected impact, effort, urgency, confidence, and source.
- User can accept, defer, dismiss, or convert recommendations into tasks/workflows.

---

## UX-P3-002 — Add strategic roadmap and initiative planning UX

**Status:** Open  
**Priority:** P3  
**Theme:** Strategy execution

Support long-horizon initiatives, milestones, OKRs, dependencies, and roadmap planning.

Create or harden:

```text
apps/dashboard/roadmap_view.py
core/roadmap-planning/
schemas/initiative-roadmap.schema.json
schemas/milestone.schema.json
schemas/okr.schema.json
docs/ux/roadmap-planning.md
```

Acceptance criteria:

- User can create initiatives, milestones, OKRs, and roadmap items from conversation.
- Roadmap links to tasks, workflows, reports, risks, and decisions.
- Assistant can summarize progress and recommend reprioritization.
- Roadmap supports weekly/monthly/quarterly views.

---

## UX-P3-003 — Add workflow comparison and optimization UX

**Status:** Open  
**Priority:** P3  
**Theme:** Continuous improvement

Let users compare workflow versions, costs, risks, quality, and outcomes.

Create or harden:

```text
apps/chat-ui/workflow_compare.py
core/workflow-optimization-ui/
schemas/workflow-comparison.schema.json
scripts/workflows/compare_workflows.py
scripts/workflows/recommend_workflow_optimizations.py
docs/ux/workflow-comparison.md
```

Acceptance criteria:

- User can compare workflow versions side-by-side.
- Comparison includes steps, skills, cost, runtime, risk, outputs, failures, approvals, and quality signals.
- Assistant recommends simplification, parallelization, skill replacements, caching, or governance improvements.
- Recommendations can become tasks or proposed workflow patches.

---

## UX-P3-004 — Add skill gap and skill improvement UX loop

**Status:** Open  
**Priority:** P3  
**Theme:** Self-improving system

Expose skill gaps, overlaps, maturity, usage, and improvement opportunities in the UI.

Create or harden:

```text
apps/dashboard/skill_gap_view.py
core/skill-improvement-ui/
schemas/skill-gap-finding.schema.json
schemas/skill-improvement-proposal.schema.json
scripts/skills/generate_skill_improvement_backlog.py
docs/ux/skill-improvement-loop.md
```

Acceptance criteria:

- UI shows missing skills, weak skills, overlapping skills, stale skills, and high-value improvement opportunities.
- Assistant can propose improving an existing skill or creating a new skill.
- Skill improvement proposals include rationale, expected impact, dependencies, tests, and governance implications.
- Approved proposals become backlog tasks or skill scaffolds.

---

## UX-P3-005 — Add learning loop and lessons-learned UX

**Status:** Open  
**Priority:** P3  
**Theme:** Institutional learning

After workflows, projects, incidents, or research sessions, capture reusable lessons.

Create or harden:

```text
apps/chat-ui/lessons_learned.py
core/lessons-learned-ui/
schemas/lesson-learned.schema.json
scripts/learning/extract_lessons_learned.py
docs/ux/lessons-learned.md
```

Acceptance criteria:

- Assistant proposes lessons after completed workflows or incidents.
- Lessons can update skills, templates, policies, knowledge, or future workflow defaults.
- User can approve, edit, reject, or scope lessons.
- Lessons link to evidence and outcomes.

---

## UX-P3-006 — Add scenario simulation and decision workspace

**Status:** Open  
**Priority:** P3  
**Theme:** Decision intelligence

Create a decision workspace for comparing options, assumptions, risks, scenarios, and recommendations.

Create or harden:

```text
apps/chat-ui/decision_workspace.py
core/decision-workspace/
schemas/decision-option.schema.json
schemas/scenario.schema.json
schemas/decision-record.schema.json
scripts/decision/simulate_scenarios.py
docs/ux/decision-workspace.md
```

Acceptance criteria:

- User can compare options with pros, cons, risks, assumptions, costs, and expected outcomes.
- Assistant can generate scenarios and sensitivity analysis.
- Final decisions become durable decision records.
- Decisions link to plans, workflows, tasks, and knowledge.

---

## UX-P3-007 — Add personal productivity command layer

**Status:** Open  
**Priority:** P3  
**Theme:** Daily operator productivity

Support daily planning, meeting notes, follow-ups, reminders, recaps, and personal operating rhythm.

Create or harden:

```text
apps/chat-ui/daily_command_center.py
core/personal-productivity/
schemas/daily-plan.schema.json
schemas/follow-up.schema.json
scripts/productivity/generate_daily_plan.py
scripts/productivity/generate_end_of_day_recap.py
docs/ux/personal-productivity.md
```

Acceptance criteria:

- User can ask for daily priorities based on workspace state.
- Assistant can create follow-ups, reminders, task updates, and recaps from conversations or meetings.
- Daily plan links to tasks, schedules, workflows, and approvals.
- End-of-day recap captures progress, blockers, and next actions.

---

## UX-P3-008 — Add meeting capture and action extraction UX

**Status:** Open  
**Priority:** P3  
**Theme:** Meeting intelligence

Support meeting transcript ingestion, summary, decisions, tasks, follow-ups, and knowledge extraction.

Create or harden:

```text
apps/chat-ui/meeting_capture.py
core/meeting-intelligence/
schemas/meeting-record.schema.json
schemas/meeting-action-item.schema.json
scripts/meetings/process_meeting_transcript.py
docs/ux/meeting-intelligence.md
```

Acceptance criteria:

- User can paste or import transcript/notes.
- Assistant extracts summary, decisions, tasks, risks, open questions, and follow-ups.
- Meeting outputs can update plans, tasks, knowledge, and workflows.
- Follow-up emails or reports can be drafted with approval.

---

## UX-P3-009 — Add voice and multimodal interaction roadmap

**Status:** Open  
**Priority:** P3  
**Theme:** Multimodal UX

Define and scaffold future voice/image/document interaction support.

Create or harden:

```text
docs/ux/multimodal-roadmap.md
schemas/multimodal-input.schema.json
core/multimodal-ingestion/
```

Acceptance criteria:

- Roadmap covers voice commands, audio notes, screenshots, diagrams, whiteboards, documents, and images.
- Multimodal inputs map to artifacts and knowledge with provenance.
- Safety and privacy boundaries are documented.
- Initial schema supports future implementation.

---

## UX-P3-010 — Add UX telemetry and product analytics

**Status:** Open  
**Priority:** P3  
**Theme:** Product improvement

Track UX friction, adoption, task completion, and assistant usefulness.

Create or harden:

```text
core/ux-telemetry/
schemas/ux-telemetry-event.schema.json
scripts/reports/generate_ux_telemetry_report.py
reports/ux_telemetry.md
reports/ux_telemetry.json
docs/ux/ux-telemetry.md
```

Acceptance criteria:

- Track action chip usage, abandoned workflows, repeated clarification loops, approval friction, failed searches, and manual overrides.
- Telemetry avoids sensitive content by default.
- Reports identify top UX friction points and improvement opportunities.
- UX metrics can feed skill/workflow improvement backlog.

---

# 2. Suggested Development Order

## Phase 1 — Make chat fluid and useful

1. UX-P0-002 Adaptive conversation orchestration
2. UX-P0-003 Visible cognition panel
3. UX-P0-004 Artifact-first workspace model
4. UX-P0-006 Plan-first workflow experience
5. UX-P0-007 Assistant action chips

## Phase 2 — Make work persistent and operational

1. UX-P0-001 Persistent assistant workspace
2. UX-P0-005 Conversation-to-structure extraction
3. UX-P0-011 Operational timeline
4. UX-P0-012 Task and schedule center
5. UX-P0-015 Memory curation review flow

## Phase 3 — Make execution trustworthy

1. UX-P0-014 Workflow dry-run and simulation preview
2. UX-P0-010 Execution streaming narration
3. UX-P0-009 Interruptible workflow control UX
4. UX-P0-013 Approval center UX
5. UX-P1-008 Explainability affordances

## Phase 4 — Make the workspace powerful

1. UX-P1-001 Command palette
2. UX-P1-003 Memory inspector
3. UX-P1-004 Knowledge graph visualization
4. UX-P1-005 Workspace health dashboard
5. UX-P1-006 Relationship-aware navigation

## Phase 5 — Make it enterprise/team ready

1. UX-P2-001 Multi-user collaboration and roles
2. UX-P2-002 Client/project portfolio UX
3. UX-P2-004 Policy authoring and governance UX
4. UX-P2-005 Connector setup wizard UX
5. UX-P2-009 Audit and compliance evidence UX

## Phase 6 — Differentiate with intelligence loops

1. UX-P3-001 Operating coach
2. UX-P3-003 Workflow comparison and optimization
3. UX-P3-004 Skill gap and skill improvement UX loop
4. UX-P3-005 Lessons-learned UX
5. UX-P3-006 Scenario simulation and decision workspace

---

# 3. Definition of Done for UX Backlog Items

Each UX backlog item should include:

- Schema updates where state is persisted.
- CLI/script support where UI invokes backend behavior.
- UI component or documented UI placeholder.
- Audit/provenance model for user-visible changes.
- Governance checks for risky actions.
- Tests or validation scripts.
- Documentation under `docs/ux/` or `docs/architecture/`.
- Example fixture showing expected input/output.

---

# 4. UX Anti-Patterns to Avoid

- Do not force fixed intake questions before creating drafts.
- Do not hide assumptions from the user.
- Do not make workflows feel irreversible.
- Do not silently persist memory without review for important facts.
- Do not require users to understand skill internals before getting value.
- Do not bury approvals in logs.
- Do not make every chat response generate a workflow.
- Do not expose private chain-of-thought; expose concise working state instead.
- Do not create powerful automation without simulation, approval, and rollback paths.

---

# 5. Target Experience Examples

## Example 1 — Fluid workflow creation

User:

```text
Create a repeatable process for researching ERP APIs for consulting prospects.
```

Assistant should:

1. Draft a plan immediately.
2. Show assumptions.
3. Suggest action chips: Create Workflow, Break Into Tasks, Save as Template, Add Knowledge, Schedule Weekly.
4. Offer to run a dry-run preview.
5. Store the final workflow as a reusable operational template.

## Example 2 — Resume prior initiative

User:

```text
Continue the Aptean ERP API work.
```

Assistant should:

1. Retrieve related workspace context.
2. Summarize last state.
3. Show open tasks, decisions, and blockers.
4. Recommend next best action.
5. Ask only if multiple paths are materially different.

## Example 3 — Governed automation

User:

```text
Run the vendor outreach workflow every Monday.
```

Assistant should:

1. Create a schedule draft.
2. Show risk and approval requirements.
3. Preview side effects.
4. Require approval for outbound communication.
5. Add schedule to Task & Schedule Center.

---

# 6. Strategic Outcome

Completing this backlog transforms Apotheon from a powerful but workflow-centric skill system into a user-friendly AI operating environment that supports:

- natural conversation
- visible planning
- artifact creation
- task and schedule management
- governed execution
- knowledge curation
- enterprise auditability
- multi-agent collaboration
- continuous self-improvement

The intended result is an assistant that feels less like a tool launcher and more like an operational partner.

---

## Open/Incomplete Work Task Tracker (Generated 2026-05-12)

The following implementation tasks were generated from all backlog items with `Status: Open` or otherwise incomplete state. Mark checkboxes as work progresses and update each source item status when complete.

### UX-P0-001 — Build persistent assistant workspace
- [ ] Define implementation design and file-level change plan for UX-P0-001.
- [ ] Implement/create the required files/components listed in UX-P0-001.
- [ ] Validate acceptance criteria for UX-P0-001 with tests or documented checks.
- [ ] Update `UX-P0-001` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-002 — Replace rigid intake with adaptive conversation orchestration
- [ ] Define implementation design and file-level change plan for UX-P0-002.
- [ ] Implement/create the required files/components listed in UX-P0-002.
- [ ] Validate acceptance criteria for UX-P0-002 with tests or documented checks.
- [ ] Update `UX-P0-002` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-003 — Add visible cognition panel
- [ ] Define implementation design and file-level change plan for UX-P0-003.
- [ ] Implement/create the required files/components listed in UX-P0-003.
- [ ] Validate acceptance criteria for UX-P0-003 with tests or documented checks.
- [ ] Update `UX-P0-003` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-004 — Add artifact-first workspace model
- [ ] Define implementation design and file-level change plan for UX-P0-004.
- [ ] Implement/create the required files/components listed in UX-P0-004.
- [ ] Validate acceptance criteria for UX-P0-004 with tests or documented checks.
- [ ] Update `UX-P0-004` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-005 — Add conversation-to-structure extraction
- [ ] Define implementation design and file-level change plan for UX-P0-005.
- [ ] Implement/create the required files/components listed in UX-P0-005.
- [ ] Validate acceptance criteria for UX-P0-005 with tests or documented checks.
- [ ] Update `UX-P0-005` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-006 — Build plan-first workflow experience
- [ ] Define implementation design and file-level change plan for UX-P0-006.
- [ ] Implement/create the required files/components listed in UX-P0-006.
- [ ] Validate acceptance criteria for UX-P0-006 with tests or documented checks.
- [ ] Update `UX-P0-006` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-007 — Add assistant action chips and quick actions
- [ ] Define implementation design and file-level change plan for UX-P0-007.
- [ ] Implement/create the required files/components listed in UX-P0-007.
- [ ] Validate acceptance criteria for UX-P0-007 with tests or documented checks.
- [ ] Update `UX-P0-007` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-008 — Add ambient assistant intelligence rail
- [ ] Define implementation design and file-level change plan for UX-P0-008.
- [ ] Implement/create the required files/components listed in UX-P0-008.
- [ ] Validate acceptance criteria for UX-P0-008 with tests or documented checks.
- [ ] Update `UX-P0-008` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-009 — Add interruptible workflow control UX
- [ ] Define implementation design and file-level change plan for UX-P0-009.
- [ ] Implement/create the required files/components listed in UX-P0-009.
- [ ] Validate acceptance criteria for UX-P0-009 with tests or documented checks.
- [ ] Update `UX-P0-009` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-010 — Add execution streaming narration
- [ ] Define implementation design and file-level change plan for UX-P0-010.
- [ ] Implement/create the required files/components listed in UX-P0-010.
- [ ] Validate acceptance criteria for UX-P0-010 with tests or documented checks.
- [ ] Update `UX-P0-010` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-011 — Add unified operational timeline
- [ ] Define implementation design and file-level change plan for UX-P0-011.
- [ ] Implement/create the required files/components listed in UX-P0-011.
- [ ] Validate acceptance criteria for UX-P0-011 with tests or documented checks.
- [ ] Update `UX-P0-011` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-012 — Add task and schedule center UX
- [ ] Define implementation design and file-level change plan for UX-P0-012.
- [ ] Implement/create the required files/components listed in UX-P0-012.
- [ ] Validate acceptance criteria for UX-P0-012 with tests or documented checks.
- [ ] Update `UX-P0-012` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-013 — Add approval center UX
- [ ] Define implementation design and file-level change plan for UX-P0-013.
- [ ] Implement/create the required files/components listed in UX-P0-013.
- [ ] Validate acceptance criteria for UX-P0-013 with tests or documented checks.
- [ ] Update `UX-P0-013` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-014 — Add workflow dry-run and simulation preview UX
- [ ] Define implementation design and file-level change plan for UX-P0-014.
- [ ] Implement/create the required files/components listed in UX-P0-014.
- [ ] Validate acceptance criteria for UX-P0-014 with tests or documented checks.
- [ ] Update `UX-P0-014` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P0-015 — Add memory curation review flow
- [ ] Define implementation design and file-level change plan for UX-P0-015.
- [ ] Implement/create the required files/components listed in UX-P0-015.
- [ ] Validate acceptance criteria for UX-P0-015 with tests or documented checks.
- [ ] Update `UX-P0-015` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-001 — Add command palette for assistant operations
- [ ] Define implementation design and file-level change plan for UX-P1-001.
- [ ] Implement/create the required files/components listed in UX-P1-001.
- [ ] Validate acceptance criteria for UX-P1-001 with tests or documented checks.
- [ ] Update `UX-P1-001` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-002 — Add multi-agent visibility and collaboration UI
- [ ] Define implementation design and file-level change plan for UX-P1-002.
- [ ] Implement/create the required files/components listed in UX-P1-002.
- [ ] Validate acceptance criteria for UX-P1-002 with tests or documented checks.
- [ ] Update `UX-P1-002` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-003 — Add AI memory inspector
- [ ] Define implementation design and file-level change plan for UX-P1-003.
- [ ] Implement/create the required files/components listed in UX-P1-003.
- [ ] Validate acceptance criteria for UX-P1-003 with tests or documented checks.
- [ ] Update `UX-P1-003` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-004 — Add knowledge graph visualization
- [ ] Define implementation design and file-level change plan for UX-P1-004.
- [ ] Implement/create the required files/components listed in UX-P1-004.
- [ ] Validate acceptance criteria for UX-P1-004 with tests or documented checks.
- [ ] Update `UX-P1-004` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-005 — Add workspace health dashboard
- [ ] Define implementation design and file-level change plan for UX-P1-005.
- [ ] Implement/create the required files/components listed in UX-P1-005.
- [ ] Validate acceptance criteria for UX-P1-005 with tests or documented checks.
- [ ] Update `UX-P1-005` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-006 — Add relationship-aware navigation
- [ ] Define implementation design and file-level change plan for UX-P1-006.
- [ ] Implement/create the required files/components listed in UX-P1-006.
- [ ] Validate acceptance criteria for UX-P1-006 with tests or documented checks.
- [ ] Update `UX-P1-006` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-007 — Add operating modes
- [ ] Define implementation design and file-level change plan for UX-P1-007.
- [ ] Implement/create the required files/components listed in UX-P1-007.
- [ ] Validate acceptance criteria for UX-P1-007 with tests or documented checks.
- [ ] Update `UX-P1-007` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-008 — Add explainability affordances everywhere
- [ ] Define implementation design and file-level change plan for UX-P1-008.
- [ ] Implement/create the required files/components listed in UX-P1-008.
- [ ] Validate acceptance criteria for UX-P1-008 with tests or documented checks.
- [ ] Update `UX-P1-008` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-009 — Add reusable operational templates
- [ ] Define implementation design and file-level change plan for UX-P1-009.
- [ ] Implement/create the required files/components listed in UX-P1-009.
- [ ] Validate acceptance criteria for UX-P1-009 with tests or documented checks.
- [ ] Update `UX-P1-009` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-010 — Add adaptive UI complexity
- [ ] Define implementation design and file-level change plan for UX-P1-010.
- [ ] Implement/create the required files/components listed in UX-P1-010.
- [ ] Validate acceptance criteria for UX-P1-010 with tests or documented checks.
- [ ] Update `UX-P1-010` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-011 — Add natural language artifact editing
- [ ] Define implementation design and file-level change plan for UX-P1-011.
- [ ] Implement/create the required files/components listed in UX-P1-011.
- [ ] Validate acceptance criteria for UX-P1-011 with tests or documented checks.
- [ ] Update `UX-P1-011` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-012 — Add advanced search across workspace and knowledge
- [ ] Define implementation design and file-level change plan for UX-P1-012.
- [ ] Implement/create the required files/components listed in UX-P1-012.
- [ ] Validate acceptance criteria for UX-P1-012 with tests or documented checks.
- [ ] Update `UX-P1-012` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-013 — Add inbox/triage experience
- [ ] Define implementation design and file-level change plan for UX-P1-013.
- [ ] Implement/create the required files/components listed in UX-P1-013.
- [ ] Validate acceptance criteria for UX-P1-013 with tests or documented checks.
- [ ] Update `UX-P1-013` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-014 — Add workspace onboarding and guided setup
- [ ] Define implementation design and file-level change plan for UX-P1-014.
- [ ] Implement/create the required files/components listed in UX-P1-014.
- [ ] Validate acceptance criteria for UX-P1-014 with tests or documented checks.
- [ ] Update `UX-P1-014` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-015 — Add notification and attention management
- [ ] Define implementation design and file-level change plan for UX-P1-015.
- [ ] Implement/create the required files/components listed in UX-P1-015.
- [ ] Validate acceptance criteria for UX-P1-015 with tests or documented checks.
- [ ] Update `UX-P1-015` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-016 — Add model/runtime selection UX
- [ ] Define implementation design and file-level change plan for UX-P1-016.
- [ ] Implement/create the required files/components listed in UX-P1-016.
- [ ] Validate acceptance criteria for UX-P1-016 with tests or documented checks.
- [ ] Update `UX-P1-016` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P1-017 — Add cost, token, and quota UX controls
- [ ] Define implementation design and file-level change plan for UX-P1-017.
- [ ] Implement/create the required files/components listed in UX-P1-017.
- [ ] Validate acceptance criteria for UX-P1-017 with tests or documented checks.
- [ ] Update `UX-P1-017` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-001 — Add multi-user collaboration and roles UX
- [x] Define implementation design and file-level change plan for UX-P2-001.
- [x] Implement/create the required files/components listed in UX-P2-001.
- [x] Validate acceptance criteria for UX-P2-001 with tests or documented checks.
- [x] Update `UX-P2-001` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-002 — Add client/project portfolio UX
- [x] Define implementation design and file-level change plan for UX-P2-002.
- [x] Implement/create the required files/components listed in UX-P2-002.
- [x] Validate acceptance criteria for UX-P2-002 with tests or documented checks.
- [x] Update `UX-P2-002` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-003 — Add report builder UX
- [x] Define implementation design and file-level change plan for UX-P2-003.
- [x] Implement/create the required files/components listed in UX-P2-003.
- [x] Validate acceptance criteria for UX-P2-003 with tests or documented checks.
- [x] Update `UX-P2-003` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-004 — Add policy authoring and governance UX
- [x] Define implementation design and file-level change plan for UX-P2-004.
- [x] Implement/create the required files/components listed in UX-P2-004.
- [x] Validate acceptance criteria for UX-P2-004 with tests or documented checks.
- [x] Update `UX-P2-004` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-005 — Add connector setup wizard UX
- [x] Define implementation design and file-level change plan for UX-P2-005.
- [x] Implement/create the required files/components listed in UX-P2-005.
- [x] Validate acceptance criteria for UX-P2-005 with tests or documented checks.
- [x] Update `UX-P2-005` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-006 — Add data import and document ingestion UX
- [x] Define implementation design and file-level change plan for UX-P2-006.
- [x] Implement/create the required files/components listed in UX-P2-006.
- [x] Validate acceptance criteria for UX-P2-006 with tests or documented checks.
- [x] Update `UX-P2-006` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-007 — Add accessibility and keyboard-first UX pass
- [x] Define implementation design and file-level change plan for UX-P2-007.
- [x] Implement/create the required files/components listed in UX-P2-007.
- [x] Validate acceptance criteria for UX-P2-007 with tests or documented checks.
- [x] Update `UX-P2-007` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-008 — Add mobile/tablet responsive UX
- [x] Define implementation design and file-level change plan for UX-P2-008.
- [x] Implement/create the required files/components listed in UX-P2-008.
- [x] Validate acceptance criteria for UX-P2-008 with tests or documented checks.
- [x] Update `UX-P2-008` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-009 — Add audit and compliance evidence UX
- [x] Define implementation design and file-level change plan for UX-P2-009.
- [x] Implement/create the required files/components listed in UX-P2-009.
- [x] Validate acceptance criteria for UX-P2-009 with tests or documented checks.
- [x] Update `UX-P2-009` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P2-010 — Add marketplace/template discovery UX
- [x] Define implementation design and file-level change plan for UX-P2-010.
- [x] Implement/create the required files/components listed in UX-P2-010.
- [x] Validate acceptance criteria for UX-P2-010 with tests or documented checks.
- [x] Update `UX-P2-010` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-001 — Add “what should I do next?” operating coach
- [ ] Define implementation design and file-level change plan for UX-P3-001.
- [ ] Implement/create the required files/components listed in UX-P3-001.
- [ ] Validate acceptance criteria for UX-P3-001 with tests or documented checks.
- [ ] Update `UX-P3-001` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-002 — Add strategic roadmap and initiative planning UX
- [ ] Define implementation design and file-level change plan for UX-P3-002.
- [ ] Implement/create the required files/components listed in UX-P3-002.
- [ ] Validate acceptance criteria for UX-P3-002 with tests or documented checks.
- [ ] Update `UX-P3-002` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-003 — Add workflow comparison and optimization UX
- [ ] Define implementation design and file-level change plan for UX-P3-003.
- [ ] Implement/create the required files/components listed in UX-P3-003.
- [ ] Validate acceptance criteria for UX-P3-003 with tests or documented checks.
- [ ] Update `UX-P3-003` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-004 — Add skill gap and skill improvement UX loop
- [ ] Define implementation design and file-level change plan for UX-P3-004.
- [ ] Implement/create the required files/components listed in UX-P3-004.
- [ ] Validate acceptance criteria for UX-P3-004 with tests or documented checks.
- [ ] Update `UX-P3-004` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-005 — Add learning loop and lessons-learned UX
- [ ] Define implementation design and file-level change plan for UX-P3-005.
- [ ] Implement/create the required files/components listed in UX-P3-005.
- [ ] Validate acceptance criteria for UX-P3-005 with tests or documented checks.
- [ ] Update `UX-P3-005` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-006 — Add scenario simulation and decision workspace
- [ ] Define implementation design and file-level change plan for UX-P3-006.
- [ ] Implement/create the required files/components listed in UX-P3-006.
- [ ] Validate acceptance criteria for UX-P3-006 with tests or documented checks.
- [ ] Update `UX-P3-006` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-007 — Add personal productivity command layer
- [ ] Define implementation design and file-level change plan for UX-P3-007.
- [ ] Implement/create the required files/components listed in UX-P3-007.
- [ ] Validate acceptance criteria for UX-P3-007 with tests or documented checks.
- [ ] Update `UX-P3-007` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-008 — Add meeting capture and action extraction UX
- [ ] Define implementation design and file-level change plan for UX-P3-008.
- [ ] Implement/create the required files/components listed in UX-P3-008.
- [ ] Validate acceptance criteria for UX-P3-008 with tests or documented checks.
- [ ] Update `UX-P3-008` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-009 — Add voice and multimodal interaction roadmap
- [ ] Define implementation design and file-level change plan for UX-P3-009.
- [ ] Implement/create the required files/components listed in UX-P3-009.
- [ ] Validate acceptance criteria for UX-P3-009 with tests or documented checks.
- [ ] Update `UX-P3-009` status from `Open` to `Completed` when acceptance criteria are met.

### UX-P3-010 — Add UX telemetry and product analytics
- [ ] Define implementation design and file-level change plan for UX-P3-010.
- [ ] Implement/create the required files/components listed in UX-P3-010.
- [ ] Validate acceptance criteria for UX-P3-010 with tests or documented checks.
- [ ] Update `UX-P3-010` status from `Open` to `Completed` when acceptance criteria are met.

