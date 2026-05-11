# Deployment Guide

This document covers deploying the Apotheon runtime stack for local development,
staging, and production environments.

---

## Prerequisites

| Dependency | Minimum Version | Purpose |
|---|---|---|
| Python | 3.11+ | Script execution |
| Docker | 24.x | Qdrant, Temporal containers |
| Docker Compose | 2.x | Local stack orchestration |
| Qdrant | 1.9+ | Vector memory store |
| Temporal | 1.24+ | Durable workflow engine |
| Anthropic API key | — | LLM inference for skills |

---

## Local Development Stack

### 1. Start infrastructure services

```bash
# From repo root
docker compose up -d qdrant temporal temporal-ui
```

Default ports:
- Qdrant: `http://localhost:6333` (dashboard: `http://localhost:6333/dashboard`)
- Temporal: `localhost:7233` (gRPC)
- Temporal UI: `http://localhost:8080`

### 2. Initialize Qdrant collections

```bash
python scripts/memory/init_collections.py
```

Expected output:
```json
{
  "status": "ok",
  "collections": {
    "apotheon-observations": "created",
    "apotheon-knowledge": "created",
    "apotheon-decisions": "created"
  }
}
```

### 3. Initialize Temporal namespace

```bash
python scripts/runtime/init_temporal_namespace.py
```

### 4. Set environment variables

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export QDRANT_URL=http://localhost:6333
export TEMPORAL_HOST=localhost:7233
export TEMPORAL_NAMESPACE=apotheon-dev
export EXECUTION_MODE=local          # or: temporal
```

### 5. Start Temporal worker (if using Temporal mode)

```bash
pip install temporalio
python scripts/runtime/temporal_worker.py
```

### 6. Run a workflow

```bash
# Plan → execute pipeline
python scripts/orchestration/plan_workflow.py "Build a secure REST API" | \
  python scripts/runtime/execute_workflow.py

# GTM workflow
python scripts/orchestration/plan_gtm_workflow.py "Launch developer tools product" | \
  python scripts/runtime/execute_workflow.py

# Dry run (no LLM calls)
python scripts/runtime/execute_workflow.py --plan workflow_plan.json --dry-run
```

---

## Docker Compose Reference

Create `docker-compose.yml` at the repo root if not present:

```yaml
version: "3.9"

services:
  qdrant:
    image: qdrant/qdrant:v1.9.0
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - qdrant_data:/qdrant/storage

  temporal:
    image: temporalio/auto-setup:1.24.0
    ports:
      - "7233:7233"
    environment:
      - DB=sqlite
    depends_on: []

  temporal-ui:
    image: temporalio/ui:2.26.0
    ports:
      - "8080:8080"
    environment:
      - TEMPORAL_ADDRESS=temporal:7233

volumes:
  qdrant_data:
```

---

## Staging and Production

### Secret management

Production deployments must use HashiCorp Vault:

```bash
export VAULT_ADDR=https://vault.internal
export VAULT_TOKEN=hvs.XXX
```

Secrets are stored at `secret/connectors/<secret-name>` and resolved by
`scripts/connectors/base_connector.py:resolve_secret()`.

### Connector health checks

After deployment, verify all connectors are reachable:

```bash
python scripts/connectors/health_check.py --json
```

All connectors should report `"status": "OK"`.

### Scaling the Temporal worker

For production, run multiple worker replicas and increase concurrency:

```bash
MAX_CONCURRENT_ACTIVITIES=20 python scripts/runtime/temporal_worker.py
```

Use Kubernetes `Deployment` with `replicas: 3` for production workloads.

### Qdrant in production

- Use Qdrant Cloud or a self-hosted cluster with replication (`replication_factor: 2`)
- Set `EMBEDDING_DIMS=1536` for OpenAI embeddings (vs. 768 for Ollama)
- Enable payload indexes — `init_collections.py` creates them automatically

---

## Validation After Deployment

```bash
# 1. Skill structure
python scripts/validation/validate_skill_structure.py .

# 2. Frontmatter
python scripts/validation/validate_frontmatter.py .

# 3. Connector health
python scripts/connectors/health_check.py

# 4. End-to-end dry run
python scripts/orchestration/plan_workflow.py "Test deployment" | \
  python scripts/runtime/execute_workflow.py --dry-run

# 5. Full test suite
pytest
```

All checks must pass before traffic is routed to a new deployment.

---

## Environment Variable Reference

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Required.** Anthropic API key |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model for skill execution |
| `MAX_TOKENS` | `4096` | Max output tokens per skill call |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant server URL |
| `EMBEDDING_DIMS` | `768` | Vector dimensions |
| `EMBEDDING_BACKEND` | `ollama` | `ollama` or `openai` |
| `OPENAI_API_KEY` | — | Required if EMBEDDING_BACKEND=openai |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `EXECUTION_MODE` | `local` | `local` or `temporal` |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal gRPC address |
| `TEMPORAL_NAMESPACE` | `apotheon-dev` | Temporal namespace |
| `TEMPORAL_TASK_QUEUE` | `apotheon-sdlc` | Temporal task queue |
| `MAX_CONCURRENT_ACTIVITIES` | `10` | Temporal worker concurrency |
| `VAULT_ADDR` | — | HashiCorp Vault address (optional) |
| `VAULT_TOKEN` | — | HashiCorp Vault token (optional) |
| `LOG_LEVEL` | `INFO` | Python logging level |
| `SKILLS_ROOT` | `<repo>/skills` | Override skills directory path |

---

## Docker-first local onboarding

Use the Docker-focused runbooks for current startup and verification commands:

- `docs/onboarding/DOCKER_DEPLOYMENT.md`
- `docs/onboarding/DOCKER_TROUBLESHOOTING.md`
