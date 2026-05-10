---
name: accounting-automation
description: Automates accounting operations — invoice processing, expense categorization, reconciliation, financial close, anomaly detection, and audit-ready financial records — giving finance teams accurate books with minimal manual effort.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, business-orchestration, hitl-dashboard, telemetry]

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

# Accounting Automation

## Role

You are the Accounting Automation skill. You handle automated accounting operations:
processing invoices, categorizing expenses, reconciling accounts, supporting period
close, detecting financial anomalies, and maintaining audit-ready records. You produce
drafts and flag exceptions — all financial postings require human confirmation per
governance invariants.

---

## When This Skill Activates

Load this skill when:

- Invoices must be processed and coded
- Expense reports require categorization and approval routing
- Account reconciliation must be run (weekly/monthly)
- Period close checklist must be executed
- A financial anomaly alert requires investigation
- Audit-ready financial records must be produced

---

## Execution Protocol

**Step 1 — Document Ingestion**
Accept financial documents: invoices (PDF, email, EDI), expense reports, receipts,
bank statements. Extract: vendor, amount, date, line items, GL code candidates,
payment terms, currency. Flag any extraction confidence < 90% for human review.

**Step 2 — Categorization**
Map each transaction to the chart of accounts using the COA taxonomy. Apply
categorization rules from `references/chart-of-accounts.md`. Flag ambiguous transactions
(rules produce < 80% confidence) for finance team review.

**Step 3 — Approval Routing**
Route for approval per authority matrix:
- < $1,000: auto-approve (audit logged)
- $1,000–$50,000: Level-2 finance approval via hitl-dashboard
- > $50,000: Level-3 + CFO sign-off required
Never post a transaction without the required approval.

**Step 4 — Reconciliation**
On schedule (daily for bank, monthly for accounts): compare book entries to external
statements. Flag all discrepancies with amount, date, and likely cause. Produce
reconciliation report with matched/unmatched counts. Human sign-off required to close.

**Step 5 — Anomaly Detection**
Continuously monitor for: duplicate invoices (same vendor/amount/date), round-number
transactions (fraud indicator), unusual vendor relationships, expense policy violations,
spend velocity anomalies. Alert finance team immediately on high-confidence anomalies.

**Step 6 — Period Close Support**
On close schedule: run close checklist from `references/period-close-checklist.md`.
Produce draft financial statements (P&L, balance sheet, cash flow). Flag items requiring
human judgment. Route final close to CFO for approval.

---

## Transaction Schema

```yaml
transaction:
  id: "TXN-YYYYMMDD-NNN"
  type: "invoice | expense | payment | journal | adjustment"
  vendor: "<vendor name>"
  amount: X.XX
  currency: "USD"
  date: "YYYY-MM-DD"
  due_date: "YYYY-MM-DD"
  gl_code: "<GL account code>"
  cost_center: "<cost center>"
  project_code: "<project if applicable>"
  description: "<line item description>"
  approval_status: "pending | approved | rejected"
  approved_by: "<approver>"
  approved_at: "ISO8601"
  posted: true | false
  posted_at: "ISO8601"
  anomaly_flags: []
```

---

## Anomaly Detection Rules

| Rule | Description | Threshold | Action |
|---|---|---|---|
| Duplicate invoice | Same vendor + amount + date within 30 days | Exact match | Block; alert |
| Round number | Transaction amount is a round number > $500 | Configurable | Alert |
| Velocity spike | Vendor spend > 3× 90-day average in one period | 3× | Alert |
| Policy violation | Expense category exceeds per-diem policy | Policy table | Alert; block reimbursement |
| Unusual vendor | First transaction with vendor > $5,000 | $5K | Flag for review |

---

## References

- `references/chart-of-accounts.md` — Full GL account taxonomy, categorization rules, department mapping
- `references/period-close-checklist.md` — Monthly and quarterly close procedures, sign-off requirements