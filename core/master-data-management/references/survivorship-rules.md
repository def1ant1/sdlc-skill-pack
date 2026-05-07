# Survivorship Rules Reference

## Overview

Defines the survivorship rule types, conflict resolution matrix, golden record merge
algorithm, and field-level survivorship overrides for the master-data-management skill.

---

## Survivorship Rule Types

### Rule 1: Most-Recent-Wins

**Description:** The value from the most recently updated source record is used for
the golden record field.

**When to use:** Fields that change frequently and where the latest value is most
authoritative (e.g., address, phone number, preference flags).

**Tie-breaking:** If two sources have the same update timestamp (within 1 second), use
source priority ranking.

```yaml
rule: most-recent-wins
field: "mailing_address"
source_update_timestamp_field: "updated_at"
tie_break: source_priority
```

---

### Rule 2: Most-Complete-Wins

**Description:** The value from the source record with the most populated fields is
used. Completeness is measured as the fraction of non-null required fields.

**When to use:** When data completeness varies significantly across sources and
completeness correlates with quality (e.g., contact records from CRM vs. event logs).

```yaml
rule: most-complete-wins
field: "company_name"
completeness_metric: "fraction_required_fields_populated"
required_fields: ["name", "address", "phone", "email"]
```

---

### Rule 3: Source-Priority-Wins

**Description:** A static priority ranking of sources is defined; the highest-priority
source with a non-null value wins.

**When to use:** When one source is known to be more authoritative regardless of
recency or completeness (e.g., HR system is always authoritative for employee name).

**Priority table (default — overridden per entity type):**

| Priority | Source Type | Rationale |
|---|---|---|
| 1 | ERP system | Financial system of record |
| 2 | CRM system | Customer system of record |
| 3 | HR system | Employee system of record |
| 4 | Marketing platform | Enrichment data |
| 5 | Event streams | Derived/behavioral data |
| 6 | Manual entry | Human-entered; lowest reliability |

```yaml
rule: source-priority-wins
field: "legal_entity_name"
priority_list: ["erp", "crm", "hr", "marketing", "events", "manual"]
```

---

### Rule 4: Consensus-Wins

**Description:** The value that appears in the majority of sources (> 50%) is used.
If no majority exists, fall back to source-priority-wins.

**When to use:** When multiple sources are of similar quality and consensus indicates
higher confidence (e.g., email address confirmed by CRM + email system + marketing).

**Minimum sources for consensus:** 3 (consensus is not applicable with < 3 sources).

```yaml
rule: consensus-wins
field: "email_address"
minimum_sources: 3
fallback_rule: source-priority-wins
```

---

## Conflict Resolution Matrix

| Entity Type | Field | Survivorship Rule | Notes |
|---|---|---|---|
| Customer | legal_name | source-priority-wins | ERP is authoritative |
| Customer | email | consensus-wins | Must match in ≥ 2 systems |
| Customer | phone | most-recent-wins | Changes frequently |
| Customer | address | most-recent-wins | Prefer most recent verified |
| Customer | industry | most-complete-wins | Enrichment adds detail |
| Employee | legal_name | source-priority-wins | HR system authoritative |
| Employee | role_title | most-recent-wins | Changes with org updates |
| Employee | department | source-priority-wins | HR system authoritative |
| Product | name | source-priority-wins | ERP is master catalog |
| Product | description | most-complete-wins | Marketing enriches |
| Product | price | most-recent-wins | Pricing system is freshest |

---

## Golden Record Merge Algorithm

```
FOR each entity cluster (group of matched records across sources):
    1. Initialize empty golden record
    2. FOR each field in the entity schema:
        a. Retrieve all non-null values from source records for this field
        b. If only one source has a value → use it
        c. If multiple sources have values:
            i. Look up survivorship rule for this entity_type × field combination
            ii. Apply the rule to select the surviving value
            iii. Record which source won and the rule applied
        d. If all sources are null → field remains null in golden record
    3. Set golden record metadata:
        - golden_record_id: assigned UUID
        - constituent_record_ids: list of all merged source record IDs
        - created_at: current timestamp
        - last_refreshed_at: current timestamp
        - version: incremented integer
    4. Write golden record to master data store
    5. Emit "golden_record.created" or "golden_record.updated" event
```

---

## Field-Level Survivorship Overrides

Specific fields may override the default rule for their entity type:

```yaml
field_overrides:
  - entity_type: Customer
    field: loyalty_tier
    rule: source-priority-wins
    priority_list: ["loyalty-platform", "crm"]
    rationale: "Loyalty platform is the system of record for tier status"

  - entity_type: Product
    field: compliance_status
    rule: source-priority-wins
    priority_list: ["compliance-system"]
    rationale: "Only compliance system tracks regulatory status"

  - entity_type: Employee
    field: active_status
    rule: most-recent-wins
    rationale: "Termination/re-hire events must propagate immediately"
```

---

## Survivorship Audit Record

Every survivorship decision is logged:

```yaml
survivorship_decision:
  golden_record_id: "GR-CUST-00012345"
  field: "email"
  rule_applied: "consensus-wins"
  surviving_value: "user@example.com"
  surviving_source: "crm"
  competing_values:
    - source: "crm"
      value: "user@example.com"
    - source: "marketing"
      value: "user@example.com"
    - source: "events"
      value: "old-email@example.com"
  consensus_count: 2
  total_sources: 3
  decision_timestamp: "2026-05-07T14:23:00Z"
```