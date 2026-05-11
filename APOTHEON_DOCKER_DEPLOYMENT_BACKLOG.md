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
- Close competitor gaps against Paperclip-style control planes, OpenClaw-style skill ecosystems, OpenCognit-style execution hierarchies, and Greentic-style governance/determinism. fileciteturn50file0
- Incorporate ecosystem lessons from agent skill standards, LangGraph/CrewAI/AutoGen orchestration, Mem0/Letta/Graphiti memory, Langfuse/Phoenix/AgentOps telemetry, OPA/Guardrails governance, n8n/Temporal/Airflow automation, and domain-cognition skill patterns. fileciteturn52file0

Source planning inputs: user-provided implementation critique, competitor comparison feedback, and AI OS ecosystem architecture feedback. fileciteturn46file0 fileciteturn50file0 fileciteturn52file0

---

## 0.1 Competitor-Informed Gap Response

The attached competitor analysis identifies the largest market gaps as execution depth, UI/control plane, skill compiler maturity, out-of-the-box deployment, reference company templates, observability, community, deterministic governance, connectors, self-improvement loops, modular packaging, onboarding, hardware accessibility, and commercial clarity. fileciteturn50file0

### Strategic response

Apotheon should position itself as:

```text
deep enterprise skill OS
+ governed execution runtime
+ skill-to-code compiler
+ local-first Docker deployment
+ company templates
+ deterministic control plane
```

rather than competing only as a generic chat assistant or personal productivity agent.

### Required differentiators

```text
1. Executable enterprise workflows, not only SKILL.md specs.
2. Skill compiler that converts SKILL.md contracts into runnable activities, schemas, tests, policies, and docs.
3. Company templates that can be imported and run.
4. Stronger governance/determinism than UI-first competitors.
5. Broader business-domain skill coverage than personal-agent ecosystems.
6. Docker-first local solo deployment that works on consumer hardware.
7. Public skill contribution and registry workflow.
```

---

## 0.2 AI-Native Operating System Architecture Direction

The ecosystem feedback reframes Apotheon’s opportunity as evolving from a skills repository into a full AI-native operational platform with a skill marketplace, orchestration runtime, memory system, governance layer, self-improving agent ecosystem, and enterprise operating system. fileciteturn52file0

### Long-term platform equation

```text
AI Runtime Layer
+ Skill Graph
+ Governance Kernel
+ Enterprise Memory
+ Workflow Orchestration
+ Telemetry
+ Knowledge Graph
+ Autonomous Agents
+ Marketplace
= AI-native enterprise operating system
```

### Design principle

Do not optimize only for prompts, workflows, or agents. Optimize for:

```text
organizational intelligence accumulation
```

Apotheon should become the persistent operational brain of a company: a reusable enterprise cognition layer that remembers decisions, learns from executions, improves skill routing, and composes business capabilities over time. fileciteturn52file0

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
skill metadata schema
skill graph engine
memory/context manager
governance/HITL
telemetry/events
SDLC feature workflow
GTM launch workflow
basic finance/accounting workflow
customer lifecycle workflow
OldFarmTrucks.com demo workflow
observability/reporting
Docker deployment
chat UI MVP
dashboard MVP
skill pipeline compiler MVP
company template MVP
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
- Users can run at least one company template end-to-end in dry-run mode.

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
    ├── apotheon-control-plane
    ├── skill-registry-api optional
    ├── qdrant
    ├── temporal
    ├── temporal-ui
    ├── postgres
    ├── redis
    ├── minio optional
    ├── grafana optional
    ├── prometheus optional
    ├── loki optional
    ├── otel-collector optional
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

### apotheon-dashboard / control plane

Purpose: browser control plane for workflows, schedules, approvals, budgets, agents, company goals, connector health, local apps, knowledge, and runtime status.

MVP implementation:

```text
Streamlit dashboard + generated dashboard_state.json
```

Post-MVP implementation:

```text
React/Vue control plane backed by FastAPI
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
mvp
core
runtime
scheduler
reports
api
ui
dashboard
control-plane
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
APOTHEON_SKILL_REGISTRY_MODE=local
APOTHEON_ENABLE_PUBLIC_REGISTRY=false
```

Rules:

- `.env` must never be committed.
- `.env.example` must contain no secrets.
- Write actions are disabled by default.
- Scheduler defaults to dry-run.
- Connectors default to read-only.
- Public registry features are disabled by default.

---

## 9. Formal Skill Specification and Progressive Loading

Create or harden:

```text
schemas/skill.yaml.schema.json
schemas/skill-metadata.schema.json
references/skill-specification-standard.md
scripts/validation/validate_skill_yaml.py
```

Every skill should include:

```yaml
id:
name:
description:
capabilities:
required_tools:
dependencies:
risk_level:
token_budget:
evaluation_metrics:
memory_requirements:
governance_policies:
```

Progressive context loading must support:

```text
metadata preload
lazy-loaded references
dependency-aware retrieval
deep context only when required
```

Acceptance criteria:

- Every MVP skill has `skill.yaml` or equivalent manifest.
- Skill metadata can be loaded without loading full references.
- Skill dependency graph can be generated from metadata.
- Token budgets are enforceable at runtime.

---

## 10. Skill Graph Engine

Create:

```text
core/skill-graph-engine/
scripts/skills/build_skill_graph.py
scripts/skills/resolve_skill_dependencies.py
reports/skill_graph.md
reports/skill_graph.json
reports/skill_graph.mmd
```

Capabilities:

```text
dependency graph construction
capability composition
skill routing support
cycle detection
version lock resolution
primitive-to-composite workflow planning
```

Acceptance criteria:

- Graph includes skills, tools, policies, memory requirements, and connectors.
- Graph detects missing dependencies and routing collisions.
- Planner can query graph for candidate skills.

---

## 11. Enterprise Orchestration Engine

Architecture must separate:

| Role | Responsibility |
|---|---|
| Planner | Decompose goals |
| Skill Router | Select skills |
| Executor | Execute steps |
| Evaluator | Score outputs |
| Governor | Enforce policy |

Create or harden:

```text
core/planner/
core/skill-router/
core/executor/
core/evaluator/
core/governor/
schemas/workflow-graph.schema.json
scripts/orchestration/execute_graph.py
```

Requirements:

```text
graph-based execution
branching
retries
state
approvals
memory hydration
evaluators
policy enforcement
checkpoint/resume
```

Acceptance criteria:

- Workflows can run as graphs, not only linear step lists.
- Each role emits telemetry.
- Governor can block unsafe branches.
- Evaluator can request revision or fallback.

---

## 12. Executable Runtime Depth

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

## 13. Multi-Layer Memory and Knowledge Graph

Create or harden:

```text
core/memory-system/
core/knowledge-graph/
core/organizational-memory/
core/procedural-memory/
schemas/memory-event.schema.json
scripts/memory/record_execution_memory.py
scripts/memory/retrieve_context.py
scripts/memory/detect_contradictions.py
```

Memory layers:

| Layer | Purpose |
|---|---|
| Working Memory | Active context |
| Episodic Memory | Past executions |
| Semantic Memory | Learned facts |
| Procedural Memory | Skill improvements |
| Organizational Memory | Enterprise knowledge |

Required execution feedback:

```json
{
  "success_rate": 0.92,
  "token_cost": 1844,
  "hallucination_risk": 0.03,
  "human_revision_cycles": 1
}
```

Acceptance criteria:

- Workflow executions update episodic memory.
- Stable facts can be promoted to semantic memory.
- Skill improvements are recorded in procedural memory.
- Contradictions are flagged before use.
- Knowledge graph links customers, invoices, products, vendors, decisions, risks, and workflows.

---

## 14. AI Telemetry and Evaluation Platform

Create or harden:

```text
core/ai-telemetry/
core/evaluation-engine/
core/replay-debugger/
schemas/ai-telemetry-event.schema.json
scripts/reports/generate_ai_telemetry_report.py
scripts/evals/run_skill_benchmarks.py
```

Track:

```text
latency
token cost
failure rate
retries
hallucination risk
human interventions
model drift
skill utilization
workflow degradation
model comparison
```

Replay and debugging should trace:

```text
User Request -> Planner -> Router -> Memory -> Tool -> Evaluator -> Governor -> Output
```

Acceptance criteria:

- Every workflow has traceable AI telemetry.
- Replay report can explain why a workflow failed.
- Benchmarks run for MVP skills.
- Regression tests flag degraded skill performance.

---

## 15. Policy Governance Kernel and Sandboxing

Create or harden:

```text
core/policy-engine/
core/governance-kernel/
core/sandbox-execution/
core/business-approval-gateway/
schemas/skill-permission.schema.json
scripts/governance/enforce_runtime_policy.py
scripts/governance/generate_evidence_pack.py
```

Every skill should declare:

```yaml
allowed_data:
restricted_actions:
compliance_requirements:
human_approval_required:
```

Constitutional skill governance principles:

```yaml
principles:
  - never expose PII
  - require approval for financial actions
  - log all external communications
  - never mutate production systems without approval
```

Acceptance criteria:

- Skill permissions are enforced at runtime.
- Sandboxed execution is available for high-risk skills.
- External actions require explicit approval.
- Evidence packs are generated for regulated workflows.

---

## 16. Event-Driven Automation Backbone

Create:

```text
core/event-bus/
core/trigger-engine/
schemas/automation-trigger.schema.json
scripts/automation/register_trigger.py
scripts/automation/run_event_trigger.py
```

Supported triggers:

```yaml
trigger:
  - new_email
  - crm_update
  - inventory_change
  - schedule_due
  - connector_event
  - file_added
  - support_ticket_created
  - budget_threshold_hit
  - policy_violation
```

Acceptance criteria:

- Triggers can launch workflows in dry-run.
- Event-triggered workflows pass through governor.
- Trigger history is visible in dashboard.

---

## 17. Domain Cognition Modules

Upgrade important skills from simple prompt files to encapsulated domain cognition modules.

Each domain cognition skill should include:

```text
principles
heuristics
frameworks
evaluators
anti-pattern detection
examples
policy boundaries
memory hooks
```

Priority domains:

```text
sales
finance/accounting
legal/tax
security
HR
knowledge/research
GTM
SDLC
operations
```

Acceptance criteria:

- Priority MVP skills include evaluators and anti-pattern detectors.
- Domain frameworks are referenced in outputs where appropriate.
- Skills can self-check against domain-specific quality rubrics.

---

## 18. Skill Pipeline Compiler

Highest-leverage productization feature.

Create:

```text
scripts/skill_pipeline.py
core/skill-compiler/
schemas/compiled-skill.schema.json
references/skill-pipeline-standard.md
reports/skill_pipeline_report.md
reports/skill_pipeline_report.json
```

Inputs:

```text
SKILL.md
skill.yaml
manifest.yaml
contracts/*.yaml
workflows/*.yaml
templates/*.md
references/*.md
evals/*.yaml
```

Generated outputs:

```text
compiled skill descriptor
Temporal activity stub
Python activity scaffold
JSON schema bindings
pytest test scaffold
eval scaffold
governance wrapper
telemetry event definitions
rate-limit policy stub
cost policy stub
documentation page
marketplace package metadata
```

Acceptance criteria:

- `python scripts/skill_pipeline.py compile skills/example-skill` generates runnable scaffolds.
- Generated scaffolds pass lint/tests.
- Compiler fails clearly on missing contracts.
- Compiler can batch compile MVP skills.
- Skill compiler output is deterministic.

---

## 19. Reference Workflow Implementations

Create executable demos under:

```text
workflows/examples/
reports/reference_workflows/
tests/reference_workflows/
company_templates/
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

## 20. Company Templates

Create importable company templates similar to competitor company-template/control-plane strengths. fileciteturn50file0

Create:

```text
company_templates/oldfarmtrucks/
company_templates/sdlc-agency/
company_templates/solo-consultant/
company_templates/local-service-business/
company_templates/ecommerce-operator/
scripts/company_templates/import_template.py
schemas/company-template.schema.json
```

Each template includes:

```text
business profile
roles/agent map
goals/OKRs
budgets
enabled skills
workflows
schedules
connectors
approval policies
dashboards
sample data
```

Acceptance criteria:

- User can import OldFarmTrucks template locally.
- Imported template creates workflows, schedules, dashboards, and sample fixtures.
- Template import runs in dry-run mode by default.

---

## 21. Skill Maturity and Certification

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

## 22. Hybrid Skill Execution

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

## 23. Chat UI Backlog

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
import company template
```

Acceptance criteria:

- User can type: Launch OldFarmTrucks.com as a classic truck dealership.
- UI returns a workflow plan.
- User can run dry-run.
- UI shows generated reports and run status.
- UI blocks live writes by default.
- UI displays approval requirements before execution.
- UI can import the OldFarmTrucks company template.

---

## 24. Dashboard / Control Plane Backlog

Single-user business operation needs a visible control plane, not only CLI output.

Dashboards:

```text
workflow runs
scheduled tasks
approvals
goals/OKRs
budgets
agent/team roles
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
memory and knowledge graph status
self-improvement proposals
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

Post-MVP:

```text
apps/control-plane-api/
apps/control-plane-ui/
```

Acceptance criteria:

- User can see workflow progress.
- User can see scheduled work.
- User can approve/reject HITL items.
- User can see budgets and rate limits.
- User can see company template goals and status.
- User can inspect memory and knowledge graph status.

---

## 25. Reliability, Error Handling, and Observability

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
workflow history visualization
anomaly detection hooks
```

Acceptance criteria:

- Every workflow run has correlation ID.
- Errors are structured and actionable.
- Circuit breakers prevent repeated failing connector calls.
- Temporal workflows support replay/checkpointing for macro-cycle orchestrations.
- UI/control plane surfaces workflow history and failures.

---

## 26. Token, Context, Cache, and Retrieval Optimization

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

## 27. Governance Enforcement and Determinism

Implement enforceable runtime guards, not just docs.

Create or harden:

```text
core/policy-engine/
core/business-approval-gateway/
scripts/governance/validate_policy_links.py
scripts/governance/validate_hitl_for_actions.py
scripts/governance/enforce_runtime_policy.py
scripts/governance/generate_evidence_pack.py
```

Required:

- Financial controls.
- External action policy.
- HR high-impact policy.
- Trading/tax/legal boundaries.
- Security mutation boundaries.
- Customer communication approvals.
- Deterministic fallbacks for high-risk paths.
- Compliance evidence packs.

Acceptance criteria:

- High-risk actions fail closed without approval.
- Policy decisions are logged.
- Approval queue appears in UI/dashboard.
- Evidence packs can be generated for regulated workflows.

---

## 28. Rate Limit and Quota Management

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

## 29. Budget and Cost Tracking

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

## 30. Modular Packaging Profiles and Feature Flags

Create profiles:

```text
profiles/local-solo.yaml
profiles/team.yaml
profiles/enterprise.yaml
profiles/mvp.yaml
profiles/full-domain-lab.yaml
```

Create feature flags:

```text
core/feature-flags/
schemas/feature-flag.schema.json
scripts/validation/validate_feature_flags.py
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
UI modules
```

Acceptance criteria:

- `local-solo` runs on consumer hardware.
- `mvp` includes only release-critical skills.
- `enterprise` enables advanced governance/connectors.
- Docker Compose profiles align with product profiles.
- Experimental skills can be hidden behind feature flags.

---

## 31. Accessibility and Consumer Hardware Support

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

## 32. VS Code / Developer Experience

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
skill compiler command
company template import command
```

---

## 33. Local Open-Source App Profiles

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

## 34. Connector Ecosystem Hardening

Prioritize robust production-grade connectors with health checks, auth, retry, rate limits, and schema mapping.

Priority connectors:

```text
GitHub
Google Workspace/Gmail/Calendar
Slack/Teams
CRM local connector
PostHog/CDP connector
ERPNext/Odoo connector
Metabase connector
Chatwoot/Zammad connector
BookStack/Wiki.js connector
Stripe/payment connector, read-only first
Salesforce/HubSpot, optional
```

Acceptance criteria:

- Each connector has health check.
- Each connector declares rate limits.
- Each connector supports dry-run.
- Write actions require approval.
- Connector failures are surfaced in dashboard.

---

## 35. Self-Improvement and Evolution Loop

Create or harden:

```text
core/evolution-engine/
core/skill-gap-engine/
scripts/evolution/propose_skill_changes.py
scripts/evolution/generate_skill_pr.py
scripts/evolution/review_skill_change.py
```

Rules:

- Self-improvement proposes changes only.
- Human review required before applying changes.
- Proposed changes must include tests/evals.
- CI must pass before merge.

Acceptance criteria:

- System can identify skill gaps from failed workflows.
- System can generate a PR-ready patch.
- System cannot auto-merge or auto-apply high-risk changes.
- Procedural memory is updated after approved improvements.

---

## 36. Skill Marketplace and Registry

Create:

```text
skill_registry/
skill_registry/README.md
skills/CONTRIBUTING.md
CONTRIBUTING.md
CODE_OF_CONDUCT.md
.github/ISSUE_TEMPLATE/
.github/PULL_REQUEST_TEMPLATE.md
scripts/registry/validate_registry_entry.py
scripts/registry/package_skill.py
scripts/registry/publish_skill.py
schemas/skill-package.schema.json
schemas/skill-lockfile.schema.json
```

Skill marketplace features:

```text
local registry first
public registry optional
versioned skills
signed skills
reputation score
test score
maturity level
governance level
dependency locking
enterprise approval workflow
examples
tests/evals
```

Acceptance criteria:

- Contributors can add a skill with one documented workflow.
- Registry validation runs in CI.
- Skill packages can be versioned and locked.
- Public publishing is optional and disabled by default.

---

## 37. Commercial and Open-Source Boundary

Create:

```text
COMMERCIAL.md
LICENSE_REVIEW.md
docs/commercial/open-core-boundary.md
```

Clarify:

```text
open-source core
open skill format
local solo usage
hosted/cloud tier
enterprise governance features
multi-tenancy
billing/usage analytics
commercial support
CLA policy if needed
```

Acceptance criteria:

- Users understand what is open vs paid.
- Hosted/enterprise ambitions do not confuse local OSS usage.

---

## 38. Backup and Restore for Docker Deployment

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

## 39. Security Hardening for Docker Deployment

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

## 40. Documentation, API Docs, and Demo Assets

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
success stories/case studies
competitor-positioning page for maintainers
AI OS architecture page
memory/knowledge graph explanation
skill marketplace guide
```

---

## 41. Container Smoke Tests

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

## 42. Phase 1 MVP Execution Plan

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
[ ] formal skill.yaml schema for MVP skills
[ ] skill graph engine MVP
[ ] skill activity runtime hardening
[ ] execute_workflow live/dry-run reliability
[ ] skill_pipeline.py compiler MVP
[ ] OldFarmTrucks company template
[ ] 5 executable reference workflows
[ ] multi-layer memory MVP
[ ] AI telemetry event schema MVP
[ ] policy runtime enforcement for writes
[ ] chat UI MVP
[ ] dashboard/control-plane MVP
[ ] rate-limit policy skeleton
[ ] budget/cost report skeleton
[ ] connector health check MVP
[ ] container smoke tests
[ ] local-solo profile
[ ] docs quickstart
[ ] contribution/registry skeleton
```

Success metrics:

```text
runnable demos
>50% MVP skills executable
5 reference workflows dry-run end-to-end
1 company template importable
passing end-to-end tests
user feedback from beta testers
reduced manual intervention in workflow loops
no dry-run side effects
workflow traces visible
memory updates visible
```

---

## 43. Recommended Implementation Order

1. Dockerfile and `.dockerignore`.
2. `.env.example`.
3. Core `docker-compose.yml` with Qdrant, Temporal, Postgres, Redis, apotheon-cli.
4. Formal `skill.yaml` schema and progressive loading.
5. Skill graph engine MVP.
6. Runtime execution hardening.
7. `skill_pipeline.py` compiler MVP.
8. Multi-layer memory MVP.
9. AI telemetry event schema and report MVP.
10. Policy/governance runtime enforcement.
11. OldFarmTrucks company template.
12. Reference workflow fixtures.
13. Container smoke tests.
14. Worker and scheduler services.
15. Docker deployment docs.
16. Chat UI MVP.
17. Dashboard/control-plane MVP.
18. Rate-limit manager.
19. Budget/cost dashboard.
20. Modular profiles and feature flags.
21. Connector health check MVP.
22. Local app compose profiles.
23. Registry/contribution skeleton.
24. Backup/restore scripts.
25. Docker security baseline.
26. Server deployment compose file.
27. VS Code/devcontainer enhancements.

---

## 44. Release Acceptance Criteria

Docker/productization is complete when:

```text
[ ] Docker image builds reproducibly
[ ] Core compose stack starts locally
[ ] Qdrant, Temporal, Postgres, and Redis are healthy
[ ] Validation commands run inside container
[ ] skill.yaml schema validates MVP skills
[ ] Skill graph report generated
[ ] Workflow dry-run works inside container
[ ] Skill pipeline compiler generates runnable scaffolds
[ ] Multi-layer memory records workflow execution data
[ ] AI telemetry report generated
[ ] Policy kernel blocks high-risk writes by default
[ ] At least 5 reference workflows execute end-to-end in dry-run
[ ] At least 3 reference workflows execute live in controlled mode
[ ] OldFarmTrucks company template imports successfully
[ ] Worker service starts
[ ] Scheduler service starts in dry-run mode
[ ] Health report is generated
[ ] Chat UI MVP can submit an objective and display workflow plan
[ ] Dashboard MVP displays runs, schedules, costs, rate limits, memory, telemetry, and health
[ ] Rate-limit policies exist for connectors and APIs
[ ] Budget/cost reports exist
[ ] Governance runtime blocks high-risk writes by default
[ ] Connector health checks exist for priority connectors
[ ] Skill registry/contribution skeleton exists
[ ] Backup/restore dry-run exists
[ ] Docker security baseline passes
[ ] Documentation includes laptop and server setup
[ ] OldFarmTrucks.com demo is executable
```
