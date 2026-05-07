# Approval Policy

Used by `core/local-security/SKILL.md` to define who can approve what actions,
escalation paths, and timeout handling for approval workflows.

---

## Approver Roles

| Role | Can Approve | Cannot Approve |
|---|---|---|
| `operator` | Level 2, Level 3 standard actions | Level 4, regulatory actions |
| `admin` | Level 2, Level 3, Level 4 with documented justification | Self-modification actions |
| `automated` | Level 0, Level 1 only | Anything Level 2 or above |

---

## Action-Specific Approval Requirements

| Action Category | Approver Required | Justification Required |
|---|---|---|
| Production deployment | operator | Deployment ticket or PR reference |
| DNS/CDN change | operator | Change reason + rollback plan |
| Customer communication | operator | Message content reviewed |
| Billing change | admin | Business reason |
| Cloud infra provision | operator | Architecture approval reference |
| Cloud infra destroy | admin | Confirmed no live traffic |
| Secret rotation | operator | Rotation schedule or incident reference |
| Bulk data write | operator | Data migration plan |
| IAM permission grant | admin | Principle of least privilege justification |
| Data deletion | admin | Data retention policy confirmation |

---

## Approval Request Format

When Level 3 approval is required, emit:

```
═══════════════════════════════════════
APPROVAL REQUIRED
═══════════════════════════════════════
Reference:   SEC-YYYYMMDD-NNN
Skill:       [requesting-skill]
Action:      [description of the proposed action]
Target:      [system, file, endpoint, or resource]
Safety Level: 3 — requires-approval
Risk:        [what could go wrong if this is wrong]
Reversible:  [YES / NO — and how to reverse if yes]

To approve:  Reply APPROVE SEC-YYYYMMDD-NNN
To reject:   Reply REJECT SEC-YYYYMMDD-NNN [reason]
Timeout:     5 minutes (re-escalate at 15 minutes)
═══════════════════════════════════════
```

---

## Escalation Path

| Trigger | Escalation Action |
|---|---|
| No approval received within 5 minutes | Re-emit approval request to operator |
| No approval received within 15 minutes | Escalate to admin; halt related workflow |
| Level 4 action attempted | Immediate escalation to admin; alert log |
| Secret detected in payload | Immediate halt; admin alert; audit log |
| Approval request rejected 3 times | Block action permanently for this workflow; human review |
| Multiple concurrent Level 3 approvals pending | Serialize; present one at a time |

---

## Approval Audit Log Fields

Every approval decision is logged with:

| Field | Description |
|---|---|
| `reference_id` | SEC-YYYYMMDD-NNN |
| `action` | Description of the proposed action |
| `requesting_skill` | Skill that proposed the action |
| `safety_level` | 0–4 |
| `decision` | AUTO-APPROVED / APPROVED / REJECTED / BLOCKED |
| `approver` | Role (operator/admin/automated) |
| `timestamp` | ISO 8601 |
| `justification` | Reason provided (or "auto" for Level 0–1) |
| `action_executed` | true / false |

---

## Waiver Protocol

Operators may issue a standing waiver for specific action categories in controlled
environments (e.g., local development, staging). Waivers must:

1. Be declared in the workspace configuration (`waivers:` section)
2. Specify a maximum safety level exempted (typically Level 2)
3. Never exempt Level 4 actions or secrets-related actions
4. Be time-bounded (expire after 30 days by default)
5. Be logged in the audit log with the issuing admin's reference

Standing waivers do not disable audit logging — they only skip the approval prompt.