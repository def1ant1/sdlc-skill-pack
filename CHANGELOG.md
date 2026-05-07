# Changelog

All notable changes to the Apotheon AI Company OS are documented here.

---

## [7.0.0] — 2026-05-07 — Sovereign Enterprise Intelligence

Implements phases 52–74 of the Master Optimized Enhancement Backlog: Cognitive Runtime,
Distributed Agent OS, Enterprise Semantic Intelligence, AI Safety Runtime, Sovereign
Infrastructure, and Self-Evolving Enterprise Cognition.

### New Core Skills — Cognitive Runtime (Wave 4)

- `core/cognitive-runtime` — Hierarchical goal decomposition, planning strategy selection, adaptive replanning
- `core/workflow-runtime` — Durable execution with checkpointing, state recovery, deterministic replay
- `core/agent-kernel` — Multi-agent process isolation, resource quotas, lifecycle management
- `core/agent-identity` — Persistent agent expertise profiles, episodic/procedural/semantic memory, reputation scoring
- `core/evolution-engine` — Autonomous self-improvement: gap detection → proposal → approval → execution

### New Core Skills — Distributed Agent OS (Wave 5)

- `core/distributed-agent-runtime` — Multi-node agent coordination with load balancing and fault tolerance
- `core/event-bus` — Distributed async event routing with at-least-once delivery, event sourcing, and replay
- `core/agent-kernel` — Execution scheduler, process isolation, resource quota enforcement

### New Core Skills — Enterprise Semantic Intelligence (Wave 3/4)

- `core/semantic-layer` — Enterprise ontology reasoning, entity resolution, temporal graph analysis
- `core/data-fabric` — Schema governance, data lineage tracking, data contract enforcement
- `core/master-data-management` — Golden record management, deduplication, survivorship rules
- `core/research-runtime` — Autonomous R&D: hypothesis→experiment→synthesis lifecycle
- `core/simulation-engine` — Digital twin runtime for business, infrastructure, and security simulation
- `core/explainability` — Causal reasoning traces, execution lineage, governance-grade explanations
- `core/predictive-reasoning` — Temporal intelligence and probabilistic enterprise outcome forecasting

### New Core Skills — AI Safety & Infrastructure (Wave 5)

- `core/alignment-engine` — Runtime safety enforcement, constitutional compliance scoring, deception detection
- `core/cluster-management` — GPU cluster optimization, topology-aware model placement, VRAM management
- `core/model-lifecycle` — Model promotion gates, canary deployment, quality monitoring, retirement
- `core/model-routing` — Task complexity estimation, adaptive local/cloud routing, cost-quality optimization
- `core/benchmark-factory` — Benchmark creation, curation, versioning, and evaluation governance

### New Core Skills — Enterprise Autonomy (Wave 6)

- `core/economic-coordination` — Priority scheduling, quota enforcement, budget-aware compute arbitration
- `core/federated-runtime` — Air-gapped, edge, and federated deployment with residency enforcement
- `core/privacy-runtime` — PII detection/redaction, retention enforcement, legal holds, residency compliance

### New Domain Skills — Durable Execution (Phase 53)

- `skills/checkpoint-management` — Workflow state serialization and durable storage
- `skills/runtime-recovery` — Failure classification and checkpoint-based recovery
- `skills/workflow-replay` — Deterministic workflow replay for audit and debugging
- `skills/state-restoration` — Checkpoint deserialization and context reconstruction

### New Domain Skills — Cognitive Runtime (Phase 54)

- `skills/hierarchical-planning` — HTN-based goal decomposition and execution planning
- `skills/meta-reasoning` — Reasoning chain quality evaluation and bias detection
- `skills/goal-decomposition` — Atomic sub-goal generation with measurable success criteria
- `skills/self-reflection` — Output quality review and systematic improvement recommendations
- `skills/constraint-reasoning` — Hard/soft constraint evaluation and alternative plan generation
- `skills/causal-analysis` — Causal inference (DiD, IV, RCT) for enterprise decisions
- `skills/long-horizon-planning` — Rolling-horizon multi-week to multi-year planning

### New Domain Skills — AI Safety & Alignment (Phase 58)

- `skills/alignment-testing` — Pre-deployment behavioral test suites and alignment scorecards
- `skills/harm-classification` — Multi-taxonomy harm scoring and mitigation routing
- `skills/deception-detection` — Hallucination, authority escalation, and manipulation detection
- `skills/adversarial-evaluation` — Structured red team evaluation and agent hardening
- `skills/policy-simulation` — Policy change impact simulation before enforcement

### New Domain Skills — Infrastructure Intelligence (Phase 59)

- `skills/gpu-cluster-optimization` — Topology-aware model placement and VRAM defragmentation
- `skills/inference-batching-optimization` — Dynamic batch sizing and window tuning
- `skills/network-topology-analysis` — NVLink/PCIe topology mapping and bottleneck detection
- `skills/model-placement-optimization` — Optimal model shard placement scoring and execution
- `skills/cache-placement-optimization` — KV cache sizing, prefix warmup, and eviction tuning

### New Domain Skills — Explainability & Causal Intelligence (Phase 61)

- `skills/causal-tracing` — Evidence-weighted root cause attribution from event streams
- `skills/execution-explanation` — Layered natural-language workflow explanations by audience
- `skills/policy-justification` — Evidence-backed policy enforcement justifications
- `skills/reasoning-visualization` — Goal trees and reasoning chains in Mermaid/DOT format

### New Domain Skills — Data Fabric & Governance (Phase 62–63)

- `skills/schema-evolution` — Breaking change detection and migration coordination
- `skills/data-contract-management` — Contract authoring, compliance monitoring, violation enforcement
- `skills/lineage-analysis` — Upstream provenance and downstream impact traversal
- `skills/dataset-curation` — Quality filtering, deduplication, and annotation consistency

### New Domain Skills — Autonomous Research (Phase 64)

- `skills/literature-review` — Systematic search, screening, synthesis, and gap identification
- `skills/research-analysis` — Statistical analysis, hypothesis testing, evidence grading
- `skills/hypothesis-generation` — Abductive reasoning for testable hypothesis generation
- `skills/patent-analysis` — FTO assessment, IP landscape mapping, white space identification
- `skills/discovery-synthesis` — Cross-stream research synthesis with convergence scoring

### New Domain Skills — Simulation & Digital Twin (Phase 65)

- `skills/business-simulation` — Monte Carlo scenario analysis for strategic decisions
- `skills/incident-simulation` — Game day exercises for SRE and security preparedness
- `skills/security-war-gaming` — ATT&CK-based adversarial exercises and defensive gap analysis
- `skills/runtime-simulation` — AI infrastructure behavior simulation for pre-deployment validation

### New Domain Skills — Benchmarking Platform (Phase 66)

- `skills/benchmark-generation` — Calibrated benchmark dataset generation with adversarial cases
- `skills/evaluation-dataset-curation` — Rigorous curation: correctness, deduplication, balance
- `skills/synthetic-dataset-generation` — Controlled synthetic training/eval data generation
- `skills/scenario-generation` — Diverse scenario synthesis for simulation and evaluation

### New Domain Skills — Model Lifecycle (Phase 67–68)

- `skills/model-benchmarking` — Standardized capability evaluation with trend tracking
- `skills/model-distillation` — Teacher-to-student knowledge transfer for local inference
- `skills/quantization-optimization` — INT4/INT8/GPTQ/AWQ quantization with quality validation
- `skills/lora-management` — LoRA adapter registration, hot-swap, routing, and retirement
- `skills/model-selection-optimization` — Multi-criteria task-to-model matching
- `skills/uncertainty-aware-routing` — Confidence-based inference escalation
- `skills/reasoning-depth-estimation` — Task complexity estimation for tier selection

### New Domain Skills — Portfolio Governance & PMO (Phase 71)

- `skills/portfolio-optimization` — Multi-criteria initiative scoring and resource allocation
- `skills/program-governance` — Milestone tracking, risk escalation, executive reporting
- `skills/initiative-prioritization` — Weighted multi-criteria initiative ranking
- `skills/capacity-balancing` — Resource capacity analysis and overcommitment detection

### New Domain Skills — Enterprise Data Privacy (Phase 72)

- `skills/pii-detection` — Multi-layer PII detection with regex, NER, and contextual classification
- `skills/data-redaction` — Jurisdiction-aware redaction, pseudonymization, and tokenization
- `skills/legal-hold-management` — Legal hold lifecycle from placement through release
- `skills/residency-analysis` — Cross-boundary data flow analysis and compliant routing

### New Reference Files — Session 2 (2026-05-07)

**Domain Skill Reference Files (34 files completing all MEDIUM gaps):**

- `skills/adversarial-evaluation/references/adversarial-playbook.md` — 8 attack categories, templates, ASR thresholds, severity scoring
- `skills/alignment-testing/references/alignment-test-suites.md` — 5 test suites (CC, BTC, SR, CB, UC), deployment gate protocol
- `skills/benchmark-generation/references/benchmark-spec-format.md` — Package structure, metadata/item/rubric schemas, quality gates
- `skills/business-simulation/references/simulation-methodology.md` — Monte Carlo, system dynamics, ABM, sensitivity analysis, output format
- `skills/cache-placement-optimization/references/cache-optimization-strategies.md` — Prompt prefix, semantic, tiered cache, placement scoring
- `skills/capacity-balancing/references/capacity-planning-model.md` — Demand forecasting, LP optimization, rebalancing triggers, capacity plan
- `skills/causal-tracing/references/causal-attribution.md` — Activation patching, counterfactual, Shapley, causal graph methods
- `skills/constraint-reasoning/references/constraint-catalog.md` — HC/SC/PR/IV taxonomy, YAML schema, standard library, CSP algorithm
- `skills/dataset-curation/references/curation-thresholds.md` — Quality filters, dedup thresholds, IAA metrics, pipeline gates
- `skills/discovery-synthesis/references/synthesis-framework.md` — Evidence integration, convergent/divergent synthesis, gap identification
- `skills/evaluation-dataset-curation/references/evaluation-curation-standards.md` — 3-level verification, anti-gaming, contamination check, release criteria
- `skills/execution-explanation/references/explanation-templates.md` — 4 audience tier templates (Executive, Manager, Engineer, Auditor)
- `skills/goal-decomposition/references/goal-schema.md` — SMART criteria, MECE decomposition, AND-OR trees, progress tracking
- `skills/gpu-cluster-optimization/references/cluster-topology.md` — Node types, NVLink specs, thermal/power constraints, placement rules
- `skills/hierarchical-planning/references/htn-decomposition-rules.md` — Method format, HTN algorithm, selection heuristics, plan quality metrics
- `skills/incident-simulation/references/game-day-scenarios.md` — 4 scenario categories (infra, security, data, capacity), scoring rubric
- `skills/inference-batching-optimization/references/batching-policy.md` — Batching strategies, adaptive algorithm, continuous batching, metrics
- `skills/lineage-analysis/references/lineage-graph-schema.md` — Node/edge types, JSON-LD format, upstream/downstream traversal, PII propagation
- `skills/lora-management/references/adapter-registry-schema.md` — Registry YAML, query API, composition rules, serving config, deprecation
- `skills/long-horizon-planning/references/rolling-horizon-methodology.md` — Horizon zones, promotion protocol, forecast locks, scenario integration
- `skills/meta-reasoning/references/bias-catalog.md` — 5 bias categories, 18 biases, detection heuristics, debiasing prompts
- `skills/model-benchmarking/references/evaluation-methodology.md` — 3 protocols (zero-shot/few-shot/CoT), metrics, capability profile, comparison
- `skills/model-distillation/references/distillation-protocol.md` — 4 distillation methods, 6-step pipeline, quality gates, run record
- `skills/model-placement-optimization/references/placement-scoring-algorithm.md` — 5 score components, scheduling algorithm, placement decision log
- `skills/network-topology-analysis/references/topology-graph-schema.md` — Node/edge schemas, JSON-LD, Dijkstra/bottleneck/fault queries
- `skills/patent-analysis/references/patent-analysis-methodology.md` — Prior art search, claim parsing, claim charts, FTO opinion, IPC codes
- `skills/policy-justification/references/justification-templates.md` — 4 templates (regulatory, security, operational, AI safety)
- `skills/policy-simulation/references/policy-simulation-model.md` — Behavioral model, impact categories, scenarios, consequence detection
- `skills/reasoning-depth-estimation/references/depth-estimation-heuristics.md` — 8-level taxonomy, 3 heuristics, composite scoring, calibration
- `skills/reasoning-visualization/references/visualization-formats.md` — 6 visualization types, Mermaid templates, rendering guidelines
- `skills/research-analysis/references/analysis-methods-guide.md` — Method decision tree, quantitative/qualitative methods, reporting standards
- `skills/runtime-simulation/references/runtime-simulation-models.md` — M/M/K queuing, DES workflow, load profile simulation, calibration
- `skills/scenario-generation/references/scenario-space-taxonomy.md` — 3 classification dimensions, coverage requirements, narrative template
- `skills/security-war-gaming/references/war-game-scenarios.md` — 4 scenario types (APT, insider, AI red team, ransomware), scoring rubric
- `skills/self-reflection/references/quality-rubric.md` — 5 quality dimensions, composite score, threshold table, improvement protocol
- `skills/state-restoration/references/restoration-validation-rules.md` — Consistency/completeness/safety rules, decision matrix, audit log
- `skills/synthetic-dataset-generation/references/generation-prompt-templates.md` — 4 templates (instruction, code, Q&A, dialogue), batch config
- `skills/workflow-replay/references/replay-protocol.md` — 5 replay modes, preconditions, determinism controls, step-by-step protocol

### Validation Status (2026-05-07)

- `validate_skill_structure.py`: **PASS** — `{"valid": true, "errors": []}`
- `validate_frontmatter.py`: **PASS** — `{"valid": true, "errors": []}`
- `detect_skill_gaps.py`: **1 gap (known false positive)** — CUR-003 for `alignment-testing` caused by `'test' in str(f)` path filter in gap detector; skill exists and is valid
- All domain and core SKILL.md files: **complete**
- All reference files: **complete**

---

### New Reference Files — Session 1 (2026-05-07)

**Cognitive Runtime:**
- `core/cognitive-runtime/references/goal-tree-schema.md` — Goal hierarchy data model, serialization, knowledge graph integration
- `core/cognitive-runtime/references/planning-strategies.md` — 5 planning strategies with selection rules and replanning triggers

**Alignment Engine:**
- `core/alignment-engine/references/constitutional-rules.md` — 5 constitutional rules with scoring weights and enforcement thresholds
- `core/alignment-engine/references/behavioral-taxonomy.md` — 5 behavioral categories, deception pattern catalog

**Agent Kernel:**
- `core/agent-kernel/references/agent-lifecycle-states.md` — 7-state lifecycle machine with telemetry events per transition
- `core/agent-kernel/references/resource-quota-policy.md` — 5 quota tiers, enforcement mechanisms, cost accounting

**Semantic Layer:**
- `core/semantic-layer/references/enterprise-ontology.md` — 30+ entity types, 15 relationships, temporal properties, constraints
- `core/semantic-layer/references/semantic-reasoning-rules.md` — 5 inference rules, 3 temporal reasoning rules, Cypher query patterns

**Workflow Runtime:**
- `core/workflow-runtime/references/checkpoint-schema.md` — Checkpoint payload YAML, storage backends, retention policy, idempotency
- `core/workflow-runtime/references/recovery-runbook.md` — Failure classification tree, 5 recovery strategies, post-mortem template

**Agent Identity:**
- `core/agent-identity/references/agent-identity-schema.md` — Identity record YAML, 3 memory types, reputation scoring, persistence

**Model Routing:**
- `core/model-routing/references/routing-policy.md` — 5 capability tiers, 4 routing rules, complexity estimation, overflow policy

**Economic Coordination:**
- `core/economic-coordination/references/resource-arbitration-policy.md` — Priority weights, quota defaults, 5 enforcement rules

**Evolution Engine:**
- `core/evolution-engine/references/evolution-constraints.md` — Scope boundaries by approval level, rollback criteria, proposal format

---

## [6.0.0] — 2026-05-07 — Business Operations & Organizational Intelligence

Implemented phases 32–51 of the Master Optimized Enhancement Backlog: Business Operations,
Finance/Accounting, Meeting Intelligence, Enterprise Search, Governance, Developer Experience,
and all associated reference files and scripts.

### New Core Skills

- `core/workflow-engine` — DAG execution backbone with 8 built-in workflow templates
- `core/skill-gap-engine` — Self-auditing registry scanner with 6-dimension quality rubric
- `core/business-orchestration` — Non-SDLC business task routing across domains
- `core/meeting-intelligence` — Transcript → decisions → action items → knowledge graph
- `core/enterprise-search` — Hybrid vector+BM25 search across 7 organizational indexes
- `core/governance` — Policy registry, approval authority matrix, AI governance reporting

### New Domain Skills

- `skills/accounting-automation` — Transaction processing, anomaly detection, approval routing
- `skills/budget-planning` — Annual/quarterly budget cycles, variance analysis, scenario planning
- `skills/legal-ops` — Contract lifecycle, NDA routing, risk flagging, counsel escalation
- `skills/workforce-management` — Employee records, org changes, compensation approvals
- `skills/vendor-procurement` — Vendor qualification, spend authority, contract management
- `skills/forecasting` — Revenue and operational forecasting (Holt-Winters, Prophet, driver-based)
- `skills/decision-intelligence` — Multi-criteria scoring, bias detection, decision records
- `skills/developer-experience` — SPACE framework, DX metrics, onboarding optimization

### New Scripts

- `scripts/skills/scan_skills.py` — Skill registry scanner with JSON and table output
- `scripts/skills/detect_skill_gaps.py` — Quality/coverage/staleness gap detection
- `scripts/skills/generate_skill_improvement_plan.py` — Sprint-targeted improvement plan generation
- `scripts/skills/scaffold_missing_skill.py` — New skill scaffolding from template
- `scripts/business/route_business_task.py` — Pattern-matching business task router
- `scripts/search/index_domain_content.py` — Content indexing for enterprise search
- `scripts/search/hybrid_enterprise_search.py` — BM25+vector hybrid search with RRF fusion
- `scripts/finance/detect_finance_anomalies.py` — Duplicate, velocity spike, and round-number detection

### New JSON Schemas

- `docs/schemas/meetings/meeting.yaml` — Meeting record schema
- `docs/schemas/meetings/action-item.yaml` — Action item lifecycle schema
- `docs/schemas/meetings/meeting-decision.yaml` — Decision extraction schema
- `docs/schemas/finance/transaction.yaml` — Transaction record schema
- `docs/schemas/finance/invoice.yaml` — Invoice schema with approval workflow
- `docs/schemas/finance/budget.yaml` — Budget period and variance schema

### New Reference Files (selected)

- `core/governance/references/governance-framework.md` — Policy registry, authority matrix, violation severity
- `core/workflow-engine/references/workflow-dsl.md` — Full YAML DSL with condition syntax and examples
- `core/workflow-engine/references/workflow-templates.md` — 8 built-in workflow templates
- `core/skill-gap-engine/references/capability-ontology.md` — 38-capability ontology across 6 domains
- `core/skill-gap-engine/references/skill-quality-rubric.md` — 6-dimension rubric with scoring examples
- `core/skill-gap-engine/references/gap-detection-rules.md` — 10 detection rules, gap record schema
- `core/enterprise-search/references/retrieval-fusion.md` — RRF formula, re-ranking, access control
- `core/enterprise-search/references/search-index-schema.md` — 7 index configurations
- `skills/repo-intelligence/references/complexity-scoring.md` — CC thresholds, cognitive CC, coverage correlation
- `skills/repo-intelligence/references/dependency-analysis.md` — Health metrics, risk scoring, license list
- `skills/repo-intelligence/references/technical-debt-patterns.md` — 6 debt patterns, priority formula, ledger schema
- `core/telemetry/references/telemetry-event-schema.md` — Base event structure, standard event types, PII policy
- `core/telemetry/references/observability-report-template.md` — Weekly report, SLO burn rate, four golden signals
- `core/kv-cache-management/references/prefix-caching-guide.md` — 5 cache zones, canonical ordering
- `core/retrieval-engine/references/reranking-policy.md` — 4-stage pipeline, 8 reranking signals
- `core/retrieval-engine/references/retrieval-backends.md` — Qdrant, Neo4j, Redis, BM25 configurations

---

## [5.0.0] — GTM Expansion

Added GTM orchestration, AI search optimization, content marketing, revenue operations,
product analytics, cloud deployment, customer success, and associated agents and scripts.

---

## [4.0.0] — Engineering SDLC Core

Added all 13 core engineering skills (requirements through executive reporting), 6 specialist
agents, multi-agent collaboration patterns, and SDLC orchestration core.

---

## [3.0.0] — AI Platform Core

Added local runtime, lora-lifecycle, synthetic-data, model-evaluation, sandbox-execution,
runtime-economics, kv-cache-management, retrieval-engine, multi-agent, and connector-hub.

---

## [2.0.0] — Knowledge & Memory

Added knowledge-graph, memory-token-management, strategic-planning, hitl-dashboard,
tenant-management, and telemetry.

---

## [1.0.0] — Security & Infrastructure

Added local-security, mcp-integrations, and initial CI pipeline.

---

## [0.1.0] — Phase 0 Foundation

- Created initial repository structure
- Added orchestration and memory-control skills
- Added governance, standards, policies, schemas, docs, and validation scripts