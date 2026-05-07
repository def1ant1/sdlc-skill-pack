# Knowledge Graph Ontology

## Entity Types

| Entity | Description | Key Properties |
|---|---|---|
| `Skill` | A platform skill definition | name, version, maturity, category |
| `Agent` | A registered autonomous agent | name, permitted_actions, data_access |
| `Decision` | A recorded organizational decision | question, selected_option, rationale, confidence |
| `Project` | A product or engineering project | name, status, owner, OKR links |
| `Feature` | A product feature | name, status, owner, PRD link |
| `Meeting` | A recorded meeting | date, participants, decisions, action_items |
| `ActionItem` | A task from a meeting | description, owner, due_date, status |
| `Person` | A team member | name, role, department |
| `Document` | A policy, standard, or reference doc | title, path, version, category |
| `Risk` | A registered risk | title, severity, owner, status |
| `Incident` | A production incident | severity, duration, root_cause |
| `Model` | An AI model or LoRA adapter | name, version, benchmark_score, status |

---

## Relationship Types

| Relationship | From → To | Description |
|---|---|---|
| `DEPENDS_ON` | Skill → Skill | Skill dependency |
| `DECIDED_BY` | Decision → Person | Who made the decision |
| `DECIDED_IN` | Decision → Meeting | Meeting where decision was made |
| `CONTRIBUTES_TO` | Feature → Project | Feature belongs to project |
| `REQUIRED_BY` | Decision → Project | Decision supports a project |
| `OWNED_BY` | Project/Risk/Feature → Person | Ownership |
| `CREATED_IN` | ActionItem → Meeting | Action item origin |
| `ASSIGNED_TO` | ActionItem → Person | Who is responsible |
| `RELATED_TO` | Decision → Decision | Related decisions |
| `IMPLEMENTS` | Feature → Decision | Feature implements a decision |
| `MITIGATES` | Skill/Feature → Risk | How a risk is mitigated |
| `CAUSED_BY` | Incident → Risk | Risk that materialized |
| `RESOLVED_BY` | Incident → ActionItem | What fixed the incident |
| `EVALUATED_BY` | Model → Agent | Who ran model evaluation |
| `TRAINED_FOR` | Model → Skill | Model optimized for a skill |
| `REFERENCED_IN` | Document → Skill | Document referenced by skill |
| `COVERS` | Document → Risk | Policy covering a risk |

---

## Graph Queries (Cypher Examples)

**Find all open action items for a person**:
```cypher
MATCH (p:Person {name: "Jane"})<-[:ASSIGNED_TO]-(a:ActionItem)
WHERE a.status IN ['open', 'overdue']
RETURN a ORDER BY a.due_date
```

**Find decisions related to a project**:
```cypher
MATCH (d:Decision)-[:REQUIRED_BY]->(p:Project {name: "Product X"})
RETURN d ORDER BY d.decided_at DESC
```

**Find skill dependency chain**:
```cypher
MATCH path = (s:Skill {name: "autonomous-os"})-[:DEPENDS_ON*]->(dep:Skill)
RETURN path
```

**Find risks with no mitigation**:
```cypher
MATCH (r:Risk) WHERE r.status = 'open'
AND NOT EXISTS {(r)<-[:MITIGATES]-()}
RETURN r ORDER BY r.risk_score DESC
```

---

## Node Naming Conventions

- Entity IDs follow the skill-specific ID formats (MTG-YYYYMMDD-NNN, DEC-YYYYMMDD-NNN, etc.)
- Property names use `snake_case`
- All timestamps stored as ISO 8601 strings
- Enums stored as lowercase strings

---

## Index Configuration

For performance, the following Neo4j indexes are maintained:

| Label | Properties |
|---|---|
| Decision | `decided_at`, `confidence` |
| ActionItem | `status`, `due_date`, `owner_id` |
| Risk | `status`, `severity`, `risk_score` |
| Person | `name` (unique) |
| Meeting | `date`, `meeting_type` |
| Model | `status`, `benchmark_score` |