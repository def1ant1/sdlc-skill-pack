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
135+ integrated skills spanning every function of a software company — engineering,
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
| GROW | gtm-orchestration, content-marketing, ai-search-optimization, customer-success, forecasting | Weekly |
| LEARN | model-evaluation, lora-lifecycle, synthetic-data, telemetry, skill-gap-engine, evolution-engine, benchmark-factory | Weekly |
| OPERATE | business-orchestration, accounting-automation, budget-planning, legal-ops, workforce-management, vendor-procurement | Continuous |
| PROTECT | alignment-engine, privacy-runtime, deception-detection, adversarial-evaluation, policy-simulation | Continuous |
| REASON | cognitive-runtime, predictive-reasoning, simulation-engine, research-runtime, causal-analysis | On-demand |

---

## Repository Layout

```
core/                          Control-plane skills (orchestration, memory, security, runtime)
  autonomous-os/               Capstone: closed-loop OS orchestrator
  orchestration/               SDLC workflow routing and phase coordination
  gtm-orchestration/           GTM lifecycle coordination
  workflow-engine/             DAG execution backbone for all cross-skill automation
  workflow-runtime/            Durable execution: checkpointing, state recovery, deterministic replay
  skill-gap-engine/            Self-auditing skill registry scanner and gap detector
  evolution-engine/            Autonomous self-improvement: gap→proposal→approval→execution
  cognitive-runtime/           Goal decomposition, hierarchical planning, adaptive replanning
  agent-kernel/                Multi-agent process isolation, resource quotas, lifecycle management
  agent-identity/              Persistent agent expertise, episodic/semantic memory, reputation
  distributed-agent-runtime/   Multi-node agent coordination with load balancing and fault tolerance
  event-bus/                   Async event routing, event sourcing, at-least-once delivery
  alignment-engine/            Constitutional compliance scoring, deception detection, safety enforcement
  semantic-layer/              Enterprise ontology, entity resolution, temporal graph reasoning
  data-fabric/                 Schema governance, data lineage, data contract enforcement
  master-data-management/      Golden records, deduplication, survivorship rules
  research-runtime/            Autonomous R&D: hypothesis → experiment → synthesis
  simulation-engine/           Digital twin for business, infrastructure, and security simulation
  explainability/              Causal traces, execution lineage, governance-grade explanations
  predictive-reasoning/        Probabilistic enterprise outcome forecasting
  benchmark-factory/           Benchmark lifecycle: create, curate, version, evaluate
  model-lifecycle/             Model promotion gates, canary deployment, quality monitoring
  model-routing/               Adaptive local/cloud routing with complexity estimation
  economic-coordination/       Priority scheduling, quota enforcement, compute arbitration
  cluster-management/          GPU cluster optimization, topology-aware model placement
  federated-runtime/           Air-gapped, edge, and federated deployment with residency enforcement
  privacy-runtime/             PII detection/redaction, retention enforcement, legal holds
  business-orchestration/      Routes non-SDLC business tasks across domains
  meeting-intelligence/        Meeting transcripts → decisions → action items → knowledge graph
  enterprise-search/           Hybrid vector+BM25 search across all organizational content
  governance/                  Policy registry, approval authority matrix, AI governance
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
  developer-experience/        DX metrics, SPACE framework, onboarding optimization
  -- Cognitive Runtime (Phase 54) --
  hierarchical-planning/       HTN-based goal decomposition and execution planning
  meta-reasoning/              Reasoning chain quality evaluation and bias detection
  goal-decomposition/          Atomic sub-goal generation with measurable success criteria
  self-reflection/             Output quality review and systematic improvement recommendations
  constraint-reasoning/        Hard/soft constraint evaluation and alternative plan generation
  causal-analysis/             Causal inference (DiD, IV, RCT) for enterprise decisions
  long-horizon-planning/       Rolling-horizon multi-week to multi-year planning
  -- Durable Execution (Phase 53) --
  checkpoint-management/       Workflow state serialization and durable storage
  runtime-recovery/            Failure classification and checkpoint-based recovery
  workflow-replay/             Deterministic workflow replay for audit and debugging
  state-restoration/           Checkpoint deserialization and context reconstruction
  -- AI Safety & Alignment (Phase 58) --
  alignment-testing/           Pre-deployment behavioral test suites and alignment scorecards
  harm-classification/         Multi-taxonomy harm scoring and mitigation routing
  deception-detection/         Hallucination, authority escalation, and manipulation detection
  adversarial-evaluation/      Structured red team evaluation and agent hardening
  policy-simulation/           Policy change impact simulation before enforcement
  -- Infrastructure Intelligence (Phase 59) --
  gpu-cluster-optimization/    Topology-aware model placement and VRAM defragmentation
  inference-batching-optimization/ Dynamic batch sizing and window tuning
  network-topology-analysis/   NVLink/PCIe topology mapping and bottleneck detection
  model-placement-optimization/ Optimal model shard placement scoring and execution
  cache-placement-optimization/ KV cache sizing, prefix warmup, and eviction tuning
  -- Intelligence --
  repo-intelligence/           Architecture inference, complexity heatmap, risk scoring
  decision-intelligence/       Multi-criteria decision scoring and ADR authoring
  forecasting/                 Revenue and operational forecasting (Holt-Winters, Prophet)
  -- Explainability (Phase 61) --
  causal-tracing/              Evidence-weighted root cause attribution from event streams
  execution-explanation/       Layered natural-language workflow explanations by audience
  policy-justification/        Evidence-backed policy enforcement justifications
  reasoning-visualization/     Goal trees and reasoning chains in Mermaid/DOT format
  -- Data Fabric & Governance (Phase 62-63) --
  schema-evolution/            Breaking change detection and migration coordination
  data-contract-management/    Contract authoring, compliance monitoring, violation enforcement
  lineage-analysis/            Upstream provenance and downstream impact traversal
  dataset-curation/            Quality filtering, deduplication, and annotation consistency
  -- Autonomous Research (Phase 64) --
  literature-review/           Systematic search, synthesis, and gap identification
  research-analysis/           Statistical analysis, hypothesis testing, evidence grading
  hypothesis-generation/       Abductive reasoning for testable hypothesis generation
  patent-analysis/             FTO assessment, IP landscape, white space identification
  discovery-synthesis/         Cross-stream research synthesis with convergence scoring
  -- Simulation & Digital Twin (Phase 65) --
  business-simulation/         Monte Carlo scenario analysis for strategic decisions
  incident-simulation/         Game day exercises for SRE and security preparedness
  security-war-gaming/         ATT&CK-based adversarial exercises and defensive gap analysis
  runtime-simulation/          AI infrastructure simulation for pre-deployment validation
  -- Benchmarking Platform (Phase 66) --
  benchmark-generation/        Calibrated benchmark generation with adversarial cases
  evaluation-dataset-curation/ Rigorous curation: correctness, deduplication, balance
  synthetic-dataset-generation/ Controlled synthetic training/eval data generation
  scenario-generation/         Diverse scenario synthesis for simulation and evaluation
  -- Model Lifecycle (Phase 67-68) --
  model-benchmarking/          Standardized capability evaluation with trend tracking
  model-distillation/          Teacher-to-student knowledge transfer for local inference
  quantization-optimization/   INT4/INT8/GPTQ/AWQ quantization with quality validation
  lora-management/             LoRA adapter registration, hot-swap, routing, and retirement
  model-selection-optimization/ Multi-criteria task-to-model matching
  uncertainty-aware-routing/   Confidence-based inference escalation
  reasoning-depth-estimation/  Task complexity estimation for tier selection
  -- GTM & Growth --
  ai-search-optimization/      llms.txt, semantic chunking, AI discoverability
  content-marketing/           Blog, newsletter, LinkedIn, X, Reddit, YouTube
  cloud-deployment/            Vercel/Cloudflare/AWS/GCP/K8s deployment automation
  -- Operations --
  customer-success/            Onboarding, health scoring, NPS, support triage
  product-analytics/           Funnels, event taxonomy, A/B experimentation
  revenue-operations/          Churn prediction, LTV/CAC, pricing strategy
  compliance-automation/       SOC2/GDPR/HIPAA/ISO27001/EU AI Act/NIST/PCI DSS
  -- Business Operations --
  accounting-automation/       Transaction processing, anomaly detection, approval routing
  budget-planning/             Annual/quarterly budget cycles, variance analysis
  legal-ops/                   Contract lifecycle, NDA routing, risk flagging
  workforce-management/        Employee records, org changes, compensation approvals
  vendor-procurement/          Vendor qualification, spend authority, contract management
  -- Portfolio Governance & PMO (Phase 71) --
  portfolio-optimization/      Multi-criteria initiative scoring and resource allocation
  program-governance/          Milestone tracking, risk escalation, executive reporting
  initiative-prioritization/   Weighted multi-criteria initiative ranking
  capacity-balancing/          Resource capacity analysis and overcommitment detection
  -- Enterprise Data Privacy (Phase 72) --
  pii-detection/               Multi-layer PII detection: regex, NER, contextual classification
  data-redaction/              Jurisdiction-aware redaction, pseudonymization, tokenization
  legal-hold-management/       Legal hold lifecycle from placement through release
  residency-analysis/          Cross-boundary data flow analysis and compliant routing
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
  skills/                      scan_skills.py, detect_skill_gaps.py,
                               generate_skill_improvement_plan.py, scaffold_missing_skill.py
  business/                    route_business_task.py
  search/                      index_domain_content.py, hybrid_enterprise_search.py
  finance/                     detect_finance_anomalies.py

docs/                          Human-facing documentation
  schemas/                     JSON Schema definitions
    meetings/                  meeting.yaml, action-item.yaml, meeting-decision.yaml
    finance/                   transaction.yaml, invoice.yaml, budget.yaml
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

### Detect skill gaps

```bash
# Scan all skills and emit a registry JSON
python scripts/skills/scan_skills.py --root . --output skill-registry.json

# Detect quality and coverage gaps
python scripts/skills/detect_skill_gaps.py --root . --output gaps.json

# Generate a prioritized improvement plan
python scripts/skills/generate_skill_improvement_plan.py --input gaps.json

# Scaffold a missing skill
python scripts/skills/scaffold_missing_skill.py <skill-name>
```

### Route a business task

```bash
python scripts/business/route_business_task.py "onboard new vendor Acme Corp"
```

### Search organizational content

```bash
# Build the search index
python scripts/search/index_domain_content.py --root . --output search-index.json

# Run a hybrid search query
python scripts/search/hybrid_enterprise_search.py \
  --query "incident response playbook" \
  --index search-index.json \
  --top 5
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
8. **Full business coverage** — Every company function has a skill: finance, legal, HR, procurement, forecasting, and decision-making are first-class OS citizens alongside engineering.

---

## Platform Capabilities

| Capability | Implementation |
|---|---|
| Full SDLC orchestration | `core/orchestration` + 12 engineering skills |
| GTM lifecycle management | `core/gtm-orchestration` + content/SEO/deployment |
| Durable workflow execution | `core/workflow-runtime` + checkpoint/recovery/replay skills |
| Cognitive runtime | `core/cognitive-runtime` + hierarchical planning + meta-reasoning |
| Autonomous self-improvement | `core/evolution-engine` → gap → proposal → operator approval → execution |
| Distributed agent OS | `core/agent-kernel` + `core/distributed-agent-runtime` + lifecycle management |
| AI safety runtime | `core/alignment-engine` + constitutional rules + deception detection + red team |
| Cross-domain workflow automation | `core/workflow-engine` + DAG DSL + 8 built-in templates |
| Business operations | `core/business-orchestration` + 5 domain skills (accounting, budget, legal, HR, procurement) |
| Meeting intelligence | `core/meeting-intelligence` → decisions + action items → knowledge graph |
| Enterprise search | `core/enterprise-search` (vector + BM25 hybrid, 7 indexes) |
| Enterprise semantic layer | `core/semantic-layer` + ontology reasoning + entity resolution |
| Master data management | `core/master-data-management` + golden records + survivorship rules |
| Data fabric | `core/data-fabric` + lineage tracking + schema governance + data contracts |
| Predictive enterprise intelligence | `core/predictive-reasoning` + incident/churn/infrastructure forecasting |
| Simulation and digital twin | `core/simulation-engine` + business/incident/security/runtime simulation |
| Autonomous research | `core/research-runtime` + literature review + hypothesis generation + synthesis |
| Explainability and causality | `core/explainability` + causal tracing + policy justification |
| Model lifecycle governance | `core/model-lifecycle` + promotion gates + canary + quality monitoring |
| Adaptive model routing | `core/model-routing` + complexity estimation + uncertainty-aware escalation |
| GPU cluster optimization | `core/cluster-management` + topology analysis + VRAM optimization |
| Sovereign AI runtime | `core/federated-runtime` + air-gapped + edge + residency enforcement |
| Enterprise privacy | `core/privacy-runtime` + PII detection/redaction + legal holds + residency |
| Portfolio governance | PMO skills + portfolio optimization + capacity balancing |
| Governance and policy | `core/governance` (policy registry, approval authority matrix, AI governance) |
| Skill quality assurance | `core/skill-gap-engine` (6-dimension rubric, gap detection, improvement plans) |
| Local model routing | `core/local-runtime` (Ollama/vLLM/llama.cpp/SGLang) |
| Multi-agent collaboration | 9 registered agents, 5 collaboration patterns |
| Persistent organizational memory | Knowledge graph + vector store + memory packets |
| AI-optimized retrieval | VectorRAG (Qdrant) + GraphRAG (Neo4j) + Redis hot cache |
| LoRA adapter lifecycle | Train → benchmark → promote → monitor → rollback |
| Synthetic data generation | 8 simulation types for evals and fine-tuning |
| Isolated code execution | 5 sandbox types with resource limits and network isolation |
| Multi-tenant isolation | Namespace-level isolation across memory, graph, connectors |
| Compliance automation | 7 frameworks: SOC2/GDPR/HIPAA/ISO27001/EU AI Act/NIST/PCI DSS |
| Revenue intelligence | Churn prediction, LTV/CAC, pricing elasticity, multi-model forecasting |
| Financial anomaly detection | Duplicate invoices, velocity spikes, new vendor thresholds |
| Decision intelligence | Multi-criteria scoring, bias detection, decision records |
| Compute resource arbitration | `core/economic-coordination` + priority scheduling + quota enforcement |
| Operator dashboard | CLI (`apotheon status/approve/explain`) + web dashboard spec |
| Cost optimization | Per-workflow economics, local-vs-cloud routing decisions |

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