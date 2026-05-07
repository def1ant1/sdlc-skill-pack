# Agent Registry

Used by `core/multi-agent/SKILL.md` as the canonical reference for all registered
specialist agents, their capabilities, input requirements, and output formats.

---

## architect

| Property | Value |
|---|---|
| File | `agents/architect/agent.md` |
| Role | System design, architecture decisions, quality attribute analysis, ADR authoring |
| Primary inputs | Requirements artifacts, constraints, technology context |
| Primary outputs | Architecture Decision Records (ADRs), system diagrams (textual), quality attribute evaluation, tradeoff analysis |
| Can challenge | Performance claims, implementation proposals |
| Authority domain | Architecture — decisions stand unless overridden by security or compliance |
| Token budget | Medium (3000–8000 tokens) |

---

## security

| Property | Value |
|---|---|
| File | `agents/security/agent.md` |
| Role | Threat modeling, vulnerability assessment, security policy review, secrets audit |
| Primary inputs | Architecture artifacts, code artifacts, deployment configs |
| Primary outputs | Threat model, vulnerability report, security recommendations, PASS/FAIL gate verdict |
| Can challenge | Any artifact — security review cannot be waived |
| Authority domain | Security — security requirements override architecture and performance |
| Token budget | Medium (2000–6000 tokens) |

---

## reviewer

| Property | Value |
|---|---|
| File | `agents/reviewer/agent.md` |
| Role | Code review, artifact quality review, standards compliance check |
| Primary inputs | Code diffs, architecture documents, skill outputs |
| Primary outputs | Review report with findings (PASS/WARN/FAIL per criterion), inline comments |
| Can challenge | Any artifact in its review scope |
| Authority domain | Quality standards — findings must be addressed before gate passes |
| Token budget | Low–Medium (1000–4000 tokens per artifact) |

---

## tester

| Property | Value |
|---|---|
| File | `agents/tester/agent.md` |
| Role | Test strategy design, edge case identification, coverage analysis, acceptance criteria |
| Primary inputs | Feature requirements, API contracts, backend artifacts |
| Primary outputs | Test plan, edge case catalog, coverage report, acceptance criteria checklist |
| Can challenge | Completeness of requirements and implementation |
| Authority domain | Test coverage — cannot be overridden; missing coverage blocks gate |
| Token budget | Medium (2000–5000 tokens) |

---

## optimizer

| Property | Value |
|---|---|
| File | `agents/optimizer/agent.md` |
| Role | Performance analysis, cost efficiency, resource utilization, bottleneck identification |
| Primary inputs | Architecture artifacts, code artifacts, telemetry data |
| Primary outputs | Performance analysis report, optimization recommendations, cost estimates |
| Can challenge | Architecture and implementation choices on efficiency grounds |
| Authority domain | Performance — recommendations are advisory unless security/compliance conflict |
| Token budget | Medium (2000–5000 tokens) |

---

## researcher

| Property | Value |
|---|---|
| File | `agents/researcher/agent.md` |
| Role | Technology evaluation, market research, competitive analysis, benchmarking |
| Primary inputs | Research questions, technology landscape, benchmark requirements |
| Primary outputs | Research report, technology comparison table, recommendation with rationale |
| Can challenge | Technology choices based on evidence |
| Authority domain | Evidence — findings are advisory; decisions made by architect or operator |
| Token budget | High (3000–10000 tokens) |

---

## gtm-agent

| Property | Value |
|---|---|
| File | `agents/gtm-agent/agent.md` |
| Role | Go-to-market strategy, launch planning, positioning, channel selection |
| Primary inputs | Product requirements, ICP definition, competitive landscape |
| Primary outputs | GTM strategy brief, launch timeline, channel recommendations, messaging framework |
| Can challenge | Product scope if misaligned with market need |
| Authority domain | GTM — recommendations are advisory; approved by operator |
| Token budget | Medium (2000–6000 tokens) |

---

## analytics-agent

| Property | Value |
|---|---|
| File | `agents/analytics-agent/agent.md` |
| Role | Metrics framework design, funnel analysis, attribution modeling, KPI definition |
| Primary inputs | Product goals, existing analytics data, GTM artifacts |
| Primary outputs | Metrics framework, analytics instrumentation plan, KPI baseline, attribution model |
| Can challenge | GTM decisions lacking measurement plans |
| Authority domain | Measurement — KPI baselines required before paid channels activate |
| Token budget | Medium (2000–5000 tokens) |

---

## governance-agent

| Property | Value |
|---|---|
| File | `agents/governance-agent/agent.md` |
| Role | Compliance review, policy generation, audit preparation, regulatory alignment |
| Primary inputs | Architecture artifacts, data models, security artifacts, jurisdiction context |
| Primary outputs | Compliance gap analysis, policy documents, audit checklist, regulatory risk assessment |
| Can challenge | Any artifact touching regulated data (PII, PHI, financial) |
| Authority domain | Compliance — findings must be resolved before release gate |
| Token budget | Medium (2000–6000 tokens) |

---

## Handoff Packet Format

When one agent hands off to another, include:

```yaml
agent_handoff:
  from_agent: [agent name]
  to_agent: [agent name]
  task: [description]
  outputs_produced:
    - type: [document | report | code | recommendation]
      name: [artifact name]
      location: [file path or reference]
      status: [draft | final]
  decisions_made:
    - [DEC-NNN]: [brief]
  open_questions:
    - [OQ-NNN]: [question that the receiving agent must answer]
  constraints_to_apply:
    - [constraint from memory packet relevant to next agent]
```