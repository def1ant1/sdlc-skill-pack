# ERP Integration — Connector Specification

## Supported ERP Systems

| ERP | Integration Method | Auth | Data Access |
|-----|-------------------|------|-------------|
| SAP S/4HANA | OData v4 REST API | OAuth 2.0 (client credentials) | GL, AP, AR, Cost Centers, Projects |
| Oracle NetSuite | SuiteTalk REST API | OAuth 1.0a | GL, AP, AR, Projects, Inventory |
| Microsoft Dynamics 365 | Dataverse REST API | Azure AD / OAuth 2.0 | Finance, Supply Chain, HR |
| Sage Intacct | XML API (REST wrapper) | Session-based token | GL, AP, AR, Projects |

---

## Canonical Financial Data Schemas

### General Ledger Entry

```yaml
gl_entry:
  entry_id: "GL-2026-xxxxx"
  source_erp: sap | netsuite | dynamics365 | sage_intacct
  source_entry_id: "1234567"
  fiscal_year: 2026
  fiscal_period: 4           # Month 1–12
  posting_date: "2026-05-07"

  account:
    account_code: "6010"
    account_name: "Software Subscriptions"
    account_type: expense | revenue | asset | liability | equity
    cost_center: "CC-ENG-001"

  amounts:
    local_currency: USD
    debit: 12500.00
    credit: 0.00
    net: 12500.00
    functional_currency: USD
    functional_net: 12500.00

  description: "AWS compute — April 2026"
  reference_doc_id: "INV-AWS-2026-04"
  posted_by: "accounts-payable@example.com"
  synced_at: "2026-05-07T06:00:00Z"
```

### Budget vs. Actuals

```yaml
budget_actual:
  period: "2026-Q2"
  cost_center: "CC-ENG-001"
  account_code: "6010"
  account_name: "Software Subscriptions"

  budget_usd: 45000.00
  actuals_usd: 37500.00        # Through end of April
  forecast_remaining_usd: 8200.00
  projected_total_usd: 45700.00

  variance_usd: -700.00        # Negative = over budget
  variance_pct: -1.6
  status: on_track | at_risk | over_budget

  last_updated: "2026-05-07T06:00:00Z"
```

### Purchase Order

```yaml
purchase_order:
  po_id: "PO-2026-xxxxx"
  source_erp: sap
  source_po_id: "4500123456"

  vendor:
    vendor_id: "VEND-001"
    name: "Amazon Web Services"

  line_items:
    - line_num: 1
      description: "EC2 Compute Reserved Instances"
      quantity: 12           # months
      unit_price: 8500.00
      total_price: 102000.00
      gl_account: "6010"
      cost_center: "CC-ENG-001"

  totals:
    subtotal_usd: 102000.00
    tax_usd: 0.00
    total_usd: 102000.00

  status: draft | approved | partially_received | received | invoiced | closed
  approval_required_above_usd: 10000.00
  approved_by: "cfo-agent"
  approved_at: "2026-04-01T14:00:00Z"
```

---

## Sync Configuration

```yaml
erp_sync_config:
  erp: sap
  environment: production    # sandbox | production

  credentials:
    secret_name: "sap-oauth-credentials"  # Resolved from vault
    token_endpoint: "https://sap.example.com/oauth/token"

  sync_schedules:
    gl_entries:
      cadence: "0 6 * * *"     # Daily at 6 AM UTC
      lookback_days: 2         # Re-sync last 2 days for corrections
    budget_actuals:
      cadence: "0 7 1 * *"    # 1st of month at 7 AM UTC
    purchase_orders:
      cadence: "*/15 * * * *"  # Every 15 minutes (near-real-time)

  data_quality:
    validate_on_ingest: true
    reject_if:
      - "amount is null"
      - "account_code not in chart_of_accounts"
    quarantine_uri: "gs://apotheon-erp-quarantine/"

  rate_limits:
    max_requests_per_minute: 100
    retry_after_seconds: 60
    max_retries: 3
```

---

## ERP Event Subscriptions

Subscribe to ERP events via webhooks (where supported) for near-real-time updates:

| Event | ERP Support | Latency |
|-------|------------|---------|
| `po.approved` | SAP, Dynamics365 | < 30 seconds |
| `invoice.posted` | All | < 30 seconds |
| `budget.threshold_reached` | SAP, NetSuite | < 5 minutes |
| `payment.executed` | All | < 30 seconds |

Webhook validation uses HMAC-SHA256 signature on the payload body. Secret stored in vault under `erp-webhook-secrets`.

---

## CFO Agent Integration Points

The `cfo-agent` queries this connector for:

1. **Real-time budget status**: `GET /v1/erp/budget?period=2026-Q2&roll_up=true`
2. **Spend anomaly detection**: Compare actual vs. forecast by cost center
3. **PO approval workflow**: Receive approval requests > threshold via notification-orchestration
4. **Month-end close checklist**: Verify all GL entries posted before period close
5. **Board reporting**: Pull actuals for `executive-reporting` skill