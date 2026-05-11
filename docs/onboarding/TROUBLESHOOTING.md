# Troubleshooting

## Common Error Categories and Remediation

### 1) Environment prerequisite failures
**Symptoms**
- `apotheon doctor` reports missing Python/package/api key checks.

**Remediation**
1. Install Python 3.11+.
2. Recreate venv and dependencies: `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
3. Set `ANTHROPIC_API_KEY` for live runs.
4. Re-run: `apotheon doctor`.

### 2) Local infrastructure unavailable (Qdrant/Temporal)
**Symptoms**
- `Qdrant reachable` or `Temporal reachable` warnings from doctor.
- Schedule/run commands error on connection refused.

**Remediation**
1. Start stack: `docker compose up -d qdrant temporal temporal-ui`.
2. Verify: `docker compose ps`.
3. Re-run: `apotheon doctor` and `apotheon diagnostics`.

### 3) Connector readiness failures
**Symptoms**
- `apotheon connectors check` reports missing credentials or connector-specific health errors.

**Remediation**
1. Validate connector env vars in `.env`.
2. Run targeted check: `apotheon connectors check --connector <name>`.
3. Confirm policy and scope restrictions before retrying workflow execution.

### 4) Local app health failures
**Symptoms**
- `apotheon local-apps check` fails for one or more compose services.

**Remediation**
1. Confirm compose file path: `--compose-file docker-compose.yml`.
2. Restart failing services: `docker compose restart <service>`.
3. Re-check: `apotheon local-apps check`.

### 5) Workflow interruption/recovery failures
**Symptoms**
- Run exits mid-flight or remains pending without progress.

**Remediation**
1. Inspect run: `apotheon logs <run_id>`.
2. Resume: `apotheon workflows resume <run_id>`.
3. If state is inconsistent, collect evidence: `apotheon diagnostics`.

### 6) Schedule lock/state corruption
**Symptoms**
- Due schedules are skipped repeatedly due to stale lock state.

**Remediation**
1. Repair state and dry-run due schedules: `apotheon schedules repair`.
2. Validate next run window: `apotheon schedules preview <schedule.yaml>`.

### 7) Backup/restore safety validation
**Symptoms**
- Need to verify recovery without mutating local state.

**Remediation**
1. Create backup: `apotheon backup create --output dist`.
2. Preview restore plan only: `apotheon backup restore --dry-run <backup_path>`.
3. Execute live restore only after dry-run review.


### Docker stack remediation

For container-first startup and failure recovery, follow `docs/onboarding/DOCKER_TROUBLESHOOTING.md`.

### 8) Structured error envelope failures
**Symptoms**
- Errors return JSON with `error_id`, `correlation_id`, and `remediation` fields.
- Validation script fails: `scripts/validation/validate_error_contracts.py`.

**Remediation**
1. Validate envelope contract: `python scripts/validation/validate_error_contracts.py`.
2. Confirm boundary emitter (`runtime`, `planner`, `scheduler`, or `connector:*`) is set in `skill`.
3. Ensure `retryable=false` for auth/config/validation and high-risk side effects.
4. Ensure remediation text is actionable for operators before rerun/escalation.


## Connector health reporting

- Run `python scripts/reports/generate_connector_health_report.py` to generate `reports/connector_health_report.md` and `reports/connector_health_report.json`.
- Connector writes remain blocked by default (`APOTHEON_CONNECTORS_READ_ONLY=true`) and require HITL approval + idempotency keys for live writes.


## Additional references
- Operator runbook: `docs/onboarding/OPERATOR_RUNBOOK.md`
- Docker troubleshooting: `docs/onboarding/DOCKER_TROUBLESHOOTING.md`
- Diagnostics commands: `docs/examples/RUNNABLE_CLI_EXAMPLES.md`
