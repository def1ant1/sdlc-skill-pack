# Apotheon AI Company OS

An AI-native Autonomous Company Operating System built as a Claude Code skill-pack.
Apotheon orchestrates the complete company lifecycle — from strategic planning and
product development through deployment, GTM, customer success, revenue optimization,
business operations, and continuous self-improvement — running primarily on local
hardware with cloud as optional overflow.

---

## What It Is

Apotheon is a **prompt/markdown-based framework**: SKILL.md files are behavioral
contracts that tell Claude how to operate each domain. There is no compiled application.
The intelligence is in the orchestration, the memory system, the knowledge graph, and
183+ integrated skills spanning every function of a software company — engineering,
cognitive runtime, AI safety, enterprise intelligence, business operations, infrastructure
optimization, governance, and autonomous self-improvement.

The platform is designed to run fully locally on a DGX Spark (128GB unified VRAM)
using Ollama, vLLM, Qwen, llama.cpp, and SGLang. Cloud models (Claude, GPT-4o) are
used for quality-critical tasks and as overflow when local capacity is saturated.

---

## The Autonomous OS Loop

```
PLAN --> BUILD --> SHIP --> GROW
  ^                           |
  +---------- LEARN ----------+
         |
       OPERATE
```

| Macro-Cycle | Skills | Cadence |
|---|---|---|
| PLAN | strategic-planning, product-analytics, decision-intelligence, hierarchical-planning, long-horizon-planning | Weekly |
| BUILD | sdlc-orchestration, multi-agent, sandbox-execution, lora-lifecycle, developer-experience, model-lifecycle | Continuous |
| SHIP | cloud-deployment, mcp-integrations, compliance-automation, local-security, release-management | Per release |
| GROW | launch-planning, seo-engineering, content-marketing, ai-search-optimization, paid-acquisition, analytics-intelligence, customer-success, revenue-optimization | Weekly |
| LEARN | model-evaluation, lora-lifecycle, synthetic-data, telemetry, skill-gap-engine, evolution-engine, benchmark-factory | Weekly |
| OPERATE | business-orchestration, accounting-automation, budget-planning, legal-ops, workforce-management, vendor-procurement | Continuous |
| PROTECT | alignment-engine, privacy-runtime, deception-detection, adversarial-evaluation, policy-simulation | Continuous |
| REASON | cognitive-runtime, predictive-reasoning, simulation-engine, research-runtime, causal-analysis | On-demand |

---

## Quick Start

### Validate the skill pack

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
pytest
```

### Run an SDLC workflow

```bash
# Plan → execute pipeline
python scripts/orchestration/plan_workflow.py "Build a secure REST API" | \
  python scripts/runtime/execute_workflow.py

# Dry run (plan only, no LLM calls)
python scripts/orchestration/plan_workflow.py "Build a secure REST API" | \
  python scripts/runtime/execute_workflow.py --dry-run

# Save plan to file and execute later
python scripts/orchestration/plan_workflow.py "Design a payment service" > plan.json
python scripts/runtime/execute_workflow.py --plan plan.json
```

### Run a GTM workflow

```bash
# Full GTM motion from objective
python scripts/orchestration/plan_gtm_workflow.py "Launch developer tools to enterprise market" | \
  python scripts/runtime/execute_workflow.py

# GTM dry run
python scripts/orchestration/plan_gtm_workflow.py "Reduce churn rate by 20%" | \
  python scripts/runtime/execute_workflow.py --dry-run
```

### Detect skill gaps

```bash
python scripts/orchestration/detect_skill_gaps.py
```

### Connector health checks

```bash
python scripts/connectors/health_check.py
python scripts/connectors/health_check.py --connector salesforce --json
```

### Initialize runtime infrastructure

```bash
# Qdrant vector collections
python scripts/memory/init_collections.py

# Temporal namespace
python scripts/runtime/init_temporal_namespace.py

# Start durable workflow worker (requires: pip install temporalio)
EXECUTION_MODE=temporal python scripts/runtime/temporal_worker.py
```

### Scaffold a new skill

```bash
python scripts/generators/create_skill.py <skill-name>
```

### Bootstrap the Autonomous OS

```bash
python scripts/orchestration/autonomous_os_bootstrap.py
```

---

## Repository Layout

```
core/                          63 control-plane skills (orchestration, memory, security, runtime)
  autonomous-os/               Capstone: closed-loop OS orchestrator
  sdlc-orchestration/          SDLC workflow routing and phase coordination
  workflow-engine/             DAG execution backbone for all cross-skill automation
  workflow-runtime/            Durable execution: checkpointing, state recovery, replay
  temporal-integration/        Temporal workflow definitions and activity registration
  ray-runtime/                 Ray cluster orchestration for distributed workloads
  skill-gap-engine/            Self-auditing skill registry scanner and gap detector
  evolution-engine/            Autonomous self-improvement: gap→proposal→approval→execution
  cognitive-runtime/           Goal decomposition, hierarchical planning, adaptive replanning
  agent-kernel/                Multi-agent process isolation, resource quotas, lifecycle
  agent-identity/              Persistent agent expertise, episodic/semantic memory
  distributed-agent-runtime/   Multi-node agent coordination with load balancing
  alignment-engine/            Constitutional compliance, deception detection, safety
  hitl-dashboard/              Human-in-the-loop CLI, dashboard, approval queue
  governance/                  Policy registry, approval authority matrix, AI governance
  model-lifecycle/             Model promotion gates, canary deployment, quality monitoring
  memory-token-management/     Persistent workflow state and token budgeting
  retrieval-engine/            VectorRAG + GraphRAG + KV cache hybrid retrieval
  knowledge-graph/             11-entity organizational knowledge model
  connector-hub/               Unified connector abstraction for all integrations
  mcp-integrations/            GitHub/Jira/Slack/Figma/Sentry/Datadog/Vercel/Cloudflare
  ... (50+ additional control-plane skills)

skills/                        120 domain skills covering the full company lifecycle

  -- Engineering (Phases 1-13) --
  requirements-engineering/    Requirements capture and specification
  system-architecture/         Architecture design and ADR authoring
  ai-engineering/              AI/ML feature development
  backend-engineering/         Backend services and APIs
  frontend-engineering/        Frontend and UI development
  code-review/                 Automated code review with FAIL/WARN/NOTE findings
  qa-automation/               Test planning, edge case analysis, coverage
  devsecops/                   Security scanning, SAST, supply chain
  release-management/          Release coordination and changelog
  observability/               Monitoring, dashboards, SLOs
  sre-incident-response/       Incident response and post-mortems
  developer-experience/        DX metrics, SPACE framework, onboarding optimization

  -- GTM & Growth (Phases 93-95, V9) --
  launch-planning/             End-to-end product launch: ICP, positioning, readiness gates
  seo-engineering/             Technical SEO, Core Web Vitals, keyword mapping
  content-marketing/           Blog, newsletter, LinkedIn, X, Reddit, YouTube
  ai-search-optimization/      llms.txt, semantic chunking, GEO, AI discoverability
  paid-acquisition/            Google Ads, LinkedIn Ads, campaign structure, ROAS
  analytics-intelligence/      GA4, Mixpanel, event taxonomy, attribution modeling
  customer-success/            Onboarding, health scoring, NPS, churn intervention
  revenue-optimization/        Churn prediction, LTV/CAC, pricing elasticity, MRR waterfall

  -- ML Runtime (Phases 76-79) --
  inference-engine-deployment/ Model serving deployment, fleet management, rollback
  inference-engine-benchmarking/ Latency, throughput, quality, and stability benchmarks
  distributed-training-orchestration/ Ray-based distributed training job management
  ray-serve-management/        Ray Serve deployment patterns: single, router, RAG pipeline

  -- Memory & Learning (Phases 80-82) --
  memory-compression/          Salience-scored observation compression
  temporal-memory-replay/      Timeline reconstruction and RLHF generation via replay
  prompt-optimization/         Mutation strategies: decomposition, CoT, persona, negative space
  workflow-ab-testing/         Thompson Sampling and shadow-mode experiment design
  lessons-learned-extraction/  Post-mortem synthesis and lessons corpus management
  institutional-knowledge-query/ Semantic search across 8 knowledge source types

  -- Sovereign Intelligence (Phases 83-92) --
  belief-state-management/     Entity confidence tracking with decay and contradiction detection
  marketplace-publishing/      8-gate certification: structure, safety, performance, IP
  sdk-authoring/               Skill SDK scaffolding, manifest, sandbox lifecycle
  ... (additional V8 skills)

  -- AI Safety & Alignment (Phase 58) --
  alignment-testing/           Pre-deployment behavioral test suites and scorecards
  harm-classification/         Multi-taxonomy harm scoring and mitigation routing
  deception-detection/         Hallucination, authority escalation, manipulation detection
  adversarial-evaluation/      Structured red team evaluation and agent hardening
  policy-simulation/           Policy change impact simulation before enforcement

  -- Business Operations --
  accounting-automation/       Transaction processing, anomaly detection, approval routing
  budget-planning/             Annual/quarterly budget cycles, variance analysis
  legal-ops/                   Contract lifecycle, NDA routing, risk flagging
  workforce-management/        Employee records, org changes, compensation approvals
  vendor-procurement/          Vendor qualification, spend authority, contract management

  -- Reporting & Governance --
  executive-reporting/         Executive summaries and board-level reporting
  compliance-governance/       Policy enforcement and governance reporting
  continuous-control-monitoring/ Real-time control testing and compliance drift detection

  ... (60+ additional domain skills)

agents/                        9 specialist agent role contracts
  architect/                   Architecture decisions, ADRs, system design
  security/                    STRIDE threat modeling, security findings
  reviewer/                    Code and artifact review with FAIL/WARN/NOTE
  tester/                      Test planning and edge case analysis
  optimizer/                   Performance and cost optimization
  researcher/                  Technical research and comparison analysis
  gtm-agent/                   GTM strategy, ICP, positioning, messaging
  analytics-agent/             Analytics framework, AARRR metrics, experiments
  governance-agent/            Compliance, AI governance, regulatory assessment

shared/                        Cross-cutting resources referenced by all skills
  standards/                   AI governance, architecture, markdown, naming,
                               prompt engineering, security baseline
  policies/                    AI safety, architectural review, data governance,
                               secure development
  references/                  analytics-crm-connectors.md (GA4, Mixpanel, Amplitude,
                               Segment, Intercom, Zendesk, HubSpot, Stripe, PostHog)
  frameworks/                  AI discovery (llms.txt, semantic chunking)
  prompts/                     Reusable prompt templates
  templates/                   Document and output templates
  ontologies/                  Domain ontologies

scripts/                       44 automation, validation, and runtime scripts

  validation/
    validate_skill_structure.py    Kebab-case and SKILL.md presence checks
    validate_frontmatter.py        YAML frontmatter field and format validation

  orchestration/
    plan_workflow.py               SDLC objective → ordered skill chain (JSON)
    plan_gtm_workflow.py           GTM objective → ordered GTM skill chain (JSON)
    detect_skill_gaps.py           Dependency gap scanner with alias suppression
    route_skill_chain.py           Topological skill ordering with dependency expansion
    validate_workflow_state.py     Gate and phase state validation
    autonomous_os_bootstrap.py     Full OS health check and capability report

  runtime/
    skill_activity.py              Core: SKILL.md → Claude API → SkillActivityOutput
    execute_workflow.py            Local sequential and Temporal durable execution
    temporal_worker.py             Temporal worker with ApotheonWorkflow definition
    init_temporal_namespace.py     Idempotent Temporal namespace creation

  memory/
    build_context_packet.py        Context packet construction for skill invocation
    embed_observation.py           Qdrant upsert: Ollama/OpenAI embedding backends
    retrieve_context.py            Semantic retrieval from Qdrant vector store
    init_collections.py            Create apotheon-observations/knowledge/decisions collections

  connectors/
    base_connector.py              BaseConnector ABC: rate limiting, retry, secret resolution
    salesforce_connector.py        Salesforce REST API (SOQL, CRUD, pagination)
    servicenow_connector.py        ServiceNow Table API (incidents, change requests)
    ga4_connector.py               GA4 Data API (runReport, sessions, events)
    slack_connector.py             Slack Web API (messaging, channels, users)
    jira_connector.py              Jira Cloud REST v3 (issues, JQL, transitions)
    health_check.py                Multi-connector health status table/JSON
    auth/
      oauth2_client.py             Client credentials + authorization code flows
      api_key_client.py            Bearer/header/query/basic API key injection
      mtls_client.py               mTLS SSLContext from files or PEM strings

  generators/
    create_skill.py                Scaffold a new skill directory and SKILL.md

docs/
  architecture/
    system-overview.md             Platform architecture overview
    runtime-components.md          Runtime stack: CLI → execution → activity → memory
    agent-fleet.md                 6-agent roster, skill mapping, collaboration patterns
    skill-dependency-graph.md      Cross-skill dependency topology
    skill-lifecycle.md             Skill maturity ladder and promotion criteria
    memory-engine.md               Qdrant + embedding pipeline architecture
    orchestration-engine.md        Workflow planning and routing internals
    orchestration-control-plane.md Core control-plane skill interactions
    governance-model.md            Approval authority matrix and policy registry

  governance/
    hitl-gate-audit.md             183-skill HITL audit: 41 covered, 20 gaps with roadmap

  onboarding/
    getting-started.md             First-run guide for new contributors
    DEPLOYMENT.md                  Local dev, staging, and production deployment
    SKILL_AUTHORING_GUIDE.md       Complete guide: scaffold → write → validate → publish
    GTM_PLANNER_GUIDE.md           GTM planner usage, skill routing, and extension guide

tests/                             12 test files, 190+ passing tests
  validation/                      Skill structure and frontmatter tests
  orchestration/                   Workflow planning and routing regression tests
  skills/                          Skill file content tests
  scripts/                         Script-level unit and integration tests (V9, new)
    test_validate_skill_structure.py
    test_validate_frontmatter.py
    test_sdlc_plan_workflow.py
    test_plan_gtm_workflow.py
    test_detect_skill_gaps.py
    test_build_context_packet.py
```

---

## Runtime Architecture

```
CLI / API Layer
  plan_workflow.py   plan_gtm_workflow.py   execute_workflow.py
          │
          ▼ workflow plan JSON
  Execution Engine
    LOCAL MODE                    TEMPORAL MODE
    execute_local()               temporal_worker.py / ApotheonWorkflow
    (sequential, in-process)      (durable, retryable, signal-driven)
          │
          ▼ SkillActivityInput
  Skill Activity Layer  (skill_activity.py)
    1. load SKILL.md → system prompt
    2. build user message (objective + context packet)
    3. call Claude API (claude-sonnet-4-6)
    4. HITL gate detection
    5. return SkillActivityOutput
          │
    ┌─────┴──────────────────────────┐
    ▼                                ▼
Anthropic API               Memory Layer (Qdrant)
claude-sonnet-4-6           embed_observation.py
                            retrieve_context.py
                            3 collections

  Connector Layer
    BaseConnector (rate limit + retry + secret resolution)
    ├── auth/ (OAuth2, API key, mTLS)
    └── Salesforce / ServiceNow / GA4 / Slack / Jira
```

Context packet accumulates across steps: each completed skill appends its name
to `artifacts` and its last 2000 chars to `additional_context` for the next skill.

---

## HITL Governance

Every skill action is classified by risk level:

| Level | Criteria | Behavior |
|---|---|---|
| **Critical (L3)** | Irreversible production impact, financial transactions, security posture | Blocks — hard approval required |
| **High (L2)** | Infrastructure changes, secret rotation, schema migrations | Waits — soft approval, 4h timeout |
| **Medium (L1)** | Internal state changes, non-production deployments | Async notification, 30-min veto |
| **Low** | Read-only operations, analysis, planning | No gate |

41 of 183 skills have HITL gates declared. The V9 roadmap targets 85%+ coverage
for all critical and high-risk skills. See `docs/governance/hitl-gate-audit.md`.

---

## Platform Capabilities

| Capability | Implementation |
|---|---|
| Full SDLC orchestration | `core/sdlc-orchestration` + 12 engineering skills |
| GTM lifecycle management | `scripts/orchestration/plan_gtm_workflow.py` + 8 GTM skills |
| Durable workflow execution | `scripts/runtime/temporal_worker.py` + `execute_workflow.py` |
| Cognitive runtime | `core/cognitive-runtime` + hierarchical planning + meta-reasoning |
| Autonomous self-improvement | `core/evolution-engine` → gap → proposal → operator approval |
| Distributed agent OS | `core/agent-kernel` + `core/distributed-agent-runtime` |
| AI safety runtime | `core/alignment-engine` + deception detection + red team |
| Vector memory | Qdrant (3 collections) + Ollama/OpenAI embedding backends |
| Business operations | `core/business-orchestration` + 5 domain skills |
| Enterprise connectors | Salesforce, ServiceNow, GA4, Slack, Jira (+ 9 GTM connectors) |
| Governance and policy | `core/governance` + HITL gate audit + approval authority matrix |
| Compliance automation | SOC2/GDPR/HIPAA/ISO27001/EU AI Act/NIST/PCI DSS |
| Local model routing | `core/local-runtime` (Ollama/vLLM/llama.cpp/SGLang) |
| GPU cluster optimization | `core/cluster-management` + topology analysis + VRAM optimization |
| Multi-agent collaboration | 9 registered agents, 5 collaboration patterns |
| Skill validation | Structure + frontmatter + dependency gap detection |

---

## Core Design Principles

1. **Progressive disclosure** — SKILL.md files stay concise. Detail lives in `references/`, `templates/`, and `scripts/`.
2. **Local-first** — Everything runs on DGX Spark (128GB unified VRAM). Cloud models are overflow, not default.
3. **Memory integrity** — The context packet never drops decisions, constraints, or FAIL gate records across a workflow's lifetime.
4. **Governed autonomy** — Every action has a risk level (Low/L1/L2/L3). L3 actions block for human approval. The OS never auto-executes production writes.
5. **Deterministic validation** — Machine-checkable quality gates at every phase transition. Scripts enforce invariants; humans review judgment calls.
6. **Knowledge graph as memory** — All decisions, artifacts, and relationships are written to the organizational knowledge graph for long-term intelligence.
7. **Closed-loop self-improvement** — The OS measures its own output quality, detects model drift, retrains adapters, and optimizes routing within operator-approved boundaries.
8. **Full business coverage** — Every company function has a skill: finance, legal, HR, procurement, forecasting, and decision-making are first-class OS citizens alongside engineering.

---

## Skill Validation Rules

All SKILL.md files must pass:

- Folder name: kebab-case (no underscores, no uppercase)
- SKILL.md opens with valid YAML frontmatter (opening and closing `---`)
- Required frontmatter fields: `name` (kebab-case), `description` (≤ 1024 chars, no `<>`)
- Recommended fields: `metadata.version`, `metadata.category`, `metadata.owner`, `metadata.maturity`, `metadata.dependencies`
- High-risk skills: must declare `hitl_gates` in frontmatter

CI runs on every push/PR: `validate_skill_structure.py` → `validate_frontmatter.py` → `scripts/run_premerge_checks.py` → `pytest`.

Run the same local pre-merge gates before opening a PR:

```bash
python scripts/run_premerge_checks.py
```

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | **Required** for skill execution |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Model for skill activities |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant vector store |
| `EMBEDDING_BACKEND` | `ollama` | `ollama` or `openai` |
| `EXECUTION_MODE` | `local` | `local` or `temporal` |
| `TEMPORAL_HOST` | `localhost:7233` | Temporal server address |
| `VAULT_ADDR` / `VAULT_TOKEN` | — | HashiCorp Vault for connector secrets |
| `LOG_LEVEL` | `INFO` | Python logging level |

Full reference: `docs/onboarding/DEPLOYMENT.md`

---

## Branch and Commit Conventions

**Branches**: `main` / `develop` / `feature/*` / `hotfix/*` / `experimental/*`

**Commit scopes**: `feat` / `fix` / `refactor` / `docs` / `test` / `security` / `governance` / `orchestration` / `memory`

---

## Documentation

| Document | Location |
|---|---|
| Deployment guide | `docs/onboarding/DEPLOYMENT.md` |
| Skill authoring | `docs/onboarding/SKILL_AUTHORING_GUIDE.md` |
| GTM planner guide | `docs/onboarding/GTM_PLANNER_GUIDE.md` |
| Getting started | `docs/onboarding/getting-started.md` |
| Runtime architecture | `docs/architecture/runtime-components.md` |
| Agent fleet | `docs/architecture/agent-fleet.md` |
| HITL gate audit | `docs/governance/hitl-gate-audit.md` |
| System overview | `docs/architecture/system-overview.md` |