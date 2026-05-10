# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Apotheon** is an AI Company Operating System — a full-stack platform for orchestrating the complete software development lifecycle (SDLC) and go-to-market (GTM) workflows using Claude. It combines:

- **214 domain skill definitions** (behavioral contracts in `SKILL.md` format)
- **76 core platform domains** (control-plane infrastructure)
- **A FastAPI runtime application** (`app/`) with DB, auth, billing, governance, and observability
- **A CLI** (`apotheon` command via `cli.py`) for local execution
- **A full infrastructure stack** (Qdrant, Temporal, Postgres, Redis, Ollama via Docker Compose)

This is **not** a purely prompt/markdown framework — it has a live runtime application.

---

## Quick Commands

```bash
# ── Validation ────────────────────────────────────────────────────────────────
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .

# ── Tests ─────────────────────────────────────────────────────────────────────
pytest                                        # full suite (257 passing)
pytest tests/runtime/                         # runtime tests only
pytest tests/integration/                     # integration tests

# ── CLI ───────────────────────────────────────────────────────────────────────
apotheon init                                 # first-time setup
apotheon doctor                               # health check all services
apotheon dry-run "<objective>"                # plan without executing
apotheon run "<objective>"                    # plan + execute
apotheon gtm "<objective>"                    # GTM workflow
apotheon status                               # active workflows + HITL queue
apotheon approve <run-id>                     # approve HITL gate
apotheon skill list                           # list all 214 skills
apotheon skill gaps                           # detect missing skill deps
apotheon memory search "<query>"              # semantic search Qdrant
apotheon memory init                          # initialize Qdrant collections
apotheon connector health                     # check connector availability
apotheon validate                             # run all validation checks

# ── Workflow planning ──────────────────────────────────────────────────────────
python scripts/orchestration/plan_workflow.py "<objective>"
python scripts/orchestration/plan_gtm_workflow.py "<objective>"

# ── Skill scaffolding ─────────────────────────────────────────────────────────
python scripts/generators/create_skill.py <skill-name>

# ── Database migrations ────────────────────────────────────────────────────────
alembic upgrade head                          # apply migrations
alembic revision --autogenerate -m "msg"     # generate migration

# ── API server ────────────────────────────────────────────────────────────────
uvicorn app.main:app --reload --port 8000

# ── Infrastructure ────────────────────────────────────────────────────────────
docker compose up -d                          # start infra (Qdrant, Temporal, Postgres, Redis, Ollama)
docker compose --profile full up -d          # infra + API server container
docker compose ps                            # check service health

# ── Linting ───────────────────────────────────────────────────────────────────
ruff check .                                  # lint (line-length 100, configured in pyproject.toml)
```

---

## Architecture

### Layer Overview

```
CLI (cli.py)
  └── Orchestration (scripts/orchestration/) → plan_workflow, route_skill_chain
       └── Runtime (scripts/runtime/) → execute_workflow, skill_activity, hitl_handler
            ├── Memory (scripts/memory/, core/memory-token-management/) → Qdrant + Redis
            ├── Connectors (scripts/connectors/) → Salesforce, Jira, Slack, Stripe, etc.
            └── Telemetry (scripts/telemetry/) → record_telemetry_event

API (app/main.py — FastAPI)
  ├── app/api/v1/ → workflows, approvals, memory, connectors, telemetry, governance, cost
  ├── app/api/websocket/gateway.py → live run updates via Redis pub/sub
  ├── app/auth/ → JWT, RBAC (VIEWER < DEVELOPER < OPERATOR < ADMIN)
  ├── app/db/ → SQLAlchemy async ORM, 13 tables, Alembic migrations
  ├── app/billing/ → pricing, cost estimator, quota enforcer
  ├── app/governance/ → policy engine (BLOCK/WARN/REQUIRE_APPROVAL), risk scorer
  ├── app/observability/ → Prometheus metrics, OpenTelemetry tracing, benchmark regression
  ├── app/memory/router.py → multi-tier (Redis → Qdrant → Postgres)
  ├── app/connectors/ → Vault client, connector registry lifecycle
  └── app/middleware/tenant.py → ContextVar tenant isolation

Skills (skills/ — 214 domain skills)
Core (core/ — 76 control-plane domains)
Agents (agents/ — 16 specialist role definitions)
Shared (shared/ — standards, policies, frameworks, templates)
Deploy (deploy/helm/, deploy/terraform/)
Extensions (extensions/vscode/)
```

### Skill Structure

Every skill lives under `skills/<kebab-case-name>/SKILL.md` (domain) or `core/<kebab-case-name>/SKILL.md` (control-plane). Each `SKILL.md` **must** open with YAML frontmatter:

```yaml
---
name: kebab-case-name
description: one-line description (max 1024 chars, no angle brackets)
metadata:
  version: "x.y.z"
  category: ...
  owner: ...
  maturity: ...
  dependencies: [...]
---
```

**Validation rules (enforced by CI):**
- Folder names must be kebab-case
- `name` must be kebab-case; `description` ≤ 1024 chars; no `<>` in frontmatter
- All `SKILL.md` files must have opening and closing `---`

### Core vs. Domain Skills

- **`core/`** — 76 control-plane domains (orchestration, memory, governance, runtime, billing, observability, api-gateway, policy-engine, etc.)
- **`skills/`** — 214 domain behavioral contracts spanning SDLC, GTM, business ops, AI/ML, safety

### Database Models (app/db/models.py)

13 SQLAlchemy ORM tables:
`Organization`, `User`, `ApiToken`, `WorkflowRun`, `WorkflowStep`, `Approval`, `AuditLog`, `ConnectorRegistration`, `OAuthToken`, `Policy`, `PolicyEvaluation`, `TokenUsage`, `BenchmarkBaseline`

All repositories inject `org_id` for multi-tenant isolation.

### HITL Gate Detection (skill_activity.py)

Three-layer detection, in priority order:
1. **Structured marker** — `<!-- HITL_GATE: {"required": true, "level": "L3", "reason": "..."} -->` in output (authoritative; `required: false` short-circuits lower layers)
2. **Risk list** — `_HITL_REQUIRED_SKILLS` frozenset (cloud-deployment, devsecops, secret-rotation, etc.)
3. **Phrase fallback** — matches phrases like "requires approval", "human approval"

### Observability Wiring

- `skill_activity.py` → records `skill_latency_seconds`, `token_usage_total`, `llm_call_duration_seconds`, `hitl_gates_total` (Prometheus)
- `execute_workflow.py` → records `workflow_runs_total`, `workflow_duration_seconds`
- `app/observability/benchmark.py` → rolling p50/p95/p99 baselines, 20% regression threshold
- `app/observability/tracing.py` → OTel TracerProvider (OTLP or console); `_NoopTracer` fallback

### Governance / Policy Engine

- `app/governance/policy_engine.py` — restricted DSL `eval()` against `EvalContext`; actions: BLOCK / WARN / REQUIRE_APPROVAL
- `app/governance/risk_scorer.py` — composite 0-100 score (inherent 50%, HITL history 25%, token volume 10%, compliance flag 15%)

---

## Infrastructure Stack

Services defined in `docker-compose.yml`:

| Service | Image | Port(s) | Purpose |
|---------|-------|---------|---------|
| `qdrant` | qdrant/qdrant:v1.9.0 | 6333, 6334 | Vector memory store |
| `temporal` | temporalio/auto-setup:1.24.2 | 7233-7235 | Durable workflow engine |
| `temporal-ui` | temporalio/ui:2.26.2 | 8080 | Temporal web UI |
| `ollama` | ollama/ollama:latest | 11434 | Local embedding model |
| `postgres` | postgres:16-alpine | 5432 | Structured data / audit log |
| `redis` | redis:7-alpine | 6379 | Hot cache / pub-sub |
| `api` (profile: full) | apotheon:latest | 8000 | FastAPI application server |

Start infra: `docker compose up -d`
Start everything: `docker compose --profile full up -d`

---

## API Endpoints (app/)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/workflows` | Submit workflow plan |
| GET | `/v1/workflows` | List runs |
| GET | `/v1/workflows/{id}` | Get run detail |
| POST | `/v1/approvals/{id}/decide` | Approve/reject HITL gate |
| GET | `/v1/memory/search` | Semantic memory search |
| GET | `/v1/governance/dashboard` | Policy violation metrics |
| GET | `/v1/governance/policies` | List active policies |
| POST | `/v1/cost/estimate` | Pre-flight cost estimate |
| GET | `/v1/telemetry/events` | Audit events |
| GET | `/v1/telemetry/token-usage` | Token usage stats |
| GET | `/metrics` | Prometheus scrape |
| GET | `/health` | Liveness probe |
| WS | `/ws/runs/{run_id}` | Live run updates |

Authentication: JWT Bearer (HS256/RS256). Set `JWT_SECRET` env var.

---

## Environment Variables

| Variable | Default | Required |
|----------|---------|----------|
| `ANTHROPIC_API_KEY` | — | Yes (for skill execution) |
| `DATABASE_URL` | `sqlite+aiosqlite:///./apotheon_dev.db` | No (SQLite default) |
| `REDIS_URL` | `redis://localhost:6379` | No |
| `QDRANT_URL` | `http://localhost:6333` | No |
| `JWT_SECRET` | — | Yes (for API auth) |
| `EXECUTION_MODE` | `local` | No (`local` or `temporal`) |
| `TEMPORAL_HOST` | `localhost:7233` | No |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | No |
| `LOG_LEVEL` | `INFO` | No |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | No |

---

## Optional Dependency Groups (pyproject.toml)

```bash
pip install -e ".[api]"            # FastAPI, SQLAlchemy, Alembic, PyJWT
pip install -e ".[observability]"  # Prometheus, OpenTelemetry
pip install -e ".[temporal]"       # Temporal SDK
pip install -e ".[ui]"             # Rich terminal UI
pip install -e ".[connectors-full]"# httpx, aiohttp, google-auth
pip install -e ".[full]"           # everything
pip install -e ".[dev]"            # pytest, ruff, httpx
```

---

## Deploy

**Helm (Kubernetes):**
```bash
helm install apotheon deploy/helm/apotheon -f deploy/helm/apotheon/values.yaml
```

**Terraform (AWS EKS + RDS + ElastiCache):**
```bash
cd deploy/terraform && terraform init && terraform apply
```

**VS Code Extension:** `extensions/vscode/` — sidebar with workflow runs, HITL queue, and skill browser.

---

## CI Pipeline

`.github/workflows/validate.yml` runs on every push/PR:
1. `validate_skill_structure.py` — kebab-case names, SKILL.md presence
2. `validate_frontmatter.py` — YAML frontmatter validity
3. `pytest` — full test suite

---

## Conventions

- **Branch strategy:** `main` / `develop` / `feature/*` / `hotfix/*` / `experimental/*`
- **Commit scopes:** `feat`, `fix`, `refactor`, `docs`, `test`, `security`, `governance`, `orchestration`, `memory`
- **New skills:** always use `python scripts/generators/create_skill.py <skill-name>` — ensures correct scaffold
- **No `__init__.py` files** in scripts or tests — pytest discovers without them
- **Windows compatibility:** use ASCII in console output (no `✓✗⏸—`); use `OK/FAIL/HITL/-`
- **Graceful degradation:** all optional services (Qdrant, Redis, Prometheus, OTel) fail silently — the core CLI works without them