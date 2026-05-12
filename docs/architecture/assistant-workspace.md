# Assistant Workspace Architecture

The assistant workspace is a persistent domain model that links the operator's conversation sessions to generated artifacts, approval decisions, and workflow execution runs.

## Domain model

`core/workspace/models.py` defines the canonical model:
- `Workspace`: root aggregate with relationship ID sets.
- `ConversationRef`: conversation session pointer.
- `ArtifactRef`: produced plan/report pointer.
- `ApprovalRef`: HITL approval pointer.
- `ExecutionRunRef`: workflow runtime pointer.
- `WorkspaceState`: full persisted state wrapper.

## Persistence lifecycle

`apps/chat-ui/workspace_state.py` implements lifecycle operations:
1. **Initialize** with `default_workspace_state()` when state file is absent.
2. **Load** via `load_workspace_state()` during chat app startup.
3. **Resume context** via `resume_session_from_workspace()` to recover the active conversation.
4. **Mutate safely** through helper methods like `register_conversation()`.
5. **Persist** with `save_workspace_state()` after every mutation.

State is stored in `reports/workspace/workspace-state.json`.

## Schema contracts

Workspace contracts are defined in:
- `schemas/workspace.schema.json`
- `schemas/workspace-state.schema.json`
- `schemas/conversation-session.schema.json`

The schemas include IDs (`$id`) and relationship fields (`*_ids`, `workspace_id`, `run_id`, `plan_id`) so downstream systems can correlate UI/session state with runtime records.

## Validation hooks

Validation executes whenever workspace state is:
- created (`default_workspace_state`)
- loaded (`load_workspace_state`)
- saved (`save_workspace_state`)
- mutated (`register_conversation`)

If required fields are missing, mutations fail fast with a `ValueError`.

## UI inspection/export

`apps/chat-ui/workspace_views.py` exposes:
- **Inspect Workspace**: pushes workspace JSON into the artifact panel.
- **Export Workspace**: downloads the current workspace-state document.

This enables operators to audit, share, and restore workspace context.
