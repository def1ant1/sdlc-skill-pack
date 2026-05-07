# Governance Framework

## Policy Registry Schema

All policies in the governance framework are registered with the following fields:

```yaml
policy:
  id: "POL-NNN"
  name: "<policy name>"
  category: "ai-governance | data | security | operational | financial | legal"
  owner: "<team or role>"
  version: "x.y.z"
  effective_date: "YYYY-MM-DD"
  review_date: "YYYY-MM-DD"
  status: "active | deprecated | draft | under-review"
  scope: "<what this policy applies to>"
  frameworks: [SOC2, ISO27001, GDPR, EU-AI-Act]
  related_controls: ["CTRL-NNN"]
  document_path: "<path to policy document>"
```

---

## Active Policy Registry

| ID | Policy | Category | Owner | Version | Review Date | Status |
|---|---|---|---|---|---|---|
| POL-001 | AI Safety Policy | ai-governance | AI team | 1.0.0 | 2027-05-01 | Active |
| POL-002 | Data Governance Policy | data | Data team | 1.0.0 | 2027-05-01 | Active |
| POL-003 | Secure Development Policy | security | Security team | 1.0.0 | 2027-05-01 | Active |
| POL-004 | Architectural Review Policy | operational | Architecture team | 1.0.0 | 2027-05-01 | Active |
| POL-005 | AI Model Deployment Policy | ai-governance | AI team | 1.0.0 | 2027-05-01 | Active |
| POL-006 | Autonomous Action Boundary Policy | ai-governance | Platform team | 1.0.0 | 2026-11-01 | Active |
| POL-007 | Prompt Governance Policy | ai-governance | AI team | 1.0.0 | 2027-05-01 | Active |

---

## Action Boundary Table

Defines what autonomous actions each skill/agent class may take without human approval:

| Action Category | Default Boundary | Override Path | Governance Level |
|---|---|---|---|
| Read-only analysis | Fully autonomous | None needed | Level 0 |
| Draft generation (internal) | Fully autonomous | None needed | Level 0 |
| External communication draft | Autonomous draft; human sends | None needed | Level 1 |
| Data writes (< 100 records) | Autonomous with audit log | Pre-approved per workflow | Level 1 |
| Data writes (100–10K records) | Requires Level-2 approval | None | Level 2 |
| Data deletes (any volume) | Requires Level-2 + confirmation | None | Level 2 |
| Production deployments | Requires Level-3 approval | Waiver for routine (hitl-dashboard) | Level 3 |
| Financial transactions | Blocked; always human | Level-3 + CFO sign-off | Level 4 |
| Model/prompt changes in production | Level-2 + regression test | None | Level 2 |
| Policy changes | Level-3 + governance review | None | Level 3 |
| New agent/skill activation | Level-3 | None | Level 3 |
| Audit log modification | Blocked; immutable | None | Level 4 |
| Agent authority escalation | Blocked; always human | None | Level 4 |

---

## Approval Level Definitions

| Level | Description | Authority |
|---|---|---|
| Level 0 | Autonomous — no human approval needed | Any registered agent |
| Level 1 | Autonomous with audit trail | Any registered agent; log required |
| Level 2 | Human review required | Operator or team lead |
| Level 3 | Senior approval required | VP / Director / C-suite |
| Level 4 | Blocked — no autonomous path | Human only; cannot be delegated |

---

## Violation Severity Matrix

| Violation | Severity | Response |
|---|---|---|
| Action taken without required approval | CRITICAL | Immediate halt; audit review; notify Level-3 |
| Data accessed beyond permitted scope | HIGH | Halt; investigate; notify data owner |
| Model used outside authorized task types | HIGH | Log; alert; route to model-evaluation |
| Output published without required human review | CRITICAL | Retract if possible; notify affected parties |
| Audit log write skipped | CRITICAL | Halt; escalate to Level-3; treat as potential breach |
| Agent escalated its own authority | CRITICAL | Immediate halt; treat as security incident |
| Financial transaction attempted | CRITICAL | Halt; escalate to CFO; treat as security incident |
| Policy review overdue > 30 days | MEDIUM | Alert policy owner; escalate at 60 days |
| Prompt version undocumented | MEDIUM | Flag in CI; require remediation before next deploy |

---

## AI Governance Reporting Template (Monthly)

```
AI GOVERNANCE REPORT — [Month YYYY]
=====================================
AUTONOMOUS ACTION VOLUME
  Total autonomous actions:   N
  By skill (top 5):           [skill: N, ...]
  Approval request rate:      X% (N of N triggered approval gate)

POLICY COMPLIANCE
  Violations this month:      N (Critical: N, High: N, Medium: N)
  Violations resolved:        N
  Open violations:            N

MODEL USAGE AUDIT
  Models used:                [model: N calls]
  Unauthorized model calls:   N (target: 0)
  Avg cost per workflow:      $X

PROMPT GOVERNANCE
  Prompt versions in prod:    N
  Undocumented prompts:       N (target: 0)
  Prompt changes this month:  N (approved: N, blocked: N)

EU AI ACT LOGGING (Art. 12)
  High-risk system calls logged: N / N (100%)
  Log integrity verified:        Yes / No
  Log retention compliance:      X months (required: ≥ 12)

GOVERNANCE HEALTH
  Policies overdue for review: N (target: 0)
  Agent registry current:      Yes / No
  Action boundary last reviewed: YYYY-MM-DD
```

---

## Agent Registry

Every registered agent and skill must have an entry:

```yaml
agent:
  id: "<agent-id>"
  name: "<agent name>"
  type: "skill | specialist-agent"
  version: "x.y.z"
  registered_at: "YYYY-MM-DD"
  registered_by: "<operator>"
  permitted_actions: [Level 0, Level 1]  # maximum action level
  data_access:
    - category: "<data category>"
      permission: "read | read-write"
  model_access: [claude-sonnet-4-6, local-llama]
  output_review_required: true | false
  approval_authority: none | Level-2 | Level-3
  status: "active | suspended | deprecated"
  last_reviewed: "YYYY-MM-DD"
```