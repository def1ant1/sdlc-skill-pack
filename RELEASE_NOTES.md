# Release Notes

## v8.0.22 — 2026-05-11

This release finalizes MB-P0-020 with a single release readiness gate and deterministic packaging outputs.

### Added
- Single release readiness gate (`scripts/validate_release_readiness.py`) aggregating release reports, artifacts/version checks, governance gates, and smoke tests.
- Package manifest output for ZIP artifacts (`dist/*.manifest.json`) alongside SHA-256 checksums.

### Changed
- `scripts/package_release.py` now enforces inclusion of `VERSION` and `RELEASE_NOTES.md` in release packages.
- Release process documentation now calls out one canonical command flow for readiness and packaging.
