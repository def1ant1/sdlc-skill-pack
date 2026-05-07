# Semantic Reasoning Rules

## Overview

The semantic-layer applies inference rules to derive implicit relationships and validate
ontological constraints. Rules are evaluated at query time and during graph consistency checks.

---

## Inference Rules

### Rule SR-001: Transitive Employment Hierarchy

If `A REPORTS_TO B` and `B REPORTS_TO C`, then `A` is transitively subordinate to `C`.

**Application:** Organization chart traversal, delegation of authority, escalation path resolution.

```cypher
MATCH (a:Employee)-[:REPORTS_TO*1..]->(c:Employee)
RETURN a, c, length(path) AS depth
```

---

### Rule SR-002: Ownership Inheritance

If an `Organization` OWNS a `Service`, and an `Employee` EMPLOYS at that org with role `owner`,
then the Employee implicitly CO_OWNS the service for governance purposes.

**Application:** Incident ownership assignment, on-call routing, change approval authority.

---

### Rule SR-003: Customer Relationship Transitivity

If `Org A` is a CUSTOMER_OF `Org B`, and `Org B` is a SUBSIDIARY_OF `Org C`,
then `Org A` is implicitly a customer of `Org C` for consolidated reporting.

**Application:** ARR roll-up, consolidated customer health scoring, executive reporting.

---

### Rule SR-004: Decision Supersedes

If `Decision D2` SUPERSEDES `Decision D1`, then D1's constraints are no longer active.

**Application:** Constraint resolution — when querying active constraints for a domain, only
non-superseded decisions are returned.

---

### Rule SR-005: Incident Impact Propagation

If `Service A` DEPENDS_ON `Service B`, and an Incident affects B, then A is implicitly
at risk and receives a derived `potential_impact` flag.

**Application:** Blast radius calculation during incident triage.

---

## Temporal Reasoning Rules

### Rule TR-001: Current State Default

Unless a temporal window is specified, queries return entities where `valid_to IS NULL`
(i.e., currently valid records only).

---

### Rule TR-002: Point-in-Time Reconstruction

A query with `AS OF timestamp T` returns all entity states where:
`valid_from <= T AND (valid_to IS NULL OR valid_to > T)`

---

### Rule TR-003: Valid-Time Overlap Detection

Two valid-time intervals [A_from, A_to] and [B_from, B_to] overlap when:
`A_from < B_to AND B_from < A_to`

Used to detect conflicting policy periods, overlapping contract terms, or duplicate employment records.

---

## Probabilistic Relationship Scoring

Some relationships carry confidence weights rather than binary existence:

```yaml
relationship:
  type: "LIKELY_COMPETITOR_OF"
  from: "Org-A"
  to: "Org-B"
  confidence: 0.75
  evidence:
    - "Similar product category"
    - "Overlapping customer segment"
    - "Shared technology stack"
  derived: true  # not asserted; inferred by semantic-layer
```

Probabilistic relationships are used for:
- Competitive intelligence analysis
- Customer churn risk (associated with churning accounts)
- Technology risk propagation (shared vulnerable dependency)

**Confidence threshold for use in decisions:** ≥ 0.7 (configurable per use case)

---

## Constraint Catalog

| Constraint ID | Description | Severity |
|---|---|---|
| SC-001 | Employee must have exactly one primary department | ERROR |
| SC-002 | ActionItem must have exactly one assignee | ERROR |
| SC-003 | Decision must have at least one decided_by person | ERROR |
| SC-004 | Transaction amount must be non-zero and positive | ERROR |
| SC-005 | Contract must have a start_date ≤ end_date | ERROR |
| SC-006 | Budget fiscal_year must match organization fiscal calendar | WARN |
| SC-007 | Incident severity must be P0-P4 | ERROR |

Constraints are evaluated on every entity write. ERROR constraints block the write;
WARN constraints allow the write but emit a `graph.constraint_violation` event.

---

## Query Patterns

### Find all active constraints for a domain
```cypher
MATCH (p:Policy)-[:GOVERNS]->(d:Domain {name: $domain})
WHERE p.valid_to IS NULL AND NOT (p)-[:SUPERSEDED_BY]->()
RETURN p
```

### Compute blast radius of an incident
```cypher
MATCH (i:Incident {id: $incident_id})-[:AFFECTS]->(s:Service)
MATCH (s)<-[:DEPENDS_ON*1..5]-(downstream:Service)
RETURN DISTINCT downstream.name, length(path) AS dependency_depth
ORDER BY dependency_depth
```

### Customer 360 view
```cypher
MATCH (c:Customer {id: $customer_id})
OPTIONAL MATCH (c)-[:HAS_CONTRACT]->(ct:Contract)
OPTIONAL MATCH (c)-[:HAS_INCIDENT]->(i:Incident)
OPTIONAL MATCH (c)<-[:ASSIGNED_TO]-(csm:Employee)
RETURN c, collect(ct), collect(i), csm
```