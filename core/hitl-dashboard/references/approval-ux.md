# Approval UX

Used by `core/hitl-dashboard/SKILL.md` to define the approval request format,
queue management rules, CLI interaction patterns, and escalation flows.

---

## Approval Request Format

When an action requires operator approval, emit this record to the approval queue:

```yaml
approval_request:
  id: "APR-YYYYMMDD-NNN"
  action_id: "ACT-YYYYMMDD-NNN"       # links to explainability record
  safety_level: 2 | 3                  # level that triggered approval requirement
  summary: "<one sentence: what, where, impact>"
  requested_by: "<skill or agent>"
  requested_at: "YYYY-MM-DDThh:mm:ssZ"
  expires_at: "YYYY-MM-DDThh:mm:ssZ"   # computed from policy
  escalate_at: "YYYY-MM-DDThh:mm:ssZ"  # computed from policy
  approver_required: "operator | admin" # from approval-policy.md
  status: "pending | approved | rejected | escalated | expired"
  resolution:
    decided_by: "<null or user>"
    decided_at: "<null or timestamp>"
    decision: "<null | approved | rejected>"
    reason: "<null or text>"
```

---

## Approval Expiry Policy

| Safety Level | Approval Window | Auto-Escalate At | Auto-Block At |
|---|---|---|---|
| Level 2 | 24h | — | 24h (block action) |
| Level 3 | 4h | 4h (escalate to admin) | 24h (block action) |

Expired unapproved actions are **not** auto-executed. They are blocked and logged.
The initiating skill must re-request approval for a new execution window.

---

## CLI Interaction Patterns

### Approve an Action

```bash
$ apotheon approve APR-20260506-001

Approval Request: APR-20260506-001
Action: Deploy apotheon-api v1.4.2 to production (AWS ECS us-east-1)
Safety Level: L3
Requested by: cloud-deployment skill
Expires: 2026-05-06 18:00:00 UTC (3h 22m remaining)

Risk: Production service update. ~30s rolling restart. Rollback: automatic if
      health check fails; manual via `apotheon deploy --rollback` if needed.

Approve? [y/N]: y
✓ Approved. Deployment initiated. Track: apotheon workflows --filter running
```

### Reject an Action

```bash
$ apotheon reject APR-20260506-001 --reason "Timing conflict with partner demo"

✓ Rejected. Reason logged. Skill notified.
```

### View Explainability Record

```bash
$ apotheon explain ACT-20260506-042

─── Explainability Record: ACT-20260506-042 ───────────────────────────
Action:  Deploy apotheon-api v1.4.2 → production

WHY
  Trigger:    CI pipeline passed all tests on branch release/v1.4.2
  Objective:  Ship the "workflow retry" feature (customer-requested P0)
  Alternative: Delayed 24h — rejected (feature is blocking 3 enterprise accounts)

WHAT CHANGES
  Modified:   AWS ECS service apotheon-api (us-east-1)
  Before:     v1.4.1 running (2 tasks healthy)
  After:      v1.4.2 (rolling deploy, zero downtime)
  Reversible: YES — rollback in < 60 seconds
  Rollback:   `apotheon deploy --rollback apotheon-api production`

DATA USED
  Sources:    CI test results, deployment-targets.md, memory packet
  Key facts:  All 142 tests passed; staging deploy validated 4h ago
  Confidence: 0.94
  Uncertainty: None flagged

RISK
  Level:      3 (production write)
  Risk:       Rolling restart may cause 30s latency spike during switch
  Blast:      API downtime affects all active users if health check fails
  Mitigations: maxUnavailable=0 (no capacity drop); auto-rollback on failure
────────────────────────────────────────────────────────────────────────
```

---

## Queue Management Rules

1. **Deduplication**: If an identical action is already pending approval, do not create a second request — return the existing `APR-*` ID
2. **Priority ordering**: Sort by (safety_level DESC, expires_at ASC, revenue_impact DESC)
3. **Batch grouping**: Actions from the same workflow within 5 minutes may be grouped into a single approval request (all-or-nothing)
4. **Context preservation**: Approval queue entries must include full explainability record — approver must never need to ask "why"
5. **Audit trail**: Every approve/reject is immutably logged with: user, timestamp, reason

---

## Escalation Flows

### Level-3 Escalation (4h timeout)

```
T+0:00  Approval request created → notification to primary operator
T+3:45  Reminder sent (15 min remaining)
T+4:00  No decision → escalate to admin; notify primary operator
T+4:00  Admin receives escalation with full context + urgency flag
T+24:00 No admin decision → action blocked; incident created (BLOCK-*)
```

### Admin Override

Admin can approve Level-3 actions that primary operator missed.
Admin can also **force-block** any pending action regardless of level.
Admin approvals require the same explainability record review.

### Waiver Protocol

For routine recurring actions (e.g., daily scheduled backup), an operator can issue a
standing waiver:

```yaml
waiver:
  id: "WAV-NNN"
  action_pattern: "<regex or exact action_type>"
  granted_by: "<admin>"
  granted_at: "YYYY-MM-DDThh:mm:ssZ"
  expires_at: "YYYY-MM-DDThh:mm:ssZ"
  max_executions_per_day: 5
  conditions: "<any constraints>"
```

Waivers expire; must be renewed. They do not eliminate logging — every execution still
generates an explainability record and audit log entry.

---

## Notification Templates

### Slack / Email Approval Request

```
[APOTHEON APPROVAL REQUIRED]
Action: <summary>
Safety Level: L<n>
Requested by: <skill>
Expires: <time remaining>

<risk statement — one sentence>

Approve: apotheon approve <id>
Explain: apotheon explain <action_id>
Dashboard: /dashboard/approvals/<id>
```

### Escalation Alert

```
[APOTHEON ESCALATION — L3 Approval Overdue]
Action: <summary>
Original request: <timestamp>
Expired: <time ago>
Now requires: Admin approval

Review: /dashboard/approvals/<id>
```