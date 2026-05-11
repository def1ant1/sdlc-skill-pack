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
- If a run fails with structured output errors, inspect step payloads in `runtime/workflow_history/<run_id>.json` and verify model responses are JSON objects with `status` and `summary`.
