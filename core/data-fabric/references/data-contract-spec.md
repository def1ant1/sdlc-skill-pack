# Data Contract Specification

## Overview

Complete data contract YAML format, quality threshold types, SLA fields, versioning,
producer/consumer registration protocol, and violation severity taxonomy.

---

## Contract YAML Format

```yaml
data_contract:
  # Identity
  contract_id: "DC-20260507-001234"       # Assigned on registration
  version: "1.2.0"                          # Semver; MAJOR on breaking schema change
  status: active                            # draft | active | suspended | terminated

  # Parties
  producer:
    id: "WF-ANALYTICS-001"
    name: "Analytics Pipeline"
    owner: "data-team@company.com"
    tier: standard

  consumer:
    id: "SKILL-FORECASTING"
    name: "forecasting skill"
    owner: "finance-team@company.com"

  # Data specification
  data:
    schema_id: "SCHEMA-REVENUE-EVENTS-V3"
    schema_version: "3.2.0"
    format: parquet                         # parquet | json | csv | avro
    transport: event-bus                    # event-bus | s3 | postgres | api
    topic_or_path: "revenue.events.daily"

  # Quality thresholds (SLA commitments from producer)
  quality:
    completeness:
      field: "transaction_id"
      threshold: 0.999                      # 99.9% non-null
      measurement: "fraction_non_null"
    accuracy:
      description: "Revenue amounts match source system within 0.01%"
      threshold: 0.9999
      measurement: "reconciliation_match_rate"
    uniqueness:
      field: "transaction_id"
      threshold: 1.0                        # No duplicates permitted
      measurement: "fraction_unique"
    freshness:
      max_delay_minutes: 15                 # Data must arrive within 15 min of source event
      measurement: "event_time_to_available_time"
    schema_compliance:
      threshold: 1.0                        # Zero schema violations permitted

  # SLA fields
  sla:
    availability_percent: 99.5              # Monthly uptime SLA
    grace_period_minutes: 5                 # Time before violation is formally recorded
    violation_notification_contacts:
      - "data-oncall@company.com"
      - "finance-team@company.com"
    escalation_after_minutes: 30            # Unresolved violation escalated after 30 min

  # Versioning
  schema_compatibility: backward            # backward | forward | full | none

  # Dates
  effective_date: "2026-03-01"
  expiry_date: "2027-03-01"               # null for perpetual
  review_date: "2026-09-01"

  # Audit
  created_at: "2026-03-01T10:00:00Z"
  created_by: "data-governance-team"
  last_modified_at: "2026-05-01T09:00:00Z"
```

---

## Quality Threshold Types

| Threshold Type | Description | Measurement Method | Unit |
|---|---|---|---|
| completeness | Non-null fraction of required fields | COUNT(non_null) / COUNT(*) | Fraction 0–1 |
| accuracy | Match rate against authoritative source | Reconciliation query | Fraction 0–1 |
| uniqueness | Fraction of records with unique key values | COUNT(DISTINCT key) / COUNT(*) | Fraction 0–1 |
| freshness | Maximum lag between source event and availability | event_time to available_time | Minutes |
| validity | Fraction conforming to business rules | Rule engine pass rate | Fraction 0–1 |
| schema_compliance | Fraction passing schema validation | Schema validator | Fraction 0–1 |
| volume | Expected record count range | COUNT(*) | Count range |

---

## SLA Violation Severity Taxonomy

| Severity | Condition | Response |
|---|---|---|
| WARNING | Threshold missed by < 10% for < grace_period | Log; no notification |
| MINOR | Threshold missed by < 10% for > grace_period | Notify producer contact |
| MAJOR | Threshold missed by 10–50% OR freshness > 2× max_delay | Notify all contacts; page producer on-call |
| CRITICAL | Threshold missed by > 50% OR data unavailable | Suspend consumer workflows; immediate escalation |
| BREACH | SLA availability target missed for calendar month | Formal breach record; SLA credit process triggered |

---

## Producer/Consumer Registration Protocol

### New Contract Registration

1. Author drafts contract YAML; submits to data-contract-management
2. Auto-validation: schema ID exists, threshold types are valid, parties registered
3. Notification sent to producer for acknowledgment (required within 5 business days)
4. On producer acknowledgment: contract status → `active`; monitoring begins
5. Consumer receives activation confirmation and starts consuming data

### Contract Amendment

1. Any party may propose an amendment
2. MINOR version bumps: notify other party; 7-day review window; auto-approve if no objection
3. MAJOR version bumps (breaking schema change): require explicit acknowledgment from consumer;
   30-day migration window; both parties must sign amendment

### Contract Termination

1. Either party may initiate termination with 30-day notice
2. During notice period: contract remains `active`; violations continue to be reported
3. On termination date: status → `terminated`; consumer workflows suspended
4. Termination record retained for 12 months for audit purposes