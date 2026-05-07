# Legal Hold Protocol Reference

## Hold Scope Definition Template

```yaml
legal_hold:
  hold_id: "LH-20260507-001"
  matter_name: "Contract Dispute — Vendor XYZ"
  matter_type: "litigation"  # litigation | regulatory | internal_investigation | audit

  scope:
    data_types:
      - emails
      - contracts
      - workflow_execution_logs
      - financial_transactions
    date_range:
      start: "2024-01-01"
      end: "2026-05-07"  # Hold date (open-ended holds use null for end)
    keywords:
      - "Vendor XYZ"
      - "Project Helios"
      - "contract modification"
    custodians:
      - type: human
        id: "EMP-001234"
        name: "Jane Smith"
        role: "VP of Operations"
      - type: system
        id: "WF-ANALYTICS-001"
        name: "Analytics Pipeline"
        scope: "All outputs tagged with project-helios"

  hold_authority:
    placed_by: "General Counsel"
    placing_counsel_id: "COUNSEL-007"
    legal_basis: "Litigation hold — reasonable anticipation of litigation (US standard)"
    placing_date: "2026-05-07"

  notifications:
    acknowledgment_required: true
    acknowledgment_deadline_days: 3
    escalation_after_days: 5  # If human custodian has not acknowledged
    reminder_interval_days: 30

  status: ACTIVE  # ACTIVE | RELEASED | PARTIAL_RELEASE
```

---

## Custodian Notification Workflow

### Initial Hold Notice

Issued within 24 hours of hold placement to all human custodians:

```
Subject: Legal Hold Notice — [Matter Name] — [Hold ID]

This notice instructs you to preserve all data within the scope defined below.
You must NOT delete, destroy, modify, or move any documents or communications
within this scope until further notice.

Hold ID: [LH-...]
Matter: [Matter Name]
Scope: [Summary of data types and date range]
Effective Date: [Date]

Please acknowledge receipt of this notice within 3 business days by clicking
the acknowledgment link below.

If you have questions, contact Legal at [contact].

[ACKNOWLEDGE THIS NOTICE]
```

### Acknowledgment Tracking

```yaml
acknowledgment_record:
  hold_id: "LH-20260507-001"
  custodian_id: "EMP-001234"
  notice_sent_at: "2026-05-07T10:00:00Z"
  acknowledgment_status: acknowledged  # acknowledged | pending | escalated
  acknowledged_at: "2026-05-07T14:30:00Z"
  method: "email_link"
```

### Escalation Protocol

| Status | Action | Timing |
|---|---|---|
| pending after 3 days | Resend notice; escalate to direct manager | Day 4 |
| pending after 5 days | Escalate to Legal; direct contact required | Day 6 |
| pending after 7 days | Declare non-compliance; document for record | Day 8 |

---

## Retention Policy Override

Legal holds override all automated retention and deletion policies:

1. **Identify scope:** Run query against data fabric to enumerate all records matching hold scope
2. **Apply exemption flag:** Set `legal_hold_id: LH-XXXXXX` on all records within scope
3. **Block deletion:** Any scheduled deletion of records with an active `legal_hold_id` is blocked
4. **Block data redaction:** PII redaction is blocked for records under active holds
5. **Block archival eviction:** Archival tier eviction is blocked for held records

**Exception:** Records under hold may still be accessed for legitimate business purposes;
the hold prevents deletion and modification, not read access.

---

## Chain-of-Custody Requirements

For records that are collected and preserved (beyond just flagging in place):

```yaml
chain_of_custody_record:
  hold_id: "LH-20260507-001"
  record_id: "DOC-00012345"
  collection_event:
    collected_at: "2026-05-07T15:00:00Z"
    collected_by: "hold-management-agent"
    source_location: "data-fabric://contracts/DOC-00012345"
    collection_method: "automated_bulk_collection"
  preservation:
    storage_location: "s3://legal-holds-archive/LH-20260507-001/DOC-00012345"
    integrity_hash: "sha256:abc123..."
    hash_verified_at: "2026-05-07T15:01:00Z"
  access_log: []  # Appended each time record is accessed during hold
```

---

## Hold Release Protocol

1. Legal counsel issues release instruction with explicit hold ID
2. Verify all reasons for hold are resolved (case settled, investigation closed)
3. Remove `legal_hold_id` flag from all records within scope
4. Restore normal retention policies (records now subject to standard deletion schedules)
5. For records that would have been deleted during the hold period: apply deletion immediately
6. For PII subject to erasure requests received during hold: process erasure now
7. Generate chain-of-custody report for the matter file
8. Set hold status → RELEASED; retain hold record for 7 years

```yaml
release_event:
  hold_id: "LH-20260507-001"
  released_by: "COUNSEL-007"
  released_at: "2026-11-15T09:00:00Z"
  release_reason: "Matter resolved by settlement agreement dated 2026-11-10"
  records_released: 1247
  custodians_notified: 3
  chain_of_custody_report_id: "COC-LH-20260507-001-FINAL"
```