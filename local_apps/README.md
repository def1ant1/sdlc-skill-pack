# Local Apps Health Toolkit

This folder contains a local Docker Compose stack, Kubernetes-style reference manifests,
and health tooling for verifying that local apps are not only **running**, but also **usable**.

## What this checks

- Container/service process health (`running`, `healthy`, `starting`, etc.)
- API usability checks (HTTP endpoint responds with expected status)
- App dependency startup order (e.g., DB/queue before app/worker)
- Port conflicts across services
- Required volume mappings and host-path existence
- Backup readiness (declared backup strategy and mount paths)
- Upgrade/migration risk warnings
- `.env` variable requirements with explicit remediation guidance

## Files

- `docker-compose.local-apps.yml` - local stack definition with health checks and dependency order
- `manifests/*.yaml` - Kubernetes reference manifests for app, db, worker, queue, and API gateway
- `../scripts/local_apps/check_app_health.py` - evaluates runtime/container/API/config health
- `../scripts/local_apps/generate_local_app_report.py` - writes JSON/Markdown report from health check results

## Usage

```bash
python scripts/local_apps/check_app_health.py \
  --compose-file local_apps/docker-compose.local-apps.yml \
  --env-file .env \
  --output-json local_apps/health-report.json

python scripts/local_apps/generate_local_app_report.py \
  --input local_apps/health-report.json \
  --output-md local_apps/health-report.md
```

## Interpretation: running vs usable

A service can be container-`running` but API-`unusable` if:

- health endpoint is failing
- DB migrations are pending
- dependent services are unavailable
- required env/config is missing

Always use `api_usable` (not just `container_running`) before considering a service production-like for local validation.
