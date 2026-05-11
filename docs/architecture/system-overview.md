# System Overview

Apotheon is an AI-native Autonomous Company Operating System — a Claude-powered
platform that orchestrates the complete company lifecycle from a single runtime
using structured skill definitions, durable workflows, and a persistent memory layer.

---

## What Apotheon Is

Apotheon is a **prompt/markdown-based framework** where every capability is a
`SKILL.md` behavioral contract. There is no compiled application. When a skill
runs, its `SKILL.md` becomes a system prompt delivered to Claude, which produces
structured output used by the next step in the chain.

The platform covers:
- **Engineering** — SDLC from requirements through deployment
- **Go-to-Market** — launch, SEO, paid acquisition, analytics, revenue
- **Business operations** — finance, legal, HR, procurement
- **AI infrastructure** — model lifecycle, LoRA training, GPU scheduling
- **Governance** — HITL gates, compliance, AI safety
- **Self-improvement** — gap detection, skill evolution, benchmark generation

**183+ skills** across 120 domain and 63 core directories.

---

## The OS Loop

```
         ┌─────────────────────────────────────────┐
         │            PLAN                         │
         │  strategic-planning, decision-intel,    │
         │  hierarchical-planning, forecasting     │
         └──────────────┬──────────────────────────┘
                        │
         ┌──────────────▼──────────────────────────┐
         │            BUILD                        │
         │  requirements → architecture →           │
         │  ai-engineering → backend → frontend →  │
         │  code-review → qa → devsecops           │
         └──────────────┬──────────────────────────┘
                        │
    ┌───────────────────▼──────────────────────────┐
    │                 SHIP                         │
    │  release-management, cloud-deployment,       │
    │  compliance-automation, local-security       │
    └───────┬────────────────────────┬─────────────┘
            │                        │
    ┌───────▼────────┐    ┌──────────▼──────────────┐
    │     GROW       │    │        OPERATE          │
    │  launch-plan,  │    │  accounting, legal,     │
    │  seo, paid,    │    │  HR, procurement,       │
    │  analytics,    │    │  business-orchestration │
    │  revenue-opt   │    └─────────────────────────┘
    └───────┬────────┘
            │
    ┌───────▼────────────────────────────────────────┐
    │                  LEARN                         │
    │  lessons-learned, benchmark-factory,           │
    │  lora-lifecycle, evolution-engine,             │
    │  skill-gap-engine, model-evaluation            │
    └────────────────────────────────────────────────┘
```

Every cycle writes decisions, artifacts, and observations to the persistent
memory layer (Qdrant), which feeds context into subsequent cycles.

---

## Layer Architecture

```
┌────────────────────────────────────────────────────────────────────┐
│                       INTERFACE LAYER                              │
│  apotheon CLI (cli.py)  |  Operator Console (scripts/ui/)         │
│  HITL Approval (Slack)  |  GitHub Actions CI                      │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────┐
│                    ORCHESTRATION LAYER                             │
│  plan_workflow.py       |  plan_gtm_workflow.py                   │
│  route_skill_chain.py   |  detect_skill_gaps.py                   │
│  execute_workflow.py    |  autonomous_os_bootstrap.py             │
└───────────────────────────────────┬────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────┐
│                      RUNTIME LAYER                                 │
│  skill_activity.py --► Claude API (claude-sonnet-4-6)             │
│  temporal_worker.py    |  hitl_handler.py                         │
│  context_manager.py    |  execute_workflow.py                     │
└────────────────────┬──────────────────────┬────────────────────────┘
                     │                      │
    ┌────────────────▼──────┐   ┌───────────▼────────────────────────┐
    │    MEMORY LAYER       │   │        CONNECTOR LAYER             │
    │  Qdrant (3 colls.)   │   │  Salesforce  ServiceNow  Jira      │
    │  embed_observation    │   │  Slack  GA4  HubSpot  Stripe       │
    │  retrieve_context     │   │  Mixpanel  Amplitude               │
    │  context_manager      │   │  base_connector + auth/            │
    └───────────────────────┘   └────────────────────────────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────┐
│                       SKILL LAYER                                  │
│  core/ (63 control-plane skills)                                   │
│  skills/ (120 domain skills)                                       │
│  agents/ (9 specialist role contracts)                             │
└────────────────────────────────────────────────────────────────────┘
```

---

## Key Components

### Skill Layer
Every capability is a `SKILL.md` file containing:
- **YAML frontmatter** — name, description, category, dependencies, HITL gates
- **Behavioral contract** — the system prompt Claude receives when executing this skill

Two types:
- `core/` — control-plane (orchestration, memory, security, runtime infrastructure)
- `skills/` — domain skills (engineering, GTM, operations, governance)

### Orchestration Layer
Two planners translate natural-language objectives into ordered skill chains:
- `plan_workflow.py` — SDLC workflows (requirements through release)
- `plan_gtm_workflow.py` — GTM workflows (launch-planning through revenue-optimization)

Both emit a workflow plan JSON consumed by `execute_workflow.py`.

### Runtime Layer
`skill_activity.py` is the core execution unit:
1. Loads the skill's `SKILL.md` as a system prompt
2. Constructs a user message from objective + context packet
3. Calls Claude API with retry/backoff on transient errors
4. Detects HITL gate phrases in output
5. Returns `SkillActivityOutput`

Two execution modes:
- **Local** (`execute_workflow.py`) — sequential, in-process, no external deps
- **Temporal** (`temporal_worker.py`) — durable, retryable, supports HITL signals

### Memory Layer
All workflow state persists in Qdrant (vector database):
- `apotheon-observations` — step outputs, context snapshots, workflow events
- `apotheon-knowledge` — institutional knowledge, lessons learned, runbooks
- `apotheon-decisions` — decision records with full context

`context_manager.py` hydrates the context packet from prior observations on
workflow resumption, enabling continuity across HITL pauses and restarts.

### HITL Governance
Every action is classified by risk level (Low / L1 / L2 / L3). Level 3 gates block
execution until a human approves via:
- **Slack bot** (`hitl_handler.py`) — posts to `#apotheon-approvals`, polls reactions
- **CLI** — `apotheon approve <run-id>` sends a Temporal signal
- **Temporal UI** — manual signal injection at `http://localhost:8080`

### Connector Layer
`BaseConnector` provides rate limiting (token bucket), retry (exponential backoff),
and secret resolution (Vault → env var). Nine connectors implemented:
Salesforce, ServiceNow, GA4, Slack, Jira, HubSpot, Stripe, Mixpanel, Amplitude.

---

## Data Flow: Single Workflow Run

```
1. User: apotheon run "Build a payment service"
        |
2. plan_workflow.py
   └── Classifies objective → detects phases: backend, devsecops, qa, release
   └── route_skill_chain.py → topological order with dependency expansion
   └── Emits: workflow_plan.json
        |
3. execute_workflow.py / ApotheonWorkflow (Temporal)
   └── context_manager.load() → hydrate context from Qdrant
        |
4. For each step:
   |-- skill_activity.py
   |   |-- load SKILL.md (system prompt)
   |   |-- build user message (objective + context_packet + prior outputs)
   |   |-- call_claude() [with retry/backoff]
   |   └-- detect HITL gate in output
   |
   |-- if HITL: hitl_handler.py → Slack notification → await reaction
   |            → Temporal signal (hitl_approved / hitl_rejected)
   |
   |-- context_manager.save_step() → embed + upsert to Qdrant
   └-- context_packet.artifacts.append(skill_name)
        |
5. context_manager.finalize("completed")
6. execute_workflow.py emits execution_log.json
```

---

## Infrastructure Requirements

| Service | Purpose | Default Port | Start |
|---|---|---|---|
| Qdrant | Vector memory store | 6333 (HTTP) | `docker compose up -d qdrant` |
| Temporal | Durable workflow engine | 7233 (gRPC) | `docker compose up -d temporal` |
| Temporal UI | Workflow visualization | 8080 | `docker compose up -d temporal-ui` |
| Ollama | Local embedding model | 11434 | `docker compose up -d ollama` |

Start all: `docker compose up -d`

Check health: `apotheon validate && apotheon connector health`

---

## Further Reading

| Topic | Document |
|---|---|
| Local setup and deployment | `docs/onboarding/DEPLOYMENT.md` |
| Writing a new skill | `docs/onboarding/SKILL_AUTHORING_GUIDE.md` |
| GTM planner | `docs/onboarding/GTM_PLANNER_GUIDE.md` |
| Runtime component diagram | `docs/architecture/runtime-components.md` |
| Agent fleet | `docs/architecture/agent-fleet.md` |
| HITL gate audit | `docs/governance/hitl-gate-audit.md` |
| Memory engine | `docs/architecture/memory-engine.md` |
| Orchestration engine | `docs/architecture/orchestration-engine.md` |

## Quota-aware connector scheduling
Connectors now load per-connector rate-limit policy documents and expose quota pressure (`normal`/`elevated`/`critical`). Schedulers can switch execution to cached data under elevated pressure and force read-only degradation at critical pressure.
