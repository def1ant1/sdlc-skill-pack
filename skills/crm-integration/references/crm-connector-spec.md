# CRM Integration — Connector Specification

## Supported CRM Systems

| CRM | Integration Method | Auth | Key Objects |
|-----|-------------------|------|-------------|
| Salesforce | REST API + Streaming API | OAuth 2.0 (JWT bearer) | Account, Contact, Opportunity, Lead, Case |
| HubSpot | CRM API v3 | OAuth 2.0 / Private App token | Contact, Company, Deal, Ticket |
| Dynamics 365 Sales | Dataverse REST API | Azure AD / OAuth 2.0 | Account, Contact, Opportunity, Lead |
| Pipedrive | REST API v1 | API key / OAuth 2.0 | Person, Organization, Deal, Activity |

---

## Canonical CRM Data Schemas

### Account

```yaml
crm_account:
  account_id: "CRM-ACCT-2026-xxxxx"
  source_crm: salesforce
  source_id: "001Dn000001xxxxx"

  name: "Acme Corporation"
  type: prospect | customer | partner | competitor
  industry: "Financial Services"
  employee_count: 12000
  annual_revenue_usd: 4_200_000_000

  primary_contact:
    contact_id: "CRM-CON-2026-xxxxx"
    name: "Alice Chen"
    title: "VP of Engineering"
    email: "alice.chen@acme.com"

  owner: "revenue-operations-agent"
  health_score: 82       # [0, 100]; computed from engagement signals
  customer_since: "2024-03-01"
  contract_renewal_date: "2027-02-28"
  arr_usd: 240000.00

  tags: [enterprise, strategic, at-renewal]
  last_activity_at: "2026-05-05T14:00:00Z"
  synced_at: "2026-05-07T06:00:00Z"
```

### Opportunity

```yaml
crm_opportunity:
  opportunity_id: "CRM-OPP-2026-xxxxx"
  source_crm: salesforce
  source_id: "006Dn000002xxxxx"
  account_id: "CRM-ACCT-2026-xxxxx"

  name: "Acme — Apotheon Enterprise Platform"
  stage: prospecting | qualification | proposal | negotiation | closed_won | closed_lost
  amount_usd: 480000.00
  arr_usd: 480000.00       # For SaaS deals
  close_date: "2026-06-30"
  probability_pct: 65

  products:
    - name: "Apotheon Enterprise OS"
      quantity: 1
      unit_price_usd: 480000.00

  next_steps: "Legal review of MSA redlines; schedule exec alignment call"
  owner: "revenue-operations-agent"
  primary_contact_id: "CRM-CON-2026-xxxxx"
  competitor: "OpenAI Enterprise"

  last_activity_at: "2026-05-06T10:00:00Z"
  synced_at: "2026-05-07T06:00:00Z"
```

### Pipeline Summary (Aggregated)

```yaml
pipeline_summary:
  generated_at: "2026-05-07T06:00:00Z"
  period_close: "2026-06-30"   # Current quarter close date

  stages:
    - stage: qualification
      count: 8
      total_arr_usd: 1_920_000
      weighted_arr_usd: 576_000   # total × avg_probability (30%)

    - stage: proposal
      count: 5
      total_arr_usd: 2_400_000
      weighted_arr_usd: 1_200_000

    - stage: negotiation
      count: 3
      total_arr_usd: 1_440_000
      weighted_arr_usd: 1_152_000

  totals:
    open_pipeline_arr_usd: 5_760_000
    weighted_pipeline_arr_usd: 2_928_000
    closed_won_qtd_arr_usd: 720_000
    quota_usd: 4_000_000
    attainment_pct: 18.0         # Closed won / quota
    forecast_pct: 91.2           # (closed won + weighted pipeline) / quota
```

---

## Sync Configuration

```yaml
crm_sync_config:
  crm: salesforce
  environment: production

  credentials:
    secret_name: "salesforce-jwt-credentials"

  sync_schedules:
    accounts:
      cadence: "*/30 * * * *"    # Every 30 minutes
    opportunities:
      cadence: "*/5 * * * *"     # Every 5 minutes (high-value, time-sensitive)
    contacts:
      cadence: "0 * * * *"       # Hourly

  streaming_events:
    enabled: true
    topics:
      - /data/OpportunityChangeEvent
      - /data/AccountChangeEvent
    latency: "< 10 seconds"

  field_mapping:
    # Salesforce field → Canonical field
    "Amount": "amount_usd"
    "CloseDate": "close_date"
    "StageName": "stage"
    "Probability": "probability_pct"
```

---

## Revenue Operations Agent Integration Points

The `revenue-operations-agent` uses this connector for:

1. **Pipeline review**: Weekly summary of stage distribution and at-risk deals
2. **Forecast generation**: Weighted pipeline + closed-won vs. quota
3. **Deal health scoring**: Composite of last-activity age, stage velocity, and engagement score
4. **Renewal risk detection**: Accounts with low health score approaching renewal date
5. **Executive reporting**: Q-over-Q ARR growth, win/loss ratio, average deal size

---

## Deal Health Score Components

| Component | Weight | Source |
|-----------|--------|--------|
| Last activity recency | 30% | `last_activity_at` age decay |
| Stage velocity | 25% | Days in current stage vs. average |
| Engagement score | 20% | Email/meeting frequency with account |
| Contact coverage | 15% | Number of contacts engaged vs. buying committee size |
| Competitive threat | 10% | Known competitor present in deal |

Score range: [0, 100]. Below 40 → flag as at-risk.