# Safety Classification Rules

Used by `core/local-security/SKILL.md` to classify proposed autonomous actions into
safety levels 0–4 and determine the approval gate required.

---

## Classification Algorithm

1. Match the proposed action against the signal tables below.
2. Use the highest-level match if multiple rules apply.
3. Apply modifier rules to adjust up or down by 1 level.
4. Apply override rules — these are non-negotiable regardless of modifiers.

---

## Level 0 — Safe (Auto-approve, log only)

| Action Signal | Examples |
|---|---|
| Read-only file access | `open(file, 'r')`, `cat`, `ls`, `find` |
| Read-only API call | `GET /resource`, `describe`, `list` |
| Local computation | data transformation, formatting, analysis with no external output |
| Memory packet read | Loading workflow state for context |
| Telemetry read | Reading metrics, logs, reports |

---

## Level 1 — Low Risk (Auto-approve, audit log)

| Action Signal | Examples |
|---|---|
| Local file write (non-secret) | Writing output to a local file in the project dir |
| Development branch push | `git push origin feature/*` |
| Draft creation | Creating a draft PR, draft email, draft document |
| Test execution | Running unit tests, integration tests in isolated env |
| Schema validation | Checking files against schemas without writing |
| Dry-run modes | Any action with `--dry-run`, `--plan`, or `--preview` flag |

---

## Level 2 — Medium Risk (Warn, auto-approve after 30s)

| Action Signal | Examples |
|---|---|
| Staging deployment | Push to staging/preview env |
| Non-production external write | Write to dev/test API endpoint |
| Webhook trigger | Non-production webhook call |
| Internal Slack message | Message to internal team channel (not customer-facing) |
| Package publish (pre-release) | npm publish with `--tag beta` |
| Local database write | SQLite, local Postgres write < 100 records |

---

## Level 3 — Requires Approval (Block until human approves)

| Action Signal | Examples |
|---|---|
| Production push | `git push origin main`, `git push origin master` |
| Container/artifact publish | `docker push`, `npm publish` (without beta tag), PyPI publish |
| Cloud infra apply | `terraform apply`, `aws cloudformation deploy`, `kubectl apply` |
| DNS change | Cloudflare, Route53, Namecheap record edit |
| Customer communication | Any email, SMS, or message to a real customer/user |
| Billing or subscription | Stripe plan change, payment trigger, invoice send |
| External API write (production) | POST/PUT/DELETE to production third-party API |
| Secret rotation | API key regeneration, certificate renewal |
| Bulk database write | > 100 records insert/update in production DB |
| Role or permission grant | IAM policy attach, user permission elevation |

---

## Level 4 — Blocked (Reject; escalate)

| Action Signal | Examples |
|---|---|
| Data deletion at scale | `DROP TABLE`, `DELETE FROM ... WHERE 1=1`, `rm -rf /data` |
| Access removal | Revoking all access for a user or service |
| Secret exposure | Writing a secret to a log, file, or external system |
| Unclassified action by unclaimed skill | Action not declared in requesting skill's capabilities |
| Regulatory boundary crossing | Processing PHI/PII without declared compliance context |
| Self-modification | Any attempt to modify own governance, approval, or logging logic |

---

## Modifier Rules

These adjust the base classification by ±1 level:

| Modifier | Effect | Condition |
|---|---|---|
| `--dry-run` or `--preview` flag confirmed | -1 level | Action explicitly in preview mode |
| Reversibility confirmed | -1 level | Action has a documented rollback procedure in memory packet |
| Production environment target | +1 level | Action targets a resource tagged `env: production` |
| Regulated data in scope | +1 level | Payload contains PII, PHI, financial, or secrets fields |
| Second failure on same action | +1 level | Action previously REJECTED and retried without changes |

---

## Override Rules (Non-Negotiable)

These rules cannot be adjusted by modifiers:

| Rule | Always Applied |
|---|---|
| Any secret detected in payload | Classify as Level 4 — BLOCKED |
| Self-modification of security/approval logic | Classify as Level 4 — BLOCKED |
| Action by unauthenticated/unregistered skill | Classify as Level 4 — BLOCKED |
| Regulatory data without compliance context | Classify as Level 4 — BLOCKED |

---

## Approval Timeout Rules

| Level | Timeout | On Timeout |
|---|---|---|
| 2 | 30 seconds | Auto-approve; log timeout event |
| 3 | 5 minutes | Re-emit approval request; escalate at 15 minutes |
| 4 | Never | No timeout; BLOCKED until operator resolves |