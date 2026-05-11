# Docker Troubleshooting

## Docker doctor
```bash
scripts/docker/doctor.sh
```
If this fails, install missing local dependencies (`docker`, `python3`, or `curl`).

## Service unhealthy
```bash
docker compose ps
python scripts/docker/check-compose-health.py
```
Remediation:
1. `docker compose logs <service> --tail=200`
2. `docker compose restart <service>`
3. re-run health check script.

## Runtime cannot connect to dependencies
Run:
```bash
scripts/docker/wait-for-services.sh
```
If failing on Temporal, ensure Postgres is healthy first.

## Clean rebuild
```bash
docker compose down -v
docker compose build --no-cache runtime
docker compose up -d
```
Then re-run:
```bash
scripts/docker/smoke-test-container.sh
```

## Common failure signatures
- `connection refused` on `:5432` → Postgres not healthy.
- `cluster health` failure in Temporal → wait for DB migrations, then restart Temporal.
- `curl ... /health` fails for runtime → check runtime logs for import/env errors.
