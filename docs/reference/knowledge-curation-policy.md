# Knowledge Curation Policy

## Purpose

Define safe, auditable memory curation where conversation extraction **proposes** notes and never auto-persists all claims.

## Policy rules

1. Extraction must default to `propose_only` mode.
2. Persisted memory requires explicit lifecycle action: `approve`, `edit`, `reject`, `archive`, or `supersede`.
3. Every note must carry provenance (`conversation_id`, excerpt refs) and impact links to artifacts/entities.
4. Retrieval should prioritize active notes (`approved`, `edited`) and avoid archived/rejected content.
5. Conflict/staleness checks must run before retrieval in high-impact flows.

## Command semantics

- **“remember this”**: marks the intent to curate and approve selected proposed notes.
- **“don’t use that anymore”**: deprecates prior notes via `archive` or `supersede` action.
- **Targeted retrieval**: filter by query + category + entity.

## Implementation references

- `scripts/orchestration/conversation_to_knowledge_notes.py`
- `core/knowledge-curation-assistant/references/knowledge-note-taxonomy.md`
- `core/knowledge-curation-assistant/templates/knowledge-note.md`
