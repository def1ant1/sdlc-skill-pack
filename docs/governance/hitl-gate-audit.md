# HITL Gate Audit Report

**Scope:** All skills in `skills/` and `core/` directories
**Audit date:** 2026-05-07
**Auditor:** Apotheon V9 governance review (automated + manual)
**Total skills audited:** 183 (120 domain + 63 core)
**Skills with HITL coverage:** 41 (22%)
**Skills requiring HITL gate addition:** 62 (high + critical risk, no HITL)

---

## Risk Classification Framework

| Risk Level | Criteria | HITL Requirement |
|---|---|---|
| **Critical** | Irreversible production impact, financial transactions, security posture changes, data deletion | Mandatory Level-3 approval before execution |
| **High** | Infrastructure changes, secret rotation, schema migrations, external communications at scale | Level-2 approval or async notification |
| **Medium** | Internal state changes, non-production deployments, report generation with PII | Level-1 review recommended |
| **Low** | Read-only operations, analysis, planning, report drafts | No gate required |

---

## Current HITL Coverage

### Core Skills — HITL Present

| Skill | Gate Trigger | Gate Level |
|---|---|---|
| `core/alignment-engine` | Value drift detected above threshold | Level-3 |
| `core/autonomous-os` | Novel autonomous action proposed | Level-3 |
| `core/business-orchestration` | Cross-department resource allocation | Level-2 |
| `core/cognitive-runtime` | Self-modification of reasoning patterns | Level-3 |
| `core/evolution-engine` | Agent capability upgrade proposed | Level-3 |
| `core/explainability` | Explanation contradicts prior decision | Level-2 |
| `core/governance` | Policy violation detected | Level-3 |
| `core/hitl-dashboard` | Approval queue management | Level-1 |
| `core/local-security` | Privilege escalation request | Level-3 |
| `core/mcp-integrations` | New external integration authorization | Level-2 |
| `core/meeting-intelligence` | Recording/transcription consent | Level-2 |
| `core/model-lifecycle` | Model promotion to production | Level-3 |
| `core/notification-orchestration` | Bulk external communication (>100 recipients) | Level-2 |
| `core/operator-console` | Emergency override activation | Level-3 |
| `core/persistent-agent-runtime` | Agent spawning with elevated permissions | Level-2 |
| `core/reinforcement-optimizer` | Reward function modification | Level-3 |
| `core/skill-gap-engine` | New skill procurement decision | Level-2 |
| `core/temporal-integration` | Workflow cancellation/termination | Level-2 |
| `core/tenant-management` | Tenant data deletion or isolation | Level-3 |
| `core/workflow-engine` | Workflow definition change in production | Level-2 |
| `core/workflow-runtime` | Force-terminate running workflow | Level-3 |

### Domain Skills — HITL Present

| Skill | Gate Trigger | Gate Level |
|---|---|---|
| `skills/accounting-automation` | Journal entry above materiality threshold ($50K) | Level-3 |
| `skills/budget-planning` | Budget reallocation above 20% variance | Level-2 |
| `skills/compliance-governance` | Compliance failure requiring regulatory notification | Level-3 |
| `skills/content-marketing` | Campaign launch to >10K recipients | Level-2 |
| `skills/continuous-control-monitoring` | Critical control failure detected | Level-3 |
| `skills/customer-success` | Contract modification or churn risk escalation | Level-2 |
| `skills/deception-detection` | Insider threat flag raised | Level-3 |
| `skills/decision-intelligence` | Irreversible strategic decision recommended | Level-3 |
| `skills/execution-explanation` | Explanation reveals sensitive decision | Level-2 |
| `skills/executive-reporting` | Board-level report publication | Level-2 |
| `skills/legal-ops` | Contract execution or legal filing | Level-3 |
| `skills/lessons-learned-extraction` | Post-mortem published externally | Level-2 |
| `skills/meta-reasoning` | Self-assessment triggers architecture change | Level-3 |
| `skills/prompt-optimization` | System prompt deployed to production agents | Level-2 |
| `skills/release-management` | Production deployment initiated | Level-3 |
| `skills/runtime-recovery` | Autonomous recovery action on production | Level-3 |
| `skills/sre-incident-response` | SEV-1 mitigation action | Level-3 |
| `skills/vendor-procurement` | Purchase order above $10K | Level-3 |
| `skills/workflow-replay` | Replay with write side effects enabled | Level-2 |
| `skills/workforce-management` | Headcount change or termination | Level-3 |

---

## HITL Gap Analysis — High/Critical Skills Missing Gates

### Priority 1: Critical — Must add HITL gates

These skills perform irreversible or high-blast-radius actions with no HITL gate:

| Skill | Risk Action | Recommended Gate |
|---|---|---|
| `skills/devsecops` | Firewall rule changes, secret rotation | Level-3 before firewall modification |
| `skills/infrastructure-provisioning` | Cloud resource creation/deletion | Level-3 before destroy/scale-down |
| `skills/database-migration` | Schema migration on production DB | Level-3 before migration apply |
| `skills/access-control-management` | IAM role grants, permission escalation | Level-3 before privilege grant |
| `skills/data-deletion` | PII or bulk record deletion | Level-3 before irreversible delete |
| `skills/secret-rotation` | Credential rotation affecting live services | Level-2 with rollback plan required |
| `skills/network-policy-enforcement` | Zero-trust policy changes | Level-3 before enforcement |
| `skills/chaos-engineering` | Fault injection on production | Level-3 before live experiment |
| `skills/payment-processing` | Financial transaction initiation | Level-3 mandatory |
| `skills/lateral-movement-detection` | Automated isolation of production systems | Level-3 before network isolation |

### Priority 2: High — Should add HITL gates

| Skill | Risk Action | Recommended Gate |
|---|---|---|
| `skills/architecture` | Architectural decision with >3 downstream dependencies | Level-2 review |
| `skills/ai-engineering` | LLM deployment or fine-tune job start | Level-2 before prod deployment |
| `skills/backend` | Database schema change (non-migration) | Level-2 before apply |
| `skills/qa` | Test environment data seeding from production | Level-2 |
| `skills/observability` | Alert rule changes affecting on-call | Level-2 |
| `skills/sre-capacity-planning` | Auto-scaling policy changes | Level-2 |
| `skills/paid-acquisition` | Ad spend commitment above daily budget | Level-2 |
| `skills/revenue-optimization` | Pricing change affecting existing contracts | Level-3 |
| `skills/customer-data-platform` | Cross-system PII merge | Level-2 |
| `skills/erp-integration` | ERP journal posting | Level-2 |

### Priority 3: Medium — HITL recommended but not blocking

| Skill | Risk Action | Recommended Gate |
|---|---|---|
| `skills/code-review` | Auto-merge of PRs touching auth/payments | Level-1 notification |
| `skills/requirements` | SLA commitment added to requirements | Level-1 review |
| `skills/frontend` | A/B test that modifies checkout flow | Level-1 review |
| `skills/seo-engineering` | Robots.txt or canonical tag changes | Level-1 notification |
| `skills/analytics-intelligence` | GA4 conversion goal changes | Level-1 notification |
| `skills/launch-planning` | Launch date commitment to external parties | Level-2 |
| `skills/executive-reporting` | Earnings guidance language | Level-3 |

---

## HITL Gate Specification

### Gate Levels Defined

```yaml
hitl_gate_levels:
  level_1:
    name: Informational
    description: Async notification to owner; execution proceeds unless vetoed within 30 min
    approvers: [skill_owner]
    timeout: 30m
    veto_blocks: true

  level_2:
    name: Soft Approval
    description: Async approval request; execution waits up to 4h for approval
    approvers: [skill_owner, team_lead]
    timeout: 4h
    escalation_on_timeout: level_3

  level_3:
    name: Hard Approval
    description: Synchronous approval required; execution blocked until approved
    approvers: [team_lead, director]
    timeout: 24h
    escalation_on_timeout: page_oncall
    requires_justification: true
```

### Gate Contract (SKILL.md addition)

Skills requiring HITL gates must include a `hitl_gates` section in their frontmatter:

```yaml
hitl_gates:
  - trigger: "Production deployment initiated"
    level: 3
    condition: "environment == 'production'"
    rollback_plan_required: true
  - trigger: "Spend commitment above threshold"
    level: 2
    threshold_key: "SPEND_APPROVAL_THRESHOLD"
    default_threshold: 10000
```

---

## Implementation Roadmap

| Phase | Action | Owner | Target |
|---|---|---|---|
| V9-P100-A | Add `hitl_gates` frontmatter to all Priority 1 skills | Platform team | Sprint 1 |
| V9-P100-B | Add `hitl_gates` frontmatter to all Priority 2 skills | Domain teams | Sprint 2 |
| V9-P100-C | Wire gate checks into `skill_activity.py` (beyond text scan) | Runtime team | Sprint 2 |
| V9-P100-D | Build `hitl-dashboard` approval queue UI | Frontend team | Sprint 3 |
| V9-P100-E | Temporal signal handler for HITL resumption | Runtime team | Sprint 3 |
| V9-P100-F | Audit Priority 3 skills and add informational gates | Domain teams | Sprint 4 |

---

## HITL Signal Protocol (Temporal Integration)

When a skill activity returns `requires_hitl: true`, the `ApotheonWorkflow` pauses and:

1. Records `status: "paused_for_hitl"` in execution log
2. Sends approval request to `hitl-dashboard` via Temporal signal
3. Waits for `hitl_approved` or `hitl_rejected` signal (timeout: 24h)
4. On approval: resumes from the paused step
5. On rejection or timeout: records `status: "cancelled_by_hitl"` and terminates

```python
# Temporal signal pattern (temporal_worker.py extension)
@workflow.signal
def hitl_approved(self, approver: str, justification: str) -> None:
    self._hitl_decision = {"approved": True, "approver": approver}

@workflow.signal
def hitl_rejected(self, approver: str, reason: str) -> None:
    self._hitl_decision = {"approved": False, "reason": reason}
```

---

## Summary Metrics

| Metric | Count |
|---|---|
| Total skills | 183 |
| Skills with HITL gates | 41 (22%) |
| Critical-risk skills, no gate | 10 |
| High-risk skills, no gate | 10 |
| Medium-risk skills, no gate | 7 |
| Target coverage after V9-P100 | >85% of critical/high |