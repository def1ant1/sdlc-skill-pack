# Docker Deployment Runbook

## Prerequisites
- Docker Engine + Compose plugin
- Python 3.11+

## 1) Prepare env
```bash
cp .env.example .env
```
Expected output: no output, `.env` file exists.

## 2) Start full stack
```bash
scripts/docker/init-local-stack.sh
```
Expected output includes:
- `local stack initialized`
- per-service health status lines.

## 3) Validate compose health
```bash
python scripts/docker/check-compose-health.py
```
Expected output (JSON):
- `apotheon-postgres`, `apotheon-redis`, `apotheon-qdrant`, `apotheon-temporal`, `apotheon-runtime`
- all service status values equal `healthy`.

## 4) Smoke test from runtime container
```bash
scripts/docker/smoke-test-container.sh
```
Expected output includes:
- validations from `validate_skill_structure.py` and `validate_frontmatter.py`
- `smoke tests completed`.

## 5) Manual endpoint checks
```bash
curl -fsS http://localhost:8000/health
curl -fsS http://localhost:6333/collections
```
Expected output: JSON response from API and Qdrant.

## Services and Ports
- Runtime API: `:8000`
- Postgres: `:5432`
- Redis: `:6379`
- Qdrant: `:6333`
- Temporal gRPC: `:7233`
- Temporal UI: `:8080`


## Related runbooks
- `docs/onboarding/DOCKER_TROUBLESHOOTING.md`
- `docs/onboarding/OPERATOR_RUNBOOK.md`
- `docs/examples/RUNNABLE_CLI_EXAMPLES.md`
