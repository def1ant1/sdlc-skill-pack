# Operator Runbook

## Recovery Flow Commands

### Baseline health and diagnostics
```bash
apotheon doctor
apotheon diagnostics
apotheon connectors check
apotheon local-apps check --compose-file docker-compose.yml
```

### Workflow recovery
```bash
apotheon workflows list --limit 20
apotheon logs <run_id>
apotheon workflows resume <run_id>
```

### Schedule recovery
```bash
apotheon schedules preview schedules/examples/oldfarmtrucks-weekly-operating-review.yaml
apotheon schedules repair
apotheon schedules run-due --dry-run
```

### Backup and restore rehearsal
```bash
apotheon backup create --output dist
apotheon backup restore --dry-run dist/<backup-archive>.tar.gz
```

## Incident-oriented quick playbooks

### Playbook A: Workflow stuck after dependency outage
1. `apotheon doctor`
2. `apotheon connectors check`
3. `apotheon diagnostics`
4. `apotheon workflows resume <run_id>`

### Playbook B: Repeated due-schedule misses
1. `apotheon schedules repair`
2. `apotheon schedules run-due --dry-run`
3. Inspect logs and resume affected workflows.

### Playbook C: Pre-restore verification
1. `apotheon backup create --output dist`
2. `apotheon backup restore --dry-run <archive>`
3. Review planned file operations before any live restore.


## Runtime Hardening Notes
- Use `--dry-run` to validate plans without any external model or connector side effects.
- For live runs, set `APOTHEON_PROVIDER` to `anthropic` or `local`; other providers are rejected by policy.
- If a run fails with structured output errors, inspect step payloads with:
  - `python scripts/workflows/list_runs.py --limit 20`
  - `python scripts/workflows/show_run.py <run_id>`
  - `python scripts/workflows/show_run.py <run_id> --summary`
- Canonical local run outputs:
  - `runtime/workflow_runs/<run_id>/run_record.json`
  - `runtime/artifacts/<run_id>.artifacts.json`
  - `runtime/reports/<run_id>.report.md`


### Scheduling update (MB-P0-010)
Scheduling tooling is implemented under `scripts/schedules/` with schema + runtime run recording in `runtime/schedule_runs/`. Use `python scripts/schedules/run_due_schedules.py --dry-run` for safe due-window checks.

## Chat UI MVP operations

### Launch
```bash
streamlit run apps/chat-ui/streamlit_app.py
```

### Safety defaults
- UI defaults to read-only/dry-run planning mode.
- Live writes remain blocked until operator checks approval intent and enters an approval ticket/reference.
- Even in approval-ready state, planner invocation in MVP is still `--dry-run`.

### UI data sources
- Health: `reports/runtime_diagnostics.json`
- Cost: `reports/cost_dashboard.json`
- Rate limits: `reports/rate_limit_report.json`
- Schedules: `schedules/registry.yaml`
- OldFarmTrucks templates: `workflows/examples/oldfarmtrucks-*.json`

## Control-plane dashboard MVP

Generate fresh dashboard state data before launching the UI:

```bash
python scripts/reports/generate_dashboard_data.py
```

Launch the dashboard:

```bash
streamlit run apps/dashboard/streamlit_dashboard.py
```

The dashboard surfaces workflow progress, schedules, approvals, budgets, rate limits, connector/local-app health, memory, telemetry, skill maturity, and OldFarmTrucks template status from `reports/dashboard_state.json`.

### HITL approve/reject actions

Use the **Approve** / **Reject** buttons in the `HITL Approval Queue` section. Decisions are written back to `reports/dashboard_state.json` with `decided_at` timestamps for auditability.


## Connector health reporting

- Run `python scripts/reports/generate_connector_health_report.py` to generate `reports/connector_health_report.md` and `reports/connector_health_report.json`.
- Connector writes remain blocked by default (`APOTHEON_CONNECTORS_READ_ONLY=true`) and require HITL approval + idempotency keys for live writes.
