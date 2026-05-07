# Apotheon AI Company OS

An AI-native Autonomous Company Operating System built as a Claude Code skill-pack.
Apotheon orchestrates the complete company lifecycle — from strategic planning and
product development through deployment, GTM, customer success, revenue optimization,
and continuous self-improvement — running primarily on local hardware with cloud as
optional overflow.

---

## What It Is

Apotheon is a **prompt/markdown-based framework**: SKILL.md files are behavioral
contracts that tell Claude how to operate each domain. There is no compiled application.
The intelligence is in the orchestration, the memory system, the knowledge graph, and
the 31 integrated skills that cover every function of a software company.

The platform is designed to run fully locally on a DGX Spark (128GB unified VRAM)
using Ollama, vLLM, Qwen, llama.cpp, and SGLang. Cloud models (Claude, GPT-4o) are
used for quality-critical tasks and as overflow when local capacity is saturated.

---

## The Autonomous OS Loop

```
PLAN --> BUILD --> SHIP --> GROW
  ^                           |
  +---------- LEARN ----------+
```

| Macro-Cycle | Skills | Cadence |
|---|---|---|
| PLAN | strategic-planning, product-analytics, revenue-operations, repo-intelligence | Weekly |
| BUILD | sdlc-orchestration, multi-agent, sandbox-execution, lora-lifecycle | Continuous |
| SHIP | cloud-deployment, mcp-integrations, compliance-automation, local-security | Per release |
| GROW | gtm-orchestration, content-marketing, ai-search-optimization, customer-success | Weekly |
| LEARN | model-evaluation, lora-lifecycle, synthetic-data, telemetry, knowledge-graph | Weekly |

---

## Repository Layout

```
core/                          Control-plane skills (orchestration, memory, security, runtime)
  autonomous-os/               Capstone: closed-loop OS orchestrator
  orchestration/               SDLC workflow routing and phase coordination
  gtm-orchestration/           GTM lifecycle coordination
  memory-token-management/     Persistent workflow state and token budgeting
  knowledge-graph/             11-entity organizational knowledge model
  retrieval-engine/            VectorRAG + GraphRAG + KV cache hybrid retrieval
  kv-cache-management/         5-zone KV cache optimization
  multi-agent/                 9-agent registry and collaboration patterns
  local-runtime/               Ollama/vLLM/llama.cpp/SGLang backend routing
  local-security/              5-level safety classification and approval gates
  telemetry/                   Agent observability, metrics, anomaly detection
  connector-hub/               Unified connector abstraction for all integrations
  mcp-integrations/            GitHub/Jira/Slack/Figma/Sentry/Datadog/Vercel/Cloudflare
  model-evaluation/            7-dimension benchmark and drift detection
  lora-lifecycle/              LoRA adapter training, promotion, rollback
  synthetic-data/              Synthetic datasets and simulation systems
  sandbox-execution/           Isolated code/browser/deployment execution
  runtime-economics/           Cost per workflow, local-vs-cloud routing economics
  tenant-management/           Multi-tenant workspace and data isolation
  hitl-dashboard/              Human-in-the-loop CLI, dashboard, explainability
  strategic-planning/          ROI scoring engine, backlog prioritization, roadmaps

skills/                        Domain skills covering the full company lifecycle
  -- Engineering --
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
  -- Intelligence --
  repo-intelligence/           Architecture inference, complexity heatmap, risk scoring
  -- GTM & Growth --
  ai-search-optimization/      llms.txt, semantic chunking, AI discoverability
  content-marketing/           Blog, newsletter, LinkedIn, X, Reddit, YouTube
  cloud-deployment/            Vercel/Cloudflare/AWS/GCP/K8s deployment automation
  -- Operations --
  customer-success/            Onboarding, health scoring, NPS, support triage
  product-analytics/           Funnels, event taxonomy, A/B experimentation
  revenue-operations/          Churn prediction, LTV/CAC, pricing strategy
  compliance-automation/       SOC2/GDPR/HIPAA/ISO27001/EU AI Act/NIST/PCI DSS
  -- Reporting --
  executive-reporting/         Executive summaries and board-level reporting
  compliance-governance/       Policy enforcement and governance reporting

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
  standards/                   6 standards: AI governance, architecture, markdown,
                               naming, prompt engineering, security baseline
  policies/                    4 policies: AI safety, architectural review,
                               data governance, secure development
  frameworks/                  AI discovery (llms.txt, semantic chunking, capability manifest)
  prompts/                     Reusable prompt templates
  templates/                   Document and output templates
  ontologies/                  Domain ontologies
  examples/                    Example workflows and outputs

scripts/                       Automation and validation tooling
  validation/                  validate_skill_structure.py, validate_frontmatter.py
  orchestration/               plan_workflow.py, autonomous_os_bootstrap.py
  generators/                  create_skill.py (scaffold new skills)
  memory/                      build_context_packet.py
  ai-discovery/                generate_llms_txt.py, validate_ai_discovery.py
  gtm/                         plan_gtm_workflow.py
  telemetry/                   record_telemetry_event.py
  security/                    scan_for_secrets.py
  analysis/                    Risk and codebase analysis utilities

docs/                          Human-facing documentation
tests/                         Validation and regression tests
```

---

## Quick Start

### Validate the skill pack

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
pytest
```

### Bootstrap the Autonomous OS

```bash
python scripts/orchestration/autonomous_os_bootstrap.py
```

Expected output when fully assembled:

```
APOTHEON AUTONOMOUS OS -- BOOTSTRAP REPORT
============================================================
Status:           [OK] OPERATIONAL
Skill coverage:   29/29 (100.0%)
Checks:           54 total  |  54 passed  |  0 failed  |  0 warnings

System is FULLY OPERATIONAL. All 31 phases present and validated.
```

### Scaffold a new skill

```bash
python scripts/generators/create_skill.py <skill-name>
```

### Route an objective to a skill plan

```bash
python scripts/orchestration/plan_workflow.py "<objective>"
```

### Build a context packet

```bash
python scripts/memory/build_context_packet.py
```

---

## Core Design Principles

1. **Progressive disclosure** — SKILL.md files stay concise (≤ 300 lines warn / 500 error for core; ≤ 150 / 300 for domain). Detail lives in `references/`, `templates/`, and `scripts/`.
2. **Local-first** — Everything runs on DGX Spark (128GB unified VRAM). Cloud models are overflow, not default.
3. **Memory integrity** — The memory packet never drops decisions, constraints, or FAIL gate records across a workflow's lifetime.
4. **Governed autonomy** — Every action has a safety level (0–4). Level 3+ actions queue for human approval. The OS never auto-executes production writes.
5. **Deterministic validation** — Machine-checkable quality gates at every phase transition. Scripts enforce invariants; humans review judgment calls.
6. **Knowledge graph as memory** — All decisions, artifacts, and relationships are written to the 11-entity organizational knowledge graph for long-term intelligence.
7. **Closed-loop self-improvement** — The OS measures its own output quality, detects model drift, retrains adapters, and optimizes routing — all within operator-approved boundaries.

---

## Platform Capabilities

| Capability | Implementation |
|---|---|
| Full SDLC orchestration | `core/orchestration` + 13 engineering skills |
| GTM lifecycle management | `core/gtm-orchestration` + content/SEO/deployment |
| Local model routing | `core/local-runtime` (Ollama/vLLM/llama.cpp/SGLang) |
| Multi-agent collaboration | 9 registered agents, 5 collaboration patterns |
| Persistent organizational memory | Knowledge graph + vector store + memory packets |
| AI-optimized retrieval | VectorRAG (Qdrant) + GraphRAG (Neo4j) + Redis hot cache |
| LoRA adapter lifecycle | Train → benchmark → promote → monitor → rollback |
| Synthetic data generation | 8 simulation types for evals and fine-tuning |
| Isolated code execution | 5 sandbox types with resource limits and network isolation |
| Multi-tenant isolation | Namespace-level isolation across memory, graph, connectors |
| Compliance automation | 7 frameworks: SOC2/GDPR/HIPAA/ISO27001/EU AI Act/NIST/PCI DSS |
| Revenue intelligence | Churn prediction, LTV/CAC, pricing elasticity modeling |
| Operator dashboard | CLI (`apotheon status/approve/explain`) + web dashboard spec |
| Cost optimization | Per-workflow economics, local-vs-cloud routing decisions |
| Self-improvement | Weekly autonomous improvement cycle with governed boundaries |

---

## Skill Validation Rules

All SKILL.md files must pass:

- Folder name: kebab-case
- SKILL.md opens with valid YAML frontmatter
- Required frontmatter fields: `name` (kebab-case), `description` (≤ 1024 chars, no `<>`), `metadata.version`, `metadata.category`, `metadata.owner`, `metadata.maturity`, `metadata.dependencies`
- Core skills: ≤ 300 lines (warning) / ≤ 500 lines (error)
- Domain skills: ≤ 150 lines (warning) / ≤ 300 lines (error)

CI runs on every push/PR: `validate_skill_structure.py` → `validate_frontmatter.py` → `pytest`.

---

## Branch and Commit Conventions

**Branches**: `main` / `develop` / `feature/*` / `hotfix/*` / `experimental/*`

**Commit scopes**: `feat` / `fix` / `refactor` / `docs` / `test` / `security` / `governance` / `orchestration` / `memory`
