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

This avoids drift between CI command lists and local pre-merge command lists.

## Failure output behavior

`run_premerge_checks.py` groups failures by phase and gate name, and deduplicates repeated error lines in captured command output to reduce repeated noise in CI logs.
