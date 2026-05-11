# Changelog

All notable changes to the Apotheon AI Company OS are documented here.

## [8.0.22] — 2026-05-11 — Release Readiness Gate + Packaging Manifest (MB-P0-020)

- Unified release gate in `scripts/validate_release_readiness.py` to aggregate release report generation, artifact consistency validation, Section 15 governance gates, and offline smoke tests.
- Hardened deterministic packaging in `scripts/package_release.py` with required `VERSION`/`RELEASE_NOTES.md` inclusion and generated checksum + manifest (`.sha256`, `.manifest.json`) for each ZIP build.
- Finalized release artifacts (`VERSION`, `CHANGELOG.md`, `RELEASE_NOTES.md`) and updated release-process docs with the single release readiness flow.

## [8.0.21] — 2026-05-11 — OldFarmTrucks Company Template Import (MB-P0-019)

- Added importable template payload at `company_templates/oldfarmtrucks/template.json` with workflows, schedules, dashboards, connectors, approvals, budgets, and sample data.
