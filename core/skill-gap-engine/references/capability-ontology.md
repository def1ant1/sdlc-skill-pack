# Capability Ontology

## Overview

The capability ontology defines the taxonomy of platform capabilities and maps each
to the skill(s) that provide it. This ontology is used by the skill-gap-engine to
detect coverage gaps when new workflows reference capabilities with no skill coverage.

---

## Capability Domain Taxonomy

### Domain 1: SDLC (Software Development Lifecycle)

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-SDLC-001 | Requirements authoring (PRD, user stories) | requirements-engineering | — |
| CAP-SDLC-002 | Architecture design (ADR, diagrams) | architecture (agent) | knowledge-graph |
| CAP-SDLC-003 | AI feature engineering | ai-engineering | model-evaluation |
| CAP-SDLC-004 | Backend service development | backend-engineering | devsecops |
| CAP-SDLC-005 | Frontend/UI development | frontend-engineering | qa-automation |
| CAP-SDLC-006 | Code review and quality gate | code-review | devsecops |
| CAP-SDLC-007 | Test automation and coverage | qa-automation | devsecops |
| CAP-SDLC-008 | Security scanning and vulnerability management | devsecops | compliance-automation |
| CAP-SDLC-009 | Release management and deployment | release-management | workflow-engine |
| CAP-SDLC-010 | Observability and SLO management | observability | telemetry |
| CAP-SDLC-011 | Incident response and post-mortem | sre-incident-response | observability |

### Domain 2: AI Platform

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-AI-001 | Local model execution | local-runtime | lora-lifecycle |
| CAP-AI-002 | Model evaluation and benchmarking | model-evaluation | lora-lifecycle |
| CAP-AI-003 | LoRA adapter training and promotion | lora-lifecycle | model-evaluation |
| CAP-AI-004 | Synthetic training data generation | synthetic-data | lora-lifecycle |
| CAP-AI-005 | Prompt versioning and governance | governance | orchestration |
| CAP-AI-006 | RAG and vector retrieval | retrieval-engine | knowledge-graph |
| CAP-AI-007 | Knowledge graph management | knowledge-graph | retrieval-engine |
| CAP-AI-008 | KV cache optimization | kv-cache-management | local-runtime |
| CAP-AI-009 | Multi-agent coordination | multi-agent | orchestration |
| CAP-AI-010 | Sandbox code execution | sandbox-execution | devsecops |

### Domain 3: Business Operations

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-BIZ-001 | Finance and accounting automation | accounting-automation | budget-planning |
| CAP-BIZ-002 | Budget planning and forecasting | budget-planning | strategic-planning |
| CAP-BIZ-003 | Revenue operations | revenue-operations | product-analytics |
| CAP-BIZ-004 | Legal operations and contract management | legal-ops | compliance-automation |
| CAP-BIZ-005 | HR and workforce management | workforce-management | strategic-planning |
| CAP-BIZ-006 | Vendor and procurement management | vendor-procurement | budget-planning |
| CAP-BIZ-007 | Meeting intelligence and action tracking | meeting-intelligence | knowledge-graph |
| CAP-BIZ-008 | Executive reporting | executive-reporting | product-analytics |
| CAP-BIZ-009 | Strategic planning and OKR management | strategic-planning | executive-reporting |

### Domain 4: Customer

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-CX-001 | Customer success and health management | customer-success | product-analytics |
| CAP-CX-002 | Customer experience intelligence | customer-success | product-analytics |
| CAP-CX-003 | Product analytics and experimentation | product-analytics | customer-success |
| CAP-CX-004 | GTM orchestration | gtm-orchestration | revenue-operations |

### Domain 5: Compliance & Governance

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-GOV-001 | AI governance and policy enforcement | governance | compliance-automation |
| CAP-GOV-002 | Compliance automation and evidence | compliance-automation | compliance-governance |
| CAP-GOV-003 | Ongoing compliance governance | compliance-governance | compliance-automation |
| CAP-GOV-004 | Multi-tenant isolation | tenant-management | local-security |
| CAP-GOV-005 | Security and access control | local-security | governance |

### Domain 6: Platform Infrastructure

| Capability ID | Capability | Primary Skill | Secondary |
|---|---|---|---|
| CAP-INF-001 | Workflow orchestration | workflow-engine | orchestration |
| CAP-INF-002 | Business task routing | business-orchestration | workflow-engine |
| CAP-INF-003 | SDLC task routing | orchestration | workflow-engine |
| CAP-INF-004 | Runtime cost optimization | runtime-economics | local-runtime |
| CAP-INF-005 | Telemetry and metrics | telemetry | observability |
| CAP-INF-006 | Human-in-the-loop approvals | hitl-dashboard | governance |
| CAP-INF-007 | Enterprise search | enterprise-search | retrieval-engine |
| CAP-INF-008 | External integrations | connector-hub | mcp-integrations |
| CAP-INF-009 | Memory and context management | memory-token-management | knowledge-graph |
| CAP-INF-010 | Skill gap detection and improvement | skill-gap-engine | governance |

---

## Coverage Gap Detection Rules

A coverage gap exists when:

1. A workflow step references a capability ID with no primary skill registered
2. A primary skill is registered but has quality score < 60 (see skill-quality-rubric.md)
3. A capability is referenced in > 3 active workflows but the primary skill has maturity = alpha
4. A primary skill has not been updated in > 6 months and has > 5 active workflow dependencies