# Local App Readiness + Startup Profiles

## Profiles

Use Docker Compose profiles to start only the category you need:

- `core`: base runtime (`local-db`, `local-queue`, `local-app`)
- `mvp`: full local MVP (`core` + `local-worker` + `local-api`)
- `automation`: queue/worker-only flows
- `analytics`: database-only scenarios

### Examples

```bash
docker compose -f local_apps/docker-compose.local-apps.yml --profile core up -d
docker compose -f local_apps/docker-compose.local-apps.yml --profile mvp up -d
```

## Health/Readiness Checks

- App health: `python scripts/local_apps/check_app_health.py ...`
- Connector health: `python scripts/local_apps/check_connector_health.py`
- Local app inventory: `python scripts/local_apps/list_apps.py`
- Markdown report: `python scripts/local_apps/generate_local_app_report.py ...`

Readiness should be based on `api_usable` + dependency health, not merely container state.
