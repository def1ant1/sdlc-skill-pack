# Graph Schema

Used by `core/knowledge-graph/SKILL.md` to define entity types, their properties,
and the full relationship catalog for the Apotheon organizational knowledge graph.

---

## Entity Definitions

### Organization
```yaml
node_label: Organization
properties:
  id: string (uuid)
  name: string (canonical)
  domain: string
  industry: string
  created_at: datetime
```

### Workspace
```yaml
node_label: Workspace
properties:
  id: string
  name: string
  type: "project | team | product-line"
  created_at: datetime
```

### Product
```yaml
node_label: Product
properties:
  id: string
  name: string
  type: "saas | api | library | platform | mobile | desktop"
  status: "ideation | development | beta | production | deprecated"
  domain: string
  tech_stack: string[]
  created_at: datetime
  launched_at: datetime (nullable)
```

### Feature
```yaml
node_label: Feature
properties:
  id: string
  name: string
  status: "planned | in_progress | released | deprecated"
  phase_built_in: string
  release_version: string (nullable)
```

### API
```yaml
node_label: API
properties:
  id: string
  name: string
  type: "rest | graphql | grpc | websocket | mcp"
  base_url: string
  version: string
  status: "active | deprecated | draft"
```

### Deployment
```yaml
node_label: Deployment
properties:
  id: string
  version: string
  environment: "development | staging | production"
  platform: string
  deployed_at: datetime
  deployed_by: string
  status: "active | rolled_back | superseded"
```

### Customer
```yaml
node_label: Customer
properties:
  id: string
  name: string (anonymized if PII)
  type: "prospect | trial | paying | churned"
  segment: "smb | mid-market | enterprise"
  mrr: number (nullable)
  first_seen_at: datetime
```

### Campaign
```yaml
node_label: Campaign
properties:
  id: string
  name: string
  type: "seo | paid | content | outbound | event | partnership"
  channel: string
  status: "draft | active | paused | complete"
  budget: number (nullable)
  started_at: datetime
  ended_at: datetime (nullable)
```

### RevenueEvent
```yaml
node_label: RevenueEvent
properties:
  id: string
  type: "new_mrr | expansion | contraction | churn | reactivation"
  amount: number
  currency: "USD"
  occurred_at: datetime
```

### Workflow
```yaml
node_label: Workflow
properties:
  id: string
  type: "sdlc | gtm | support | analytics | governance"
  plan_id: string
  complexity: string
  status: "running | complete | failed"
  started_at: datetime
  completed_at: datetime (nullable)
```

### Agent
```yaml
node_label: Agent
properties:
  id: string
  name: string
  type: "skill | orchestrator | domain-expert"
  model: string
  version: string
```

---

## Relationship Catalog

| From | Relationship | To | Properties |
|---|---|---|---|
| Organization | OWNS | Workspace, Product | since: datetime |
| Workspace | CONTAINS | Product, Workflow, Agent | — |
| Product | HAS | Feature, API, Deployment | — |
| Product | TARGETS | Customer | since: datetime |
| Feature | IMPLEMENTS | Decision, Requirement | — |
| API | EXPOSED_BY | Product | version: string |
| API | CONSUMED_BY | Feature, Customer | — |
| Deployment | DEPLOYED_TO | Product | environment: string |
| Deployment | SUPERSEDES | Deployment | — |
| Customer | USES | Product, Feature | since: datetime |
| Customer | GENERATES | RevenueEvent | — |
| Campaign | TARGETS | Customer | — |
| Campaign | PROMOTES | Product, Feature | — |
| Campaign | GENERATES | RevenueEvent | attribution: string |
| RevenueEvent | ATTRIBUTED_TO | Campaign, Customer | weight: float |
| Workflow | PRODUCES | Artifact, Decision, Feature, Deployment | phase: string |
| Workflow | INVOLVES | Product, Agent | role: string |
| Agent | PERFORMS | Workflow | — |
| Agent | MAKES | Decision | confidence: float |
| Decision | CONSTRAINS | Feature, API, Deployment | — |
| Decision | SUPERSEDES | Decision | — |

---

## Constraint Rules

1. Every node must have `id` and `name` populated.
2. Every node must have at least one outgoing or incoming relationship.
3. `Customer.name` must be anonymized if it contains PII (replace with `CUST-NNN`).
4. `RevenueEvent.amount` must be positive for `new_mrr` and `expansion`; negative for `contraction` and `churn`.
5. Only one `DEPLOYED_TO` relationship may have `status: active` per Product+environment combination.
6. `Decision.SUPERSEDES` chains must be acyclic.