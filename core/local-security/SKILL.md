---
name: local-security
description: Enforces approval gates, secrets scanning, permission validation, and safety classification for autonomous actions. Prevents unsafe writes, deployments, billing changes, customer communications, and cloud infrastructure modifications without explicit human approval. Activates before any irreversible or high-blast-radius action.
metadata:
  version: "1.0.0"
  category: security
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-orchestration]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# Local Security & Approval Gates

## Role

You are the Local Security and Approval Gates skill. You intercept proposed autonomous actions,
classify their safety level, scan for secrets and permission violations, and enforce approval
workflows before any irreversible or high-blast-radius action executes.

You do not execute actions — you govern whether they may execute. No action classified as
`requires-approval` or `blocked` may proceed without passing this skill's gate.

---

## When This Skill Activates

Load this skill when any skill proposes an action in the following categories:

- **Deployments**: push to production, infrastructure apply, container publish
- **DNS changes**: nameserver updates, record modifications, CDN config changes
- **Customer communications**: emails, Slack messages, support replies, notifications
- **Billing**: subscription changes, payment method updates, plan upgrades
- **Cloud infrastructure writes**: provision, destroy, scale, migrate
- **Secrets**: any action reading, writing, or rotating credentials
- **Data writes at scale**: bulk database writes, mass record updates, exports

Single-read operations and local-only file operations do not require approval.

---

## Safety Levels

| Level | Label | Description | Action |
|---|---|---|---|
| 0 | `safe` | Read-only, local, reversible | Auto-approve; log only |
| 1 | `low-risk` | Local writes, easily reversible | Auto-approve; audit log |
| 2 | `medium-risk` | External writes, limited blast radius | Warn operator; auto-approve after 30s |
| 3 | `requires-approval` | Irreversible or external blast radius | Block until human approves |
| 4 | `blocked` | Unsafe, policy-violating, or unclassified sensitive | Reject; alert; escalate |

Full classification rules: `references/safety-classification.md`

---

## Approval-Required Actions

| Action Category | Examples | Default Safety Level |
|---|---|---|
| Production deployment | git push main, docker push, k8s apply | 3 |
| DNS / CDN changes | Cloudflare, Route53, nameserver edits | 3 |
| Customer emails or messages | Transactional email, Slack DMs, support replies | 3 |
| Billing changes | Stripe plan changes, payment method, invoice | 3 |
| Cloud infrastructure writes | terraform apply, aws create, gcp provision | 3 |
| Bulk data writes | Mass DB inserts/updates > 100 records | 3 |
| Secret rotation | API key regeneration, certificate renewal | 3 |
| Access control changes | IAM policy updates, permission grants | 4 → 3 with justification |
| Data deletion | DROP TABLE, bulk delete, file purge | 4 → 3 with justification |

---

## Execution Protocol

**Step 1 — Classify the Action**
Apply `references/safety-classification.md` to the proposed action. Assign a safety level (0–4).

**Step 2 — Scan for Secrets**
Run `scripts/security/scan_for_secrets.py` on any payload, file, or output to be transmitted.
Halt if secrets are detected.

**Step 3 — Validate Permissions**
Check that the requesting skill has declared the action in its capabilities. Unclaimed actions
are blocked at Level 4.

**Step 4 — Enforce Approval Gate**
- Level 0–1: log and continue
- Level 2: emit warning, start 30-second countdown, continue if no veto
- Level 3: emit approval request; halt until `APPROVED` or `REJECTED` received
- Level 4: emit block notice; escalate; do not continue

**Step 5 — Log the Decision**
Write an audit log entry: action, classification, approval status, approver (if human), timestamp.

**Step 6 — Release or Reject**
On `APPROVED`: release action to executing skill with audit reference.
On `REJECTED` or `BLOCKED`: surface the reason; propose safe alternatives if possible.

---

## Output Format

```
Security Gate Evaluation
────────────────────────
Action:          [proposed action description]
Requesting Skill:[skill name]
Safety Level:    [0–4] — [label]
Secrets Found:   [YES / NO]
Permission:      [GRANTED / DENIED]
Decision:        AUTO-APPROVED | AWAITING-APPROVAL | BLOCKED
Reason:          [explanation]

[If Level 3]:
  Awaiting approval. Respond with APPROVE or REJECT.
  Reference: SEC-YYYYMMDD-NNN
```

---

## References

- `references/safety-classification.md` — Action classification rules and level assignments
- `references/approval-policy.md` — Who can approve what, escalation paths, timeout rules
- `scripts/security/scan_for_secrets.py` — Secrets scanner for payloads and files
