# APOTHEON — DOCKER DEPLOYMENT AND PRODUCTIZATION BACKLOG

**Status:** DEPLOYMENT SIMPLIFICATION + EXECUTABLE PRODUCTIZATION PLAN  
**Purpose:** Make Apotheon easy to run locally, demo, test, schedule, observe, and eventually deploy for single-user or small-business use through Docker Compose, while converting markdown-heavy skill specifications into verifiable executable workflows.

---

## 0. Productization Risk Being Addressed

This document directly addresses the current productization concern that Apotheon may be too spec-heavy unless the runtime, reference workflows, UI, dashboards, reliability, and deployment path are made executable and easy to validate.

Key critique incorporated:

- Turn markdown contracts into verifiable executable components.
- Provide 5-10 complete reference workflows.
- Harden reliability, observability, error handling, and Temporal durability.
- Focus on an MVP skill set before broad domain expansion.
- Make the project accessible on normal laptops, not only high-end hardware.
- Provide a single-user chat/dashboard experience.
- Add rate limits, budget tracking, connector limits, and API/database quotas.
- Add deployable Docker profiles for local solo, team, and enterprise use.

Source planning input: user-provided critique and execution recommendations. fileciteturn46file0

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

## 2. MVP Product Scope

To avoid over-building, define a release-oriented MVP skill set.

### MVP Skill Set

```text
core orchestration
workflow runtime
skill activity runtime
memory/context manager
governance/HITL
SDLC feature workflow
GTM launch workflow
basic finance/accounting workflow
customer lifecycle workflow
OldFarmTrucks.com demo workflow
observability/reporting
Docker deployment
chat UI MVP
dashboard MVP
```

### Non-MVP handling

Ultra-niche or high-risk domain skills may remain as:

```text
stub
spec-only
research-only
not-enabled-by-default
requires enterprise profile
requires governance review
```

Acceptance criteria:

- MVP profile can run on a normal laptop.
- MVP profile has executable reference workflows.
- Non-MVP skills are clearly labeled and excluded from default scheduler execution.

---

## 3. Target Docker Architecture

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
    ├── apotheon-api
    ├── apotheon-chat-ui
    ├── apotheon-dashboard
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

## 4. Required Docker Files

Create:

```text
Dockerfile
Dockerfile.dev
.devcontainer/devcontainer.json
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
scripts/docker/check-compose-health.py
```

---

## 5. Core Services

### apotheon-cli

Purpose: one-off commands, validation, workflow planning, smoke tests, and report generation.

Example:

```bash
docker compose run --rm apotheon-cli python scripts/run_premerge_checks.py
```

### apotheon-worker

Purpose: workflow execution workers.

```bash
python scripts/runtime/temporal_worker.py
```

### apotheon-scheduler

Purpose: due schedules, initially dry-run only.

```bash
python scripts/schedules/run_due_schedules.py --loop --dry-run
```

### apotheon-reports

Purpose: periodic local ops, readiness, health, runtime, and budget reports.

```bash
python scripts/reports/generate_local_ops_report.py
```

### apotheon-api

Purpose: local HTTP API for chat UI, dashboards, workflow runs, schedules, approvals, reports, memory, and health.

Candidate implementation:

```text
FastAPI
Postgres for state
Redis for queue/cache
```

### apotheon-chat-ui

Purpose: browser UI for single-user interaction.

MVP implementation:

```text
Streamlit frontend calling local scripts/API
```

Later implementation:

```text
FastAPI + React + persistent job queue
```

### apotheon-dashboard

Purpose: browser dashboards for workflows, schedules, approvals, budget/cost, connectors, local apps, knowledge, and runtime health.

MVP implementation:

```text
Streamlit dashboard + generated dashboard_state.json
```

---

## 6. Infrastructure Services

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
metabase
```

---

## 7. Docker Compose Profiles

Define profiles:

```text
local-solo
team
enterprise
core
runtime
scheduler
reports
api
ui
dashboard
observability
local-apps
security
all
```

Example usage:

```bash
# Single-user laptop MVP
docker compose --profile local-solo up -d

# Runtime plus worker and scheduler
docker compose --profile runtime --profile scheduler up -d

# Add API, UI, and dashboard
docker compose --profile api --profile ui --profile dashboard up -d

# Add observability
docker compose --profile observability up -d
```

---

## 8. Environment Configuration

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
APOTHEON_MVP_PROFILE=local-solo
APOTHEON_MAX_WORKFLOW_COST_USD=2.00
APOTHEON_MAX_DAILY_COST_USD=10.00
APOTHEON_CONNECTOR_READ_ONLY_DEFAULT=true
```

Rules:

- `.env` must never be committed.
- `.env.example` must contain no secrets.
- Write actions are disabled by default.
- Scheduler defaults to dry-run.
- Connectors default to read-only.

---

## 9. Executable Runtime Depth

Create or harden:

```text
scripts/runtime/skill_activity.py
scripts/runtime/execute_workflow.py
scripts/runtime/output_parser.py
scripts/runtime/model_router.py
scripts/runtime/local_model_fallback.py
scripts/runtime/schema_validation.py
scripts/runtime/retry_policy.py
```

Requirements:

- Full LLM invocation for live mode.
- Dry-run mode with no external model/API side effects.
- Structured output parsing.
- JSON schema validation of skill output.
- Retry logic by error category.
- Fallback to local model where configured.
- HITL gate detection.
- Workflow run records.
- Correlation IDs.
- Token/cost estimates.

Acceptance criteria:

- Runtime can execute 5-10 reference workflows end-to-end.
- Failed model outputs generate structured validation errors.
- Local fallback is attempted only when policy allows.
- Dry-run tests prove no external calls occur.

---

## 10. Reference Workflow Implementations

Create executable demos under:

```text
workflows/examples/
reports/reference_workflows/
tests/reference_workflows/
```

Required reference workflows:

```text
SDLC feature build
GTM launch
accounting/month-end close support
OldFarmTrucks.com launch readiness
OldFarmTrucks.com customer lifecycle
cash forecast
knowledge research/evidence pack
data-security access review
connector health review
weekly operating review
```

Each workflow must include:

```text
workflow plan JSON/YAML
fixtures
expected artifacts
expected reports
dry-run test
live-mode documentation
failure scenario test
```

Acceptance criteria:

- At least 5 workflows execute end-to-end in dry-run.
- At least 3 workflows execute live with model calls in controlled mode.
- OldFarmTrucks.com is maintained as the living demo.

---

## 11. Skill Maturity and Certification

Create or extend:

```text
scripts/grade_skill_maturity.py
scripts/certify_skill.py
reports/skill_maturity_report.md
reports/skill_certification_report.md
tests/skills/test_skill_maturity.py
```

Maturity levels:

```text
0 = spec only
1 = valid SKILL.md
2 = V9 manifest + schema contract
3 = executable dry-run
4 = executable live-mode or deterministic Python activity
5 = certified with evals, tests, telemetry, governance, and examples
```

Target:

```text
>70% of MVP skills at level 3+
>50% of MVP skills at level 4+
critical/high-risk MVP skills at level 5
```

---

## 12. Hybrid Skill Execution

Migrate core skills to hybrid mode:

```text
Markdown prompt contract
+ optional Python activity implementation
+ deterministic scripts for data/API operations
+ schema-validated output
```

Prioritize deterministic Python activities for:

```text
data ingestion
connector reads
schema validation
cost calculation
rate-limit checks
policy checks
schedule calculations
file/report generation
```

Acceptance criteria:

- Deterministic steps do not rely on LLM generation.
- LLM is used for reasoning, synthesis, drafting, and planning.
- Python activities are unit-tested.

---

## 13. Chat UI Backlog

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
show estimated cost before execution
show rate-limit warnings
```

Acceptance criteria:

- User can type: Launch OldFarmTrucks.com as a classic truck dealership.
- UI returns a workflow plan.
- User can run dry-run.
- UI shows generated reports and run status.
- UI blocks live writes by default.
- UI displays approval requirements before execution.

---

## 14. Dashboard Backlog

Single-user business operation needs dashboards for:

```text
workflow runs
scheduled tasks
approvals
expenses and budget
runtime costs
connector status
connector rate limits
local app health
knowledge base status
skill inventory
skill maturity
skill gaps
business KPIs
customer lifecycle
inventory and market scans
security findings
errors/retries/circuit breakers
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

## 15. Reliability, Error Handling, and Observability

Implement or integrate the hardening backlog:

```text
APOTHEON_HARDENING_AND_ERROR_HANDLING_BACKLOG.md
```

Required capabilities:

```text
structured error envelope
retry/backoff/circuit breaker
workflow checkpoint and resume
Temporal replay
compensation on failure
audit trail
OpenTelemetry traces
Prometheus metrics
runtime diagnostics
failure injection tests
```

Acceptance criteria:

- Every workflow run has correlation ID.
- Errors are structured and actionable.
- Circuit breakers prevent repeated failing connector calls.
- Temporal workflows support replay/checkpointing for macro-cycle orchestrations.

---

## 16. Token, Context, Cache, and Retrieval Optimization

Create or harden:

```text
core/memory-token-management/
core/semantic-cache/
scripts/memory/build_context_packet.py
scripts/memory/retrieve_context.py
scripts/reports/generate_context_budget_report.py
```

Requirements:

- Token budget per skill/workflow.
- Progressive disclosure.
- Semantic cache with Qdrant.
- Retrieval source ranking.
- Stale context detection.
- Contradiction detection hooks.
- Cost and latency estimates.

Acceptance criteria:

- Context budget report generated.
- Workflows fail or degrade gracefully when budget exceeded.
- Cached outputs are lineage-aware and invalidated safely.

---

## 17. Governance Enforcement

Implement enforceable runtime guards, not just docs.

Create or harden:

```text
core/policy-engine/
core/business-approval-gateway/
scripts/governance/validate_policy_links.py
scripts/governance/validate_hitl_for_actions.py
scripts/governance/enforce_runtime_policy.py
```

Required:

- Financial controls.
- External action policy.
- HR high-impact policy.
- Trading/tax/legal boundaries.
- Security mutation boundaries.
- Customer communication approvals.

Acceptance criteria:

- High-risk actions fail closed without approval.
- Policy decisions are logged.
- Approval queue appears in UI/dashboard.

---

## 18. Rate Limit and Quota Management

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

## 19. Budget and Cost Tracking

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

- Every workflow run reports estimated cost.
- Scheduler can block or warn on budget thresholds.
- Dashboard shows daily/weekly/monthly spend.
- UI shows estimated cost before workflow execution.

---

## 20. Modular Packaging Profiles

Create profiles:

```text
profiles/local-solo.yaml
profiles/team.yaml
profiles/enterprise.yaml
profiles/mvp.yaml
profiles/full-domain-lab.yaml
```

Profiles control:

```text
enabled skills
enabled planners
enabled schedules
enabled connectors
enabled local apps
resource limits
default model routing
write-action policy
budget limits
```

Acceptance criteria:

- `local-solo` runs on consumer hardware.
- `mvp` includes only release-critical skills.
- `enterprise` enables advanced governance/connectors.
- Docker Compose profiles align with product profiles.

---

## 21. Accessibility and Consumer Hardware Support

Requirements:

```text
CPU-first defaults
small local model support
cloud fallback when configured
selective skill loading
minimal local-solo profile
quantized model guidance
resource usage reporting
```

Create:

```text
docs/onboarding/CONSUMER_HARDWARE_SETUP.md
scripts/reports/generate_resource_usage_report.py
```

Acceptance criteria:

- Local solo profile can run without DGX-class hardware.
- Heavy local models are optional.
- Cloud model fallback is configurable.

---

## 22. VS Code / Developer Experience

Create or improve:

```text
extensions/vscode/
```

Capabilities:

```text
skill authoring assistance
frontmatter validation
dry-run workflow launch
skill maturity panel
workflow/dashboard link
error diagnostics
```

---

## 23. Local Open-Source App Profiles

Add local Docker-deployable business app profiles:

```text
CRM: Twenty CRM or EspoCRM
CDP/analytics: PostHog
Marketing: Mautic or Listmonk
BI: Metabase
Automation: n8n
ERP/accounting/inventory: ERPNext or Odoo Community
Helpdesk: Zammad or Chatwoot
Knowledge: BookStack or Wiki.js
Identity: Keycloak or Authentik
Secrets: Vault or Infisical
Observability: Prometheus + Grafana + Loki
Security: Wazuh / DefectDojo / Trivy
```

Create:

```text
local_apps/docker-compose.local-apps.yml
local_apps/manifests/*.yaml
scripts/local_apps/check_app_health.py
reports/local_app_health_report.md
```

---

## 24. Backup and Restore for Docker Deployment

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

## 25. Security Hardening for Docker Deployment

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

## 26. Documentation, API Docs, and Demo Assets

Create or improve:

```text
README.md
docs/onboarding/DOCKER_DEPLOYMENT.md
docs/onboarding/LOCAL_LAPTOP_SETUP_RUNBOOK.md
docs/onboarding/TROUBLESHOOTING.md
docs/onboarding/OPERATOR_RUNBOOK.md
docs/api/
docs/examples/
CONTRIBUTING.md
ROADMAP.md
```

Required assets:

```text
architecture diagrams
quickstart tutorial
single-user tutorial
OldFarmTrucks demo tutorial
video demo script
API docs for FastAPI if implemented
issue templates
contribution workflow
```

---

## 27. Container Smoke Tests

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
docker compose run --rm apotheon-cli pytest --tb=short -q
```

---

## 28. Phase 1 MVP Execution Plan

Target timeline:

```text
4-8 weeks
```

Goal:

```text
Users can reliably run SDLC and basic business operations workflows locally.
```

Phase 1 tasks:

```text
[ ] Dockerfile + compose core services
[ ] .env.example
[ ] skill activity runtime hardening
[ ] execute_workflow live/dry-run reliability
[ ] 5 executable reference workflows
[ ] chat UI MVP
[ ] dashboard MVP
[ ] rate-limit policy skeleton
[ ] budget/cost report skeleton
[ ] governance runtime enforcement for writes
[ ] container smoke tests
[ ] local-solo profile
[ ] docs quickstart
```

Success metrics:

```text
runnable demos
>50% MVP skills executable
passing end-to-end tests
user feedback from beta testers
reduced manual intervention in workflow loops
no dry-run side effects
```

---

## 29. Recommended Implementation Order

1. Dockerfile and `.dockerignore`.
2. `.env.example`.
3. Core `docker-compose.yml` with Qdrant, Temporal, Postgres, Redis, apotheon-cli.
4. Runtime execution hardening.
5. Reference workflow fixtures.
6. Container smoke tests.
7. Worker and scheduler services.
8. Docker deployment docs.
9. Chat UI MVP.
10. Dashboard MVP.
11. Rate-limit manager.
12. Budget/cost dashboard.
13. Modular profiles.
14. Local app compose profiles.
15. Backup/restore scripts.
16. Docker security baseline.
17. Server deployment compose file.
18. VS Code/devcontainer enhancements.

---

## 30. Release Acceptance Criteria

Docker/productization is complete when:

```text
[ ] Docker image builds reproducibly
[ ] Core compose stack starts locally
[ ] Qdrant, Temporal, Postgres, and Redis are healthy
[ ] Validation commands run inside container
[ ] Workflow dry-run works inside container
[ ] At least 5 reference workflows execute end-to-end in dry-run
[ ] At least 3 reference workflows execute live in controlled mode
[ ] Worker service starts
[ ] Scheduler service starts in dry-run mode
[ ] Health report is generated
[ ] Chat UI MVP can submit an objective and display workflow plan
[ ] Dashboard MVP displays runs, schedules, costs, rate limits, and health
[ ] Rate-limit policies exist for connectors and APIs
[ ] Budget/cost reports exist
[ ] Governance runtime blocks high-risk writes by default
[ ] Backup/restore dry-run exists
[ ] Docker security baseline passes
[ ] Documentation includes laptop and server setup
[ ] OldFarmTrucks.com demo is executable
```
