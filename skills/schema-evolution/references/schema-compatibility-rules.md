# Schema Compatibility Rules

## Breaking vs. Non-Breaking Change Taxonomy

### Non-Breaking Changes (Backward Compatible)

These changes can be deployed without requiring consumer updates:

| Change Type | Example | Consumer Impact |
|---|---|---|
| Add optional field | New nullable column `discount_code` | Consumers that ignore it are unaffected |
| Relax constraint | Change `NOT NULL` to `NULLABLE` | More permissive; consumers still work |
| Expand enum values | Add new status value `PENDING_REVIEW` | Consumers may need to handle new value |
| Increase field size | VARCHAR(100) → VARCHAR(500) | Larger values allowed; no truncation |
| Add new table/topic | New `order_events` table | Consumers not yet subscribed are unaffected |
| Add index | New index on `customer_id` | Performance only; no data change |

### Breaking Changes (Require Migration)

These changes require consumer updates before the schema change goes live:

| Change Type | Example | Consumer Impact |
|---|---|---|
| Remove field | Drop column `legacy_id` | Consumers reading this field will break |
| Rename field | `user_id` → `customer_id` | All references must be updated |
| Change field type (narrowing) | BIGINT → INT | Data may truncate; query results may differ |
| Change field type (incompatible) | VARCHAR → TIMESTAMP | Existing data may fail to parse |
| Add required field | NOT NULL column with no default | Existing inserts will fail |
| Remove enum value | Remove status `ARCHIVED` | Consumers may receive/send invalid values |
| Change key structure | Composite key becomes single key | Joins and lookups break |
| Change partition key | Event-bus partition key field changes | Message ordering guarantees broken |

---

## Compatibility Window Policy

| Change Type | Minimum Notice Period | Consumer Response Required |
|---|---|---|
| Non-breaking | 7 days | Acknowledgment recommended (optional) |
| Breaking — additive (add required field) | 30 days | Consumer must update ingestion logic |
| Breaking — removal (drop field/table) | 60 days | Consumer must remove references |
| Breaking — rename | 45 days | Consumer must update field names; dual-write period provided |
| Emergency breaking change | 5 days (operator approval required) | Mandatory emergency acknowledgment |

**Dual-write period:** For rename changes, the schema evolution skill coordinates a
dual-write period where both old and new field names are populated for the duration of
the compatibility window, enabling consumers to migrate at their own pace.

---

## Migration Coordination Protocol

### Phase 1: Proposal and Impact Assessment

1. Producer submits schema change proposal to schema-evolution skill
2. Skill classifies change (breaking vs. non-breaking) using the taxonomy above
3. Lineage analysis identifies all downstream consumers with active data contracts
4. Producer is notified of the consumer list and required coordination steps

### Phase 2: Consumer Notification

1. All consumers receive a structured change notice:

```yaml
schema_change_notice:
  notice_id: "SCN-20260507-001"
  schema_id: "SCHEMA-ORDER-EVENTS-V3"
  change_type: breaking
  description: "Removing field 'legacy_order_id' which has been unused since 2025-01"
  breaking_fields: ["legacy_order_id"]
  effective_date: "2026-07-07"
  compatibility_window_days: 60
  migration_guide: "Remove references to legacy_order_id; use order_id instead"
  acknowledgment_required: true
  acknowledgment_deadline: "2026-05-21"
```

2. Consumers must acknowledge within the notice period
3. Unresponsive consumers are escalated after 50% of the compatibility window has elapsed

### Phase 3: Migration Execution

1. Producer enables dual-write (old + new schema) at compatibility window start
2. Consumers migrate their code during the compatibility window
3. Each consumer marks themselves as migrated in the contract registry
4. Schema-evolution skill tracks acknowledgment status for all consumers

### Phase 4: Compatibility Gate

Breaking changes are blocked from promotion until:
- All registered consumers have acknowledged AND marked as migrated, OR
- Operator explicitly overrides with documented justification for any non-migrated consumers

### Phase 5: Schema Promotion

1. Breaking change is applied to the schema registry
2. Dual-write period ends
3. `schema.evolved` event is published with change details
4. Data contract compliance checks are updated to validate against new schema version

---

## Consumer Acknowledgment Requirements

| Consumer Status | Required Action | Escalation If Not Done |
|---|---|---|
| Active consumer (has data contract) | Explicit acknowledgment + migration confirmation | After 50% of compatibility window |
| Suspended consumer | Acknowledgment only (migration on re-activation) | After 75% of compatibility window |
| Legacy consumer (no active contract) | Best-effort notification only | No escalation; documented |