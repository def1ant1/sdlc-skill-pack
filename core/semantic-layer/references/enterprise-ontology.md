# Enterprise Ontology

## Overview

The enterprise ontology defines the canonical entity types and relationship vocabulary for
the Apotheon semantic layer. All skills and agents use this ontology when reading from or
writing to the knowledge graph.

---

## Entity Type Hierarchy

```
EnterpriseEntity (abstract base)
├── Party
│   ├── Person
│   │   ├── Employee
│   │   ├── Candidate
│   │   └── ExternalContact
│   └── Organization
│       ├── Customer
│       ├── Vendor
│       ├── Partner
│       └── Competitor
├── FinancialEntity
│   ├── Transaction
│   ├── Invoice
│   ├── Budget
│   ├── Contract
│   └── PurchaseOrder
├── ProductEntity
│   ├── Product
│   ├── Feature
│   ├── Requirement
│   └── Release
├── TechnicalEntity
│   ├── Service
│   ├── Repository
│   ├── Deployment
│   └── Incident
├── KnowledgeEntity
│   ├── Decision
│   ├── Plan
│   ├── Meeting
│   ├── ActionItem
│   └── Document
└── AgentEntity
    ├── Agent
    ├── Workflow
    └── Skill
```

---

## Core Relationship Vocabulary

| Relationship | From → To | Cardinality | Description |
|---|---|---|---|
| EMPLOYS | Organization → Employee | 1:N | Org employs person |
| REPORTS_TO | Employee → Employee | N:1 | Management hierarchy |
| OWNS | Person → KnowledgeEntity | N:N | Person owns/created entity |
| ASSIGNED_TO | ActionItem → Person | N:1 | Action item assigned to person |
| MEMBER_OF | Person → Organization | N:N | Team/department membership |
| CUSTOMER_OF | Organization → Organization | N:N | Customer relationship |
| VENDOR_OF | Organization → Organization | N:N | Vendor relationship |
| CREATED | Agent → KnowledgeEntity | 1:N | Agent created artifact |
| APPROVED | Person → Decision | N:N | Person approved decision |
| ADDRESSES | Decision → Requirement | N:N | Decision addresses requirement |
| DEPENDS_ON | TechnicalEntity → TechnicalEntity | N:N | Technical dependency |
| TRIGGERED | Incident → Service | N:1 | Incident triggered by service |
| CONTAINS | Plan → Task | 1:N | Plan contains tasks |
| INVOICES | Organization → Organization | N:N | Billing relationship |
| GOVERNS | Policy → Workflow | 1:N | Policy applies to workflow |

---

## Temporal Properties

All entities carry temporal validity metadata:

```yaml
entity:
  valid_from: "YYYY-MM-DD"   # when this fact became true
  valid_to: "YYYY-MM-DD"     # when this fact ceased to be true (null if current)
  transaction_time: "ISO8601" # when this record was inserted into the graph
```

This enables bi-temporal querying: "What did we know about entity X at time T as of version V?"

---

## Semantic Constraints

### Mandatory Attributes per Entity Type

| Entity Type | Required Attributes |
|---|---|
| Employee | name, employee_id, department, start_date, employment_status |
| Customer | name, customer_id, tier, contract_start, csm_owner |
| Transaction | transaction_id, amount, currency, date, category, account |
| Decision | decision_id, title, decision_date, decided_by, rationale |
| Incident | incident_id, severity, declared_at, affected_service, status |

### Cardinality Constraints

- An `ActionItem` must have exactly one assignee
- A `Decision` must have at least one `decided_by` Person
- An `Employee` must belong to exactly one primary department
- A `Budget` must be owned by exactly one Organization unit

### Inheritance Rules

- Sub-type entities inherit all attributes and relationships of their parent type
- Semantic constraints on parent types apply to all sub-types
- Queries on parent types return all sub-type instances unless filtered

---

## Ontology Extension Process

New entity types may be proposed through governance:

1. Submit `ontology.extension_proposed` event with proposed type definition
2. semantic-layer validates: no naming conflicts, consistent inheritance
3. Level-2 operator approval required
4. Extension applied at next scheduled ontology version increment
5. All existing skills notified of new entity type availability

Ontology versions follow semantic versioning: breaking changes increment major version.