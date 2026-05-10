---
name: erp-integration
description: Synchronizes SAP/Oracle financial data, automates procurement workflows, and extracts structured data from ERP systems via the enterprise-integration-hub.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['enterprise-integration-hub']

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

## Role

ERP system integration skill. Provides high-level operations on top of `enterprise-integration-hub`
for SAP and Oracle ERP systems: financial data sync (GL, cost centers, budgets), procurement
automation (PO creation, approval routing, vendor management), and structured data extraction
for analytics and compliance.

## Activation Triggers

- `cfo-agent` requests current actuals vs. budget data
- `compliance-agent` needs financial control evidence (transaction logs, approval audit trail)
- Procurement automation workflow requires PO creation or approval status
- Scheduled financial data sync cycle is due
- `enterprise-integration-hub` receives an ERP webhook event (invoice posted, PO approved)

## Execution Protocol

1. **Financial data pull**: Query ERP GL and cost center data:
   - Map platform canonical budget entity fields to SAP BAPI / Oracle API fields
   - Retrieve: actual spend by GL code, cost center, period
   - Transform to canonical `budget_actuals` schema
   - Cache results for 4 hours (financial data acceptable staleness window)

2. **Budget vs. actual**: Compute variance for each budget line:
   - `variance_usd = actual - budget`
   - `variance_pct = variance_usd / budget`
   - Flag lines with `|variance_pct| > 0.10` as requiring attention

3. **Procurement automation**: For PO creation requests:
   - Validate vendor is on the approved vendor list
   - Check budget availability for the cost center
   - Submit PO via ERP API with required fields (vendor, amount, GL code, approver)
   - Return PO number for tracking

4. **Evidence extraction**: For compliance requests, pull:
   - Transaction journal entries with approver audit trail
   - Segregation of duties evidence (different approvers for creation vs. approval)
   - Vendor payment history for SOX controls

## Output Format

```yaml
erp_result:
  operation: financials | procurement | evidence
  system: sap | oracle
  status: success | auth_failed | rate_limited | data_unavailable
  data: {}
  cache_hit: false
  audit_ref: "ERP-OPS-2026-xxxxx"
```

## Quality Gates

- Financial data must include source timestamp — never serve data without provenance
- PO creation requires budget availability check before submission

## References

- `references/` — ERP field mapping tables, procurement workflow spec, financial data schema
