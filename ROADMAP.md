# Apotheon SDLC Skills — Roadmap

## Current Release: v0.1 (Local Runtime)

Core infrastructure is operational for local development and testing.

### Completed
- 13 domain SDLC skills (requirements → executive-reporting)
- 70+ business domain skills across finance, customer, inventory, HR, legal
- GTM skill pack (8 skills)
- Control-plane: orchestration, memory, policy engine, observability, billing
- Local execution engine with dry-run and HITL support
- Domain workflow planners (business, finance, customer, inventory)
- Schedule registry with cron/interval/event modes
- Workflow plan schema and validator
- Premerge gate suite (20 gates)
- Docker Compose local stack (Qdrant, Temporal, Postgres, Redis, Ollama)
- FastAPI application server with JWT auth, RBAC, WebSocket gateway
- Alembic database migrations
- Prometheus metrics + OpenTelemetry tracing
- VS Code extension
- Helm chart + Terraform (EKS)

## Near-Term (v0.2)

- OldFarmTrucks.com reference implementation (end-to-end)
- Live Temporal workflow integration
- Semantic cache layer (Qdrant)
- Multi-tenant billing enforcement
- Connector integrations (Stripe, HubSpot, QuickBooks)

## Medium-Term (v0.3)

- Agent-to-agent coordination (multi-agent runtime)
- Federated deployment (multi-region)
- Model routing and cost optimization
- Self-improving skill factory

## Long-Term

- Autonomous OS bootstrap (zero-config onboarding)
- World model integration
- Reinforcement learning from operator feedback

## Documentation maturity
- Centralized docs index and onboarding navigation.
- OldFarmTrucks demo quickstart + video script.
- API/docs/examples coverage with automated docs integrity checks.
