# Release Notes

## v8.0.5 — 2026-05-10

This release strengthens release governance and CI validation.

### Added
- Canonical `VERSION` file (`8.0.5`) as release source of truth.
- CI gate enforcing `README.md` declared version matches `VERSION`.
- CI gate ensuring `CHANGELOG.md` includes a `8.0.5` entry.
- CI gate ensuring `RELEASE_NOTES.md` includes a `v8.0.5` section.
- CI gate verifying generated reports embed the current commit SHA traceability metadata.

### Changed
- Updated release process documentation with explicit artifact validation and mismatch troubleshooting.
- Added exact file/line mismatch hints in release artifact validation failures.
