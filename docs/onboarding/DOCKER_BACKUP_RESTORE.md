# Docker Backup / Restore

## Backup
```bash
scripts/docker/backup-stack.sh
```

Artifacts:
- `docker-stack-backup-<timestamp>.tar.gz`
- `docker-stack-backup-<timestamp>.tar.gz.sha256`

## Restore preview (required)
```bash
scripts/docker/restore-stack.sh dist/backups/docker/<archive>.tar.gz --dry-run
```

## Live restore
```bash
scripts/docker/restore-stack.sh dist/backups/docker/<archive>.tar.gz --live
```

## Validation
1. `docker compose ps`
2. `scripts/docker/check-compose-health.py`
3. `scripts/docker/smoke-test-container.sh`

## Recovery guidance
- Always run dry-run preview first.
- Confirm approval before any secret-inclusive restore.
- If health checks fail, rollback to previous known-good backup and re-run validation.
