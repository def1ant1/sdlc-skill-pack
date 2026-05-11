# APOTHEON — DOCKER DEPLOYMENT BACKLOG

**Status:** DEPLOYMENT SIMPLIFICATION PLAN  
**Purpose:** Make Apotheon easy to run locally, demo, test, schedule, and eventually deploy for single-user or small-business use through Docker Compose, while preserving direct host execution for development.

---

## 1. Deployment Philosophy

Use Docker to standardize the runtime environment, but do not make Docker the only supported execution mode.

Supported modes:

```text
1. Host mode
   Best for active Claude Code development, debugging, and editing.

2. Docker Compose laptop mode
   Best for repeatable local operation, demos, smoke tests, and scheduled workers.

3. Docker Compose server mode
   Best for always-on schedules, Temporal workers, local business apps, dashboards, and shared/team use.

4. Devcontainer mode
   Best for reproducible developer onboarding.
```

Recommended stance:

```text
Host Claude Code for interactive development.
Dockerize the Apotheon runtime for repeatable execution.
Use Docker Compose for Qdrant, Temporal, Postgres, Redis, local apps, workers, schedulers, reports, and dashboards.
```

---

## 2. Target Docker Architecture

```text
host machine
├── repo checkout
├── .env
├── docker-compose.yml
├── docker-compose.override.yml
├── docker-compose.local-apps.yml
└── services
    ├── apotheon-cli
    ├── apotheon-worker
    ├── apotheon-scheduler
    ├── apotheon-reports
    ├── apotheon-api optional
    ├── apotheon-chat-ui optional
    ├── qdrant
    ├── temporal
    ├── temporal-ui
    ├── postgres
    ├── redis
    ├── minio optional
    ├── grafana optional
    ├── prometheus optional
    ├── loki optional
    └── local business app profiles optional
```

---

## 3. Required Files

Create:

```text
Dockerfile
Dockerfile.dev
.dockerignore
docker-compose.yml
docker-compose.override.yml
docker-compose.server.yml
docker-compose.local-apps.yml
.env.example
docs/onboarding/DOCKER_DEPLOYMENT.md
docs/onboarding/DOCKER_TROUBLESHOOTING.md
scripts/docker/doctor.sh
scripts/docker/wait-for-services.sh
scripts/docker/init-local-stack.sh
scripts/docker/smoke-test-container.sh
```

---

## 4. Core Services

### apotheon-cli

Purpose: run one-off commands, validation, workflow planning, smoke tests, and report generation.

Example command:

```bash
docker compose run --rm apotheon-cli python scripts/run_premerge_checks.py
```

### apotheon-worker

Purpose: run workflow execution workers.

Command:

```bash
python scripts/runtime/temporal_worker.py
```

### apotheon-scheduler

Purpose: run due schedules, initially in dry-run mode.

Command:

```bash
python scripts/schedules/run_due_schedules.py --loop --dry-run
```

### apotheon-reports

Purpose: generate periodic local ops, readiness, health, and runtime reports.

Command:

```bash
python scripts/reports/generate_local_ops_report.py
```

### apotheon-api optional

Purpose: expose local HTTP endpoints for chat UI, dashboards, workflow runs, schedules, approvals, and reports.

Candidate implementation:

```text
FastAPI
```

### apotheon-chat-ui optional

Purpose: browser UI for single-user interaction with workflows, schedules, reports, approvals, and memory.

Candidate implementation:

```text
Streamlit first for MVP
FastAPI + React later for production
Open WebUI integration optional for chat-style LLM access
```

---

## 5. Infrastructure Services

Required:

```text
qdrant
temporal
temporal-ui
postgres
redis
```

Optional:

```text
minio
grafana
prometheus
loki
otel-collector
uptime-kuma
```

---

## 6. Docker Compose Profiles

Define profiles:

```text
core
runtime
scheduler
reports
api
ui
observability
local-apps
security
all
```

Example usage:

```bash
# Core local runtime
docker compose --profile core up -d

# Runtime plus worker and scheduler
docker compose --profile runtime --profile scheduler up -d

# Add API and UI
docker compose --profile api --profile ui up -d

# Add observability
docker compose --profile observability up -d
```

---

## 7. Environment Configuration

Create `.env.example` with:

```bash
EXECUTION_MODE=local
LOG_LEVEL=INFO
LOG_FORMAT=json
APOTHEON_WORKSPACE=/workspace
QDRANT_URL=http://qdrant:6333
TEMPORAL_HOST=temporal:7233
TEMPORAL_NAMESPACE=apotheon-dev
TEMPORAL_TASK_QUEUE=apotheon-sdlc
POSTGRES_HOST=postgres
POSTGRES_DB=apotheon
POSTGRES_USER=apotheon
POSTGRES_PASSWORD=change-me
REDIS_URL=redis://redis:6379/0
EMBEDDING_BACKEND=ollama
OLLAMA_URL=http://host.docker.internal:11434
CLAUDE_MODEL=claude-sonnet-4-6
ANTHROPIC_API_KEY=
OPENAI_API_KEY=
APOTHEON_DRY_RUN_DEFAULT=true
APOTHEON_REQUIRE_HITL_FOR_WRITES=true
APOTHEON_ENABLE_EXTERNAL_WRITES=false
```

Rules:

- `.env` must never be committed.
- `.env.example` must contain no secrets.
- Write actions are disabled by default.
- Dry-run is default for scheduler until explicitly changed.

---

## 8. Volumes and Data Persistence

Required volumes:

```text
qdrant_data
temporal_data
postgres_data
redis_data
apotheon_runtime
apotheon_reports
apotheon_artifacts
apotheon_backups
```

Mount the repo into app containers:

```yaml
volumes:
  - .:/workspace
```

Server deployments may instead bake code into the image and mount only runtime/config/artifact volumes.

---

## 9. Health Checks

Each service needs health checks.

Examples:

```text
qdrant: /collections
temporal: tctl or temporal operator health check
postgres: pg_isready
redis: redis-cli ping
apotheon-api: /health
apotheon-worker: heartbeat file or worker status endpoint
apotheon-scheduler: heartbeat file
```

Create:

```text
scripts/docker/check-compose-health.py
reports/docker_health_report.md
reports/docker_health_report.json
```

---

## 10. Container Smoke Tests

Create:

```text
tests/deployment/test_docker_build.py
tests/deployment/test_docker_compose_config.py
tests/deployment/test_container_smoke.py
```

Required smoke commands:

```bash
docker compose build apotheon-cli
docker compose config
docker compose run --rm apotheon-cli python --version
docker compose run --rm apotheon-cli python scripts/validation/validate_skill_structure.py .
docker compose run --rm apotheon-cli python scripts/generate_skill_inventory.py
docker compose run --rm apotheon-cli python scripts/smoke_test_release.py --dry-run
```

---

## 11. Chat UI Backlog

A single user needs a lightweight browser interface.

Create MVP:

```text
apps/chat-ui/
apps/chat-ui/README.md
apps/chat-ui/streamlit_app.py
scripts/api/apotheon_api.py
```

MVP chat UI capabilities:

```text
submit objective
select domain planner
run dry-run planning
show workflow plan
run workflow dry-run
show artifacts/reports
show pending approvals
show recent runs
show schedule list
show local app health
```

Suggested first implementation:

```text
Streamlit frontend + subprocess calls to existing scripts
```

Later implementation:

```text
FastAPI backend + React frontend + persistent job queue
```

Acceptance criteria:

- User can type: Launch OldFarmTrucks.com as a classic truck dealership.
- UI returns a workflow plan.
- User can run dry-run.
- UI shows generated reports and run status.
- No write/external side effect occurs by default.

---

## 12. Dashboard Backlog

Single-user business operation needs dashboards for:

```text
workflow runs
scheduled tasks
approvals
expenses and budget
runtime costs
connector status
local app health
knowledge base status
skill inventory
skill gaps
business KPIs
customer lifecycle
inventory and market scans
security findings
```

MVP dashboard options:

```text
Streamlit dashboard
Metabase connected to Postgres
Grafana for runtime/ops metrics
Temporal UI for workflow execution
Qdrant dashboard/API for memory collections
```

Create:

```text
apps/dashboard/
apps/dashboard/streamlit_dashboard.py
scripts/reports/generate_dashboard_data.py
schemas/dashboard-state.schema.json
reports/dashboard_state.json
```

---

## 13. Rate Limit and Quota Management Backlog

Create:

```text
core/rate-limit-manager/
skills/rate-limit-analysis/
schemas/rate-limit-policy.schema.json
references/rate-limit-and-quota-standard.md
scripts/validation/validate_rate_limit_policies.py
scripts/reports/generate_rate_limit_report.py
```

Track limits for:

```text
LLM APIs
embedding APIs
GitHub API
Gmail/Google APIs
CRM APIs
CDP APIs
ERP/accounting APIs
helpdesk APIs
local app APIs
database connection pools
Qdrant requests
Temporal task queues
Redis memory/ops
Postgres connections
scraping targets
email sending
SMS sending
market data APIs
legal/tax/economic data APIs
```

Required rate-limit policy fields:

```yaml
service:
operation:
limit_type: rpm | rph | rpd | concurrent | tokens_per_minute | cost_budget | connection_pool | storage | task_queue
limit:
window:
burst:
backoff_policy:
retry_after_source:
priority:
degradation_mode:
alert_threshold:
hard_stop_threshold:
owner:
```

Acceptance criteria:

- Connectors declare rate-limit policies.
- Scheduler respects connector quotas.
- Workflows can degrade to cached/stale/read-only mode when limits are reached.
- Reports show current quota usage and recent throttling.

---

## 14. Budget and Cost Tracking Backlog

Create:

```text
core/runtime-economics/
skills/budget-monitoring/
skills/api-cost-analysis/
skills/llm-token-cost-tracking/
skills/workflow-cost-attribution/
schemas/cost-event.schema.json
reports/cost_dashboard.md
reports/cost_dashboard.json
```

Track:

```text
LLM token spend
embedding spend
API usage spend
market data subscriptions
email/SMS cost
cloud/server cost
local app resource cost estimate
workflow cost
skill cost
schedule cost
connector cost
```

Acceptance criteria:

- Every workflow run can report estimated cost.
- Scheduler can block or warn on budget thresholds.
- Dashboard shows daily/weekly/monthly spend.

---

## 15. Backup and Restore for Docker Deployment

Create:

```text
scripts/docker/backup-stack.sh
scripts/docker/restore-stack.sh
docs/onboarding/DOCKER_BACKUP_RESTORE.md
```

Backup scope:

```text
Postgres
Qdrant
Temporal state if used
Redis if durable data is stored
runtime artifacts
reports
local app volumes
configuration snapshots excluding secrets
```

Acceptance criteria:

- Backup creates manifest and checksums.
- Restore has dry-run preview.
- Secrets are excluded unless explicitly encrypted.

---

## 16. Security Hardening for Docker Deployment

Create:

```text
docs/governance/docker-security-baseline.md
scripts/docker/check-security-baseline.py
```

Controls:

```text
non-root container user
read-only filesystem where possible
least-privilege volumes
no secrets in image layers
.env excluded from git
health check endpoints protected in server mode
network segmentation
write actions disabled by default
admin ports bound to localhost by default
TLS/reverse proxy guidance for server mode
image vulnerability scanning
```

---

## 17. Recommended Implementation Order

1. Dockerfile and `.dockerignore`.
2. `.env.example`.
3. Core `docker-compose.yml` with Qdrant, Temporal, Postgres, Redis, apotheon-cli.
4. Container smoke tests.
5. Worker and scheduler services.
6. Docker deployment docs.
7. Chat UI MVP.
8. Dashboard MVP.
9. Rate-limit manager.
10. Budget/cost dashboard.
11. Local app compose profiles.
12. Backup/restore scripts.
13. Docker security baseline.
14. Server deployment compose file.

---

## 18. Release Acceptance Criteria

Docker deployment is complete when:

```text
[ ] Docker image builds reproducibly
[ ] Core compose stack starts locally
[ ] Qdrant, Temporal, Postgres, and Redis are healthy
[ ] Validation commands run inside container
[ ] Workflow dry-run works inside container
[ ] Worker service starts
[ ] Scheduler service starts in dry-run mode
[ ] Health report is generated
[ ] Chat UI MVP can submit an objective and display workflow plan
[ ] Dashboard MVP displays runs, schedules, costs, and health
[ ] Rate-limit policies exist for connectors and APIs
[ ] Budget/cost reports exist
[ ] Backup/restore dry-run exists
[ ] Docker security baseline passes
[ ] Documentation includes laptop and server setup
```
