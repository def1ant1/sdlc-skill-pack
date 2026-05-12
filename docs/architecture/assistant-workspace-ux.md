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
