---
last_updated: 2026-05-10
owner: documentation-governance
---

# Documentation Governance Standard

## Canonical Ownership

- `APOTHEON_V9_ENTERPRISE_SKILL_OS_BACKLOG.md` is the canonical owner for execution planning and phase status only.
- `CHANGELOG.md` is the canonical owner for released changes only.
- `docs/` is the canonical owner for durable architecture, usage, and standards.

## Merge Rules

1. Do not copy-paste full sections between backlog, roadmap, changelog, and `docs/`.
2. Use links/references to canonical sources rather than duplicating prose.
3. Every concept must have exactly one canonical owner document.
4. If a section is intentionally mirrored, use a concise summary and a link to canonical content.
5. Completed backlog phases must map to `CHANGELOG.md` entries or include an explicit `not released` marker.

## Enforcement

- `scripts/docs/validate_doc_uniqueness.py` blocks duplicate section titles and duplicate content fingerprints.
- `scripts/docs/check_backlog_changelog_sync.py` blocks completed phases without release mapping.
- `scripts/docs/enforce_doc_freshness.py` blocks missing/stale `last_updated` metadata on key docs.
