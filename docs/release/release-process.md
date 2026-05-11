# Release Process and Gate Topology

## Gate topology

The pre-merge gate runner is `scripts/run_premerge_checks.py` and is phase-aware.

- `contracts` phase gates (quality and governance contracts):
  - doc uniqueness (`scripts/docs/validate_doc_uniqueness.py`)
  - backlog/changelog sync (`scripts/docs/check_backlog_changelog_sync.py`)
  - doc freshness (`scripts/docs/enforce_doc_freshness.py`)
  - README claims (`scripts/docs/validate_readme_claims.py`)
  - backlog truth (`scripts/validate_backlog_truth.py`)
  - skill contracts (`scripts/validate_skill_contracts.py`)
  - context budget (`scripts/check_context_budget.py`)
  - inventory/dependency/overlap generation and checks
  - eval, telemetry, work task freshness, HITL coverage, and maturity gates
- `release` phase gates (release artifact and release-health checks):
  - release report generation (`scripts/generate_release_reports.py`)
  - HITL coverage (`scripts/validate_hitl_coverage.py`)
  - skill maturity (`scripts/grade_skill_maturity.py`)

## CI execution model

CI uses the **canonical single entrypoint** model for phase-gated checks:

- `python scripts/run_premerge_checks.py --phase contracts`
- `python scripts/run_premerge_checks.py --phase release`
- `python scripts/validate_section15_release_gates.py`

This avoids drift between CI command lists and local pre-merge command lists.

## Section 15 machine-verifiable release gates

Section 15 of `APOTHEON_HARDENING_AND_ERROR_HANDLING_BACKLOG.md` is enforced by:

- `scripts/validate_section15_release_gates.py`

The gate runner validates:

- module/file presence checks
- schema adoption checks
- workflow resume support checks
- planner diagnostics checks
- schedule safety checks
- connector fail-closed checks
- governance gate checks
- diagnostics output checks
- backup/restore dry-run checks
- hardening test checks

Each gate emits PASS/FAIL output and, for missing artifacts, prints direct file pointers so remediation is immediate.

### Local usage

Run before opening a release PR or cutting a local tag:

```bash
python scripts/validate_section15_release_gates.py
```

Optional strict mode (ensures non-command gates are treated as mandatory presences only):

```bash
python scripts/validate_section15_release_gates.py --strict
```

### CI usage and release promotion blocking

`/.github/workflows/validate.yml` runs Section 15 gates in:

- the main `validate` job (push/PR safety)
- the `release-reports` job (release `published` and `prereleased` events)

Any failure exits non-zero, so release tagging/promotion is blocked until all Section 15 gates pass.

## Failure output behavior

`run_premerge_checks.py` groups failures by phase and gate name, and deduplicates repeated error lines in captured command output to reduce repeated noise in CI logs.


## Release artifact consistency checks

Before merge and at release time, CI must validate:

- `README.md` declared version equals `VERSION`.
- `CHANGELOG.md` contains the current release entry from `VERSION`.
- `RELEASE_NOTES.md` contains a matching release-notes section for that version.
- Generated files in `reports/` embed current commit SHA traceability metadata.

Use:

- `python scripts/validate_release_artifacts.py`

The validator emits mismatch messages with exact file and line references to accelerate correction.


## Canonical MB-P0-020 release flow

```bash
python scripts/validate_release_readiness.py
python scripts/package_release.py --version "$(cat VERSION)"
python scripts/validate_release_package.py --zip-path "dist/apotheon-skill-pack-v$(cat VERSION).zip"
```

This flow yields a deterministic release ZIP plus `.sha256` and `.manifest.json` artifacts tied to the exact package contents.
