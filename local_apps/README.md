# Local Apps Health Toolkit

This folder contains local app compose/env/docs/manifests/mappings plus scripts to verify readiness.

## Included assets

- `docker-compose.local-apps.yml` with profile-based startup (`core`, `mvp`, `automation`, `analytics`)
- `.env.local-apps.example` for local runtime configuration
- `manifests/*.yaml` Kubernetes-style reference manifests
- `mappings/local_app_categories.yaml` canonical app category mapping + coverage
- `docs/local-app-readiness.md` profile and readiness guidance

## Scripts

- `scripts/local_apps/list_apps.py`
- `scripts/local_apps/check_app_health.py`
- `scripts/local_apps/check_connector_health.py`
- `scripts/local_apps/generate_local_app_report.py`

## Generate reports

```bash
python scripts/local_apps/check_app_health.py \
  --compose-file local_apps/docker-compose.local-apps.yml \
  --env-file local_apps/.env.local-apps.example \
  --output-json reports/local_apps/health-report.json

python scripts/local_apps/generate_local_app_report.py \
  --input reports/local_apps/health-report.json \
  --output-md reports/local_apps/health-report.md

python scripts/local_apps/check_connector_health.py
```
