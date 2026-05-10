---
last_updated: 2026-05-10
owner: documentation-governance
---

# Documentation Governance

## Canonical Ownership

- **Backlog** owns **work status** (planned/in-progress/done execution state).
- **Changelog** owns **released deltas** (what has shipped and when).
- **Docs** (the `docs/` tree) own **enduring guidance** (architecture, standards, and operational reference).

## Rules

1. Keep status tracking in backlog documents only; do not duplicate status tables in `README` or `docs/`.
2. Keep release notes in `CHANGELOG.md` only; backlog/docs may link to changelog entries.
3. Keep long-form guidance in `docs/`; backlog/changelog may include short summaries plus links.
4. Avoid large duplicated sections across top-level backlog, docs, and readme documents.
5. Completed backlog work must map to released/not-released markers in `CHANGELOG.md`.

## Enforcement

- `scripts/docs/validate_doc_uniqueness.py` detects duplicated large sections across top-level backlog/docs/readme files.
- `scripts/docs/check_backlog_changelog_sync.py` verifies completed backlog status is reflected in changelog release tracking.
- `scripts/docs/enforce_doc_freshness.py` requires `last_updated` metadata on key top-level documents.
