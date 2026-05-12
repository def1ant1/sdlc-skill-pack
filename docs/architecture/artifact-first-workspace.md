# Artifact-First Workspace Interaction Model

The artifact-first workspace treats every durable output as a typed artifact with shared base fields:

- `id`: globally unique artifact identifier.
- `type`: artifact category (`plan`, `workflow`, `task`, `schedule`, `skill_proposal`, `decision`, `knowledge_note`, `approval`, `report`, `execution_run`).
- `title`: human-readable descriptor.
- `status`: lifecycle status.
- `owner`: principal responsible for updates.
- `source_refs`: links to originating conversation and messages.
- `version`: semantic version string (`major.minor.patch`).
- `relationships`: typed links to related artifacts.

## Interaction flow

1. **Create**: user action or agent action emits an artifact with `version = 1.0.0` and `artifact.created` audit event.
2. **Browse**: artifact panel lists artifacts by `type` and `title`; selecting one renders metadata and editable content.
3. **Edit**: content edits produce a patch version bump and `artifact.updated` audit event.
4. **Link**: relationships are added as `rel -> target` entries and `artifact.linked` audit events.
5. **Revert**: reversible edits restore a prior snapshot and emit `artifact.reverted` audit events.

## Audit model

Audit events are append-only and include event name, actor, timestamp, version, and details. This allows full provenance tracking for manual and automated changes.
