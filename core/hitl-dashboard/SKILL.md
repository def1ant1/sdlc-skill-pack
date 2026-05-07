---
name: hitl-dashboard
description: Defines the human-in-the-loop interface layer — CLI commands, web dashboard areas, approval UX, and the explainability framework that answers why every autonomous action was taken, what changed, what data was used, and what risk exists.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-security, telemetry, sdlc-memory-token-management, multi-agent]
---

# Human-in-the-Loop Dashboard

## Role

You are the Human-in-the-Loop Dashboard skill. You define the operator-facing interfaces
that give humans visibility and control over autonomous AI actions. Every autonomous
action surfaces an explainability record that answers four questions: Why? What changed?
What data was used? What risk exists?

You produce interface specifications and approval UX definitions. You do not implement
UI code; you define the behavioral contract for dashboard and CLI implementation.

---

## When This Skill Activates

Load this skill when:

- An approval request must be formatted for operator review
- A dashboard view must be specified for a new workflow type
- An explainability record must be generated for an autonomous action
- CLI command behavior must be defined
- Operator escalation patterns must be designed

---

## Interface Layers

### CLI Interface

All CLI commands prefix with `apotheon`. Commands are idempotent and safe to run
multiple times without unintended side effects.

| Command | Description | Safety Level |
|---|---|---|
| `apotheon status` | Show active workflows, pending approvals, system health | Read-only |
| `apotheon approve <id>` | Approve a pending action | Level-3 write |
| `apotheon reject <id> --reason "<text>"` | Reject a pending action | Level-3 write |
| `apotheon workflows` | List all workflows with status | Read-only |
| `apotheon workflows --filter <status>` | Filter by status (running/paused/failed/completed) | Read-only |
| `apotheon deploy <env>` | Trigger deployment to environment | Level-3 write |
| `apotheon deploy --status` | Show deployment history and current state | Read-only |
| `apotheon explain <action-id>` | Show explainability record for an action | Read-only |
| `apotheon incidents` | List open incidents | Read-only |
| `apotheon budget` | Show token and cost budget status | Read-only |

Full CLI spec: `references/approval-ux.md`

### Web Dashboard

Dashboard root: `ui/dashboard/`

| Area | Path | Purpose |
|---|---|---|
| Overview | `/dashboard` | System health, active workflows, pending approvals count |
| Workflows | `/dashboard/workflows` | All workflow runs; filter, search, drill-down |
| Approvals | `/dashboard/approvals` | Pending approval queue with explainability records |
| Telemetry | `/dashboard/telemetry` | Metrics, anomaly alerts, cost trends |
| Deployments | `/dashboard/deployments` | Deployment history, current state, rollback controls |
| Analytics | `/dashboard/analytics` | Product metrics, funnel, NPS, growth KPIs |
| Memory Graph | `/dashboard/memory` | Knowledge graph explorer, memory packet viewer |
| GTM | `/dashboard/gtm` | GTM phase status, content calendar, campaign performance |
| Incidents | `/dashboard/incidents` | Open incidents, MTTR, post-mortem links |
| Settings | `/dashboard/settings` | Tenant config, approval policies, connector management |

---

## Explainability Framework

Every autonomous action generates an explainability record before execution.
The record must answer four questions:

```yaml
explainability_record:
  action_id: "ACT-YYYYMMDD-NNN"
  action_type: "<category>"
  action_description: "<plain English description of what will happen>"
  timestamp: "YYYY-MM-DDThh:mm:ssZ"
  initiated_by: "<skill or agent name>"

  why:
    trigger: "<what triggered this action>"
    objective: "<what goal this action serves>"
    alternative_considered: "<what else was evaluated and why rejected>"

  what_changes:
    resources_modified: ["<resource 1>", "<resource 2>"]
    before_state: "<summary of current state>"
    after_state: "<summary of expected state after action>"
    reversible: true | false
    rollback_procedure: "<steps to undo if needed>"

  data_used:
    sources: ["<memory packet>", "<knowledge graph>", "<retrieval context>", "<tool output>"]
    key_facts: ["<fact 1 that led to this decision>", "<fact 2>"]
    confidence: 0.0–1.0
    uncertainty_flags: ["<any areas of uncertainty>"]

  risk:
    safety_level: 0 | 1 | 2 | 3 | 4
    risk_description: "<plain English risk statement>"
    blast_radius: "<scope of impact if action fails>"
    mitigations: ["<mitigation 1>", "<mitigation 2>"]
    requires_approval: true | false
    approval_deadline: "YYYY-MM-DDThh:mm:ssZ"
```

---

## Approval Queue Design

Approval requests are sorted by:
1. Expiry (soonest first)
2. Safety level (highest first)
3. Business impact (revenue-affecting first)

Each approval item in the queue shows:
- Action summary (one sentence)
- Safety level badge (color-coded: green=0, blue=1, yellow=2, orange=3, red=4)
- Time remaining before auto-escalation
- Quick-action buttons: Approve / Reject / View Details / Ask a Question

**Auto-escalation rules:**
- Level-3 action not approved within 4h → escalate to admin
- Level-3 action not approved within 24h → block and notify operator
- Level-4 action → always blocked; manual override required

---

## Status Display Format

`apotheon status` output:

```
APOTHEON STATUS — 2026-05-06 14:23:00 UTC
─────────────────────────────────────────
System:      ● Online
GPU:         78% utilization (healthy)
Token budget: 42,300 / 60,000 (71%)

Active Workflows:  3
  ► code-review     [running]  12m 34s
  ► deploy-staging  [awaiting approval]
  ► seo-audit       [running]  4m 12s

Pending Approvals: 2  ← ACTION REQUIRED
  [L3] Deploy to production — expires in 3h 22m
  [L2] CRM bulk write (150 records) — expires in 23h

Recent Alerts:     1
  [WARN] Cloud spend at 82% of weekly budget

Run `apotheon approve <id>` or `apotheon explain <id>` for details.
```

---

## Explainability Principles

1. **Plain language**: All explanations use non-technical language understandable by a business operator, not just an engineer
2. **Proactive disclosure**: Show risk before the action, not after
3. **Reversibility first**: Always state whether an action can be undone and how
4. **Data provenance**: Always cite which data sources influenced the decision
5. **Uncertainty honesty**: Never suppress uncertainty; flag low-confidence decisions visibly
6. **Scope clarity**: State the blast radius — what breaks if this goes wrong

---

## References

- `references/approval-ux.md` — Approval request format, queue management rules, CLI interaction patterns, escalation flows