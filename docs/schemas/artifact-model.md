# Conversation Artifact Model

This model standardizes assistant-created artifacts so they are addressable in chat and traceable through versions.

## Artifact schemas

Location: `schemas/artifacts/`

- `common-envelope.schema.json` defines shared envelope fields:
  - `id`, `type`, `title`, `status`
  - `source.conversation_id`, `source.message_ids`
  - `owner`, `version`, `content`, `links`
- Type schemas:
  - `plan.schema.json`
  - `workflow.schema.json`
  - `skill-proposal.schema.json`
  - `task.schema.json`
  - `schedule.schema.json`
  - `knowledge-note.schema.json`
  - `decision.schema.json`
  - `approval-request.schema.json`
  - `assistant-action.schema.json`

## Conversion rules

Defined in `schemas/artifacts/conversion-rules.yaml`.

Supported transformations:
- plan -> task
- plan -> workflow
- conversation -> knowledge_note
- workflow_run -> decision
- workflow_run -> knowledge_note (lessons learned)

## Validation and fixtures

- Fixtures for each artifact type are stored in `fixtures/artifacts/*.json`.
- Validation script: `scripts/validation/validate_artifact_schemas.py`.
- This check verifies fixtures match envelope and type constraints and supports version-tracked assistant artifacts.
