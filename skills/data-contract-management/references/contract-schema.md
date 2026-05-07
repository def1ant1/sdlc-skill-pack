# Data Contract Schema Reference

## Full Contract YAML Format

See `core/data-fabric/references/data-contract-spec.md` for the complete contract YAML
specification. This document covers the domain skill-specific extensions and operational
details.

---

## Quality Threshold Configuration

### Threshold Types and Measurement Methods

| Threshold Type | Measurement SQL Pattern | Pass Condition |
|---|---|---|
| completeness | `COUNT(field) / COUNT(*) >= threshold` | Fraction of non-null values |
| uniqueness | `COUNT(DISTINCT field) / COUNT(*) >= threshold` | Fraction of unique values |
| accuracy | `SUM(CASE WHEN reconciled THEN 1 END) / COUNT(*)` | Reconciliation pass rate |
| freshness | `TIMESTAMPDIFF(MINUTE, MAX(event_time), NOW()) <= threshold` | Max lag in minutes |
| validity | `COUNT(CASE WHEN passes_rule THEN 1 END) / COUNT(*)` | Business rule pass rate |
| volume | `COUNT(*) BETWEEN min_count AND max_count` | Record count range |
| schema_compliance | `COUNT(valid_records) / COUNT(*)` | Schema validation pass rate |

### Threshold Configuration Example

```yaml
quality:
  completeness:
    field: "customer_id"
    threshold: 0.999
    measurement: "fraction_non_null"
    check_interval_minutes: 15
    grace_period_minutes: 5

  uniqueness:
    field: "order_id"
    threshold: 1.0
    measurement: "fraction_unique"
    check_interval_minutes: 15
    grace_period_minutes: 0  # No grace for uniqueness violations

  freshness:
    max_delay_minutes: 30
    measurement: "source_to_available_lag_p95"
    check_interval_minutes: 5
    grace_period_minutes: 5

  volume:
    min_records_per_hour: 100
    max_records_per_hour: 50000
    check_interval_minutes: 60
    grace_period_minutes: 15
```

---

## SLA Violation Grace Periods

Grace periods prevent alert fatigue from transient spikes:

| Violation Type | Default Grace Period | Rationale |
|---|---|---|
| Freshness breach | 5 minutes | Network/processing delays |
| Completeness breach | 5 minutes | Late-arriving records |
| Volume below minimum | 15 minutes | Business cycle low periods |
| Volume above maximum | 5 minutes | Traffic spike |
| Uniqueness breach | 0 minutes | Duplicates are immediate risk |
| Schema violation | 0 minutes | Parser/contract break |

---

## Violation Severity and Response Matrix

| Threshold Missed By | Duration | Severity | Response |
|---|---|---|---|
| < 5% | < grace period | INFO | Log only |
| < 5% | > grace period | WARNING | Notify producer contact |
| 5–20% | Any | MINOR | Page producer on-call |
| 20–50% | Any | MAJOR | Suspend affected consumer workflows; alert all parties |
| > 50% | Any | CRITICAL | Suspend all consumers; incident declared; immediate escalation |
| Total unavailability | Any | CRITICAL | Same as > 50% |

---

## Contract Compliance Monitoring Schema

```yaml
compliance_record:
  contract_id: "DC-20260507-001234"
  check_timestamp: "2026-05-07T14:23:00Z"
  check_interval_minutes: 15

  threshold_results:
    - threshold_type: completeness
      field: customer_id
      measured_value: 0.9998
      threshold: 0.999
      status: PASS

    - threshold_type: freshness
      max_delay_minutes: 30
      measured_p95_minutes: 12.3
      status: PASS

    - threshold_type: uniqueness
      field: order_id
      measured_value: 0.9999
      threshold: 1.0
      status: FAIL
      violation_severity: CRITICAL
      affected_records: 42

  overall_status: VIOLATION
  active_violations: [uniqueness_order_id]
  escalation_triggered: true
  escalation_id: "ESC-20260507-009"
```

---

## Contract Lifecycle State Machine

```
[draft] → [pending_acknowledgment] → [active] → [suspended] → [terminated]
                                          ↑______________|
                                       (reactivation after resolution)
```

| State | Monitoring | Violations Reported | Consumer Workflows |
|---|---|---|---|
| draft | No | No | Not applicable |
| pending_acknowledgment | No | No | Not applicable |
| active | Yes | Yes | Running normally |
| suspended | Yes (to detect recovery) | Yes | Suspended by MDM |
| terminated | No | No | Permanently suspended |

**Suspension trigger:** CRITICAL violation not resolved within `sla.escalation_after_minutes`

**Reactivation trigger:** Operator confirms root cause resolved; all thresholds pass for
2 consecutive check intervals