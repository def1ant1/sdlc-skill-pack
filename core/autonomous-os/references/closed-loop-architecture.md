# Closed-Loop Architecture

Used by `core/autonomous-os/SKILL.md` to document the full integration graph,
data flows between all skills, and feedback loops that make the OS self-sustaining.

---

## Full Skill Integration Graph

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CONTROL PLANE                                    │
│  sdlc-orchestration ←→ gtm-orchestration ←→ autonomous-os          │
│         ↕                    ↕                    ↕                 │
│  memory-token-mgmt  ←→  knowledge-graph  ←→  retrieval-engine      │
│         ↕                    ↕                    ↕                 │
│  kv-cache-mgmt      ←→  multi-agent       ←→  local-security        │
└─────────────────────────────────────────────────────────────────────┘
         ↕                    ↕                    ↕
┌─────────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE PLANE                             │
│  local-runtime  ←→  runtime-economics  ←→  telemetry               │
│       ↕                   ↕                    ↕                   │
│  connector-hub  ←→  mcp-integrations   ←→  sandbox-execution       │
│       ↕                   ↕                    ↕                   │
│  cloud-deployment ←→ tenant-management ←→  hitl-dashboard          │
└─────────────────────────────────────────────────────────────────────┘
         ↕                    ↕                    ↕
┌─────────────────────────────────────────────────────────────────────┐
│                    ENGINEERING PLANE                                │
│  requirements ←→ architecture ←→ ai-engineering ←→ backend         │
│       ↕              ↕               ↕                ↕            │
│  frontend ←→ code-review ←→ qa ←→ devsecops ←→ release            │
│       ↕              ↕               ↕                ↕            │
│  observability ←→ sre ←→ compliance ←→ executive-reporting         │
│                                       ↕                            │
│            repo-intelligence ←→ model-evaluation                   │
└─────────────────────────────────────────────────────────────────────┘
         ↕                    ↕                    ↕
┌─────────────────────────────────────────────────────────────────────┐
│                    GTM + GROWTH PLANE                               │
│  content-marketing ←→ ai-search-optimization ←→ gtm-orchestration  │
│          ↕                    ↕                         ↕           │
│  customer-success ←→ product-analytics ←→ revenue-operations        │
│          ↕                    ↕                         ↕           │
│  strategic-planning ←→ compliance-automation ←→ lora-lifecycle     │
│          ↕                                              ↕           │
│  synthetic-data ←────────────────────────────────── model-eval     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Primary Data Flows

### Engineering → GTM (CX-006)

```
sdlc-orchestration produces:
  release notes → gtm-orchestration (launch plan)
  API changelog → ai-search-optimization (llms.txt update)
  security report → compliance-automation (evidence)
  test results → model-evaluation (quality baseline)
```

### Operations → Intelligence

```
telemetry produces:
  workflow metrics → runtime-economics (cost analysis)
  anomaly alerts → multi-agent (incident response)
  usage events → product-analytics (funnel data)
  model quality scores → model-evaluation (drift detection)
```

### Intelligence → Planning

```
product-analytics produces:
  retention curves → strategic-planning (roadmap scoring)
  feature adoption → customer-success (health scores)
  experiment results → revenue-operations (pricing model)
  funnel data → gtm-orchestration (channel optimization)

revenue-operations produces:
  churn predictions → customer-success (intervention trigger)
  LTV:CAC by segment → strategic-planning (investment scoring)
  expansion signals → gtm-orchestration (upsell campaign)
```

### Learning → Execution

```
model-evaluation produces:
  drift alerts → lora-lifecycle (retrain trigger)
  benchmark scores → local-runtime (routing update)
  quality reports → strategic-planning (model investment)

lora-lifecycle produces:
  new adapter → local-runtime (routing table update)
  training data request → synthetic-data (dataset generation)
  adapter registry → retrieval-engine (capability index)
```

### Knowledge Graph as Central Memory

All skills read from and write to the knowledge graph:
```
Entity writes:
  sdlc-orchestration    → Workflow, Feature
  multi-agent           → Agent, Decision
  cloud-deployment      → Deployment, API
  customer-success      → Customer
  product-analytics     → Campaign, RevenueEvent
  repo-intelligence     → Product, Feature, API
  compliance-automation → Workflow (compliance evidence)

Relationship writes:
  gtm-orchestration     → Campaign TARGETS Customer
  revenue-operations    → Customer GENERATES RevenueEvent
  lora-lifecycle        → Agent USES Deployment (model serving)
  strategic-planning    → Feature HAS_RISK (tech debt)
```

---

## Feedback Loops

### Loop 1: Product Quality Loop (Weekly)

```
repo-intelligence → identifies complexity/churn hotspots
→ strategic-planning scores tech debt items
→ sdlc-orchestration routes refactor work
→ repo-intelligence confirms improvement on next scan
```

### Loop 2: Model Quality Loop (Weekly)

```
telemetry → captures model output quality events
→ model-evaluation detects drift
→ lora-lifecycle triggers retraining
→ synthetic-data generates fresh training examples
→ lora-lifecycle promotes new adapter
→ local-runtime updates routing
→ telemetry confirms quality improvement
```

### Loop 3: Revenue Retention Loop (Weekly)

```
product-analytics → computes D7/D30 retention by cohort
→ customer-success identifies at-risk accounts
→ gtm-orchestration triggers retention campaigns
→ revenue-operations measures NRR impact
→ strategic-planning adjusts roadmap toward retention features
```

### Loop 4: Cost Optimization Loop (Weekly)

```
telemetry → records token counts and model routes per workflow
→ runtime-economics computes cost per workflow by type
→ runtime-economics identifies tasks running on cloud unnecessarily
→ local-runtime routing table updated (shift to local)
→ runtime-economics confirms cost reduction next cycle
```

### Loop 5: GTM → Product Signal Loop (Ongoing)

```
content-marketing → publishes blog/social content
→ ai-search-optimization monitors AI citation rates
→ product-analytics tracks traffic from AI referrals
→ customer-success tracks activation from AI-sourced signups
→ strategic-planning scores AI discoverability as investment priority
→ ai-search-optimization gets allocated improvement work
```

### Loop 6: Compliance Posture Loop (Monthly)

```
compliance-automation → runs evidence gap scan
→ repo-intelligence → scans code for new control implementations
→ compliance-automation → updates control inventory
→ local-security → updates safety classification rules if new risks found
→ compliance-automation → produces audit readiness score
→ strategic-planning → prioritizes compliance gaps by certification impact
```

---

## Skill Dependency Ordering

Skills must load and be healthy in this order for full OS operation:

**Tier 0 — Must be first:**
```
sdlc-memory-token-management
local-security
telemetry
```

**Tier 1 — Core infrastructure:**
```
local-runtime
connector-hub
kv-cache-management
knowledge-graph
retrieval-engine
```

**Tier 2 — Orchestration:**
```
sdlc-orchestration
gtm-orchestration
multi-agent
tenant-management
hitl-dashboard
```

**Tier 3 — Execution skills:**
```
sandbox-execution
cloud-deployment
mcp-integrations
runtime-economics
model-evaluation
```

**Tier 4 — Domain skills:**
```
All skills/* and remaining core/*
```

**Tier 5 — Capstone:**
```
autonomous-os
```

If any Tier 0–2 skill fails health check: OS halts and alerts operator.
If Tier 3–4 skill fails: OS continues with reduced capability; degraded mode logged.

---

## Memory Packet Flow Across Cycles

The memory packet is the single carrier of cross-cycle state. Its `phase_status`
field tracks all 12 SDLC phases plus the 5 GTM phases simultaneously for each
active workflow. The autonomous OS never drops:

- `decisions.accepted` — permanent record of all approved choices
- `decisions.rejected` — permanent record of what was considered and declined
- `constraints` — limits that apply to all future decisions
- `quality_gate_status` with any `FAIL` records — never overwritten
- `risks` — accumulated risk register for the full workflow lifecycle

Between cycles, the OS compresses conversation context but preserves the full memory
packet in the knowledge graph as a durable artifact.