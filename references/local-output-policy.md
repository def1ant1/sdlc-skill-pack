# Local Output Policy

This policy defines deterministic file layout and retention for local workflow execution records.

## Runtime file layout

- Run records: `runtime/workflow_runs/<run_id>/run_record.json`
- Deterministic artifact index: `runtime/artifacts/<run_id>.artifacts.json`
- Deterministic operator report: `runtime/reports/<run_id>.report.md`
- Legacy compatibility record: `runtime/workflow_history/<run_id>.json`

## Determinism requirements

- Every local run MUST persist all three run outputs (record, artifacts index, report).
- Output filenames MUST be derived from `run_id` only.
- Artifact listing in `*.artifacts.json` MUST be sorted and deduplicated.

## Retention policy

- Keep the most recent 90 days of local run records by default.
- Keep at least the latest 500 records regardless of age.
- Operators MAY archive or delete older records for disk management.
- `runtime/` generated outputs are local operational state and should not be committed except `.gitkeep` sentinels.

## Inspection commands

- `python scripts/workflows/list_runs.py`
- `python scripts/workflows/show_run.py <run_id>`
- `python scripts/workflows/show_run.py <run_id> --summary`
