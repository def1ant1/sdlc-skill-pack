# Entity Extraction Rules

Used by `core/knowledge-graph/SKILL.md` to identify entities in workflow outputs,
phase reports, and documents, and map them to the graph schema.

---

## Extraction Pipeline

For each document or workflow output:

1. Tokenize into sentences
2. Apply pattern matching (table below) to identify entity mentions
3. Classify each mention to an entity type
4. Extract properties from surrounding context
5. Identify relationships from sentence structure

---

## Signal Patterns per Entity Type

| Entity Type | Strong Signals | Weak Signals | Negative Signals |
|---|---|---|---|
| `Product` | "product", "service", "platform", "app", "SaaS", "API we built" | "system", "tool", "solution" | "third-party", "external vendor" |
| `Feature` | "feature", "capability", "functionality", "we added", "now supports" | "enhancement", "improvement" | "bug fix", "hotfix" |
| `API` | "endpoint", "REST API", "/v1/", "GraphQL", "gRPC", "webhook" | "interface", "contract" | "UI", "dashboard" |
| `Deployment` | "deployed", "released to", "v1.2.3", "production push", "rollout" | "shipped", "went live" | "drafted", "planned" |
| `Customer` | "customer", "user", "client", "account", "subscriber" | "prospect", "lead", "trial" | "internal user", "test account" |
| `Campaign` | "campaign", "launch", "marketing push", "SEO effort", "paid ads" | "initiative", "program" | "internal", "experiment" |
| `RevenueEvent` | "MRR", "ARR", "upgrade", "churn", "expansion", "new contract" | "revenue", "billing" | "estimate", "projection" |
| `Workflow` | "workflow", "plan ID", "WP-", "SDLC run", "GTM workflow" | "process", "pipeline" | "manual task" |
| `Decision` | "decided to", "we will use", "chosen approach", "DEC-", "accepted:" | "agreed", "confirmed" | "considering", "might" |
| `Agent` | "skill loaded", "orchestrator", "AI agent", "Claude", "Qwen" | "model", "LLM" | "human", "operator" |

---

## Property Extraction Rules

| Entity | Property | Extraction Method |
|---|---|---|
| Product | `name` | Proper noun immediately following "product", "platform", or "service" |
| Product | `status` | Past tense verbs: "launched" → production, "building" → development |
| Deployment | `version` | Regex: `v\d+\.\d+(\.\d+)?` or semver pattern |
| Deployment | `environment` | Keywords: "production", "staging", "dev", "preview" |
| Customer | `type` | Keywords: "trial", "paying", "churned", "prospect" |
| RevenueEvent | `amount` | Currency pattern: `\$[\d,]+` or `\d+ MRR` |
| RevenueEvent | `type` | "new contract" → new_mrr, "upgraded" → expansion, "cancelled" → churn |
| Campaign | `type` | Channel keywords: "SEO" → seo, "Google Ads" → paid, "blog" → content |
| Decision | `decision` | Text following "decided to" or "we will" until sentence end |

---

## Relationship Extraction

| Sentence Pattern | Extracted Relationship |
|---|---|
| "[Product] deployed to production" | Deployment → DEPLOYED_TO → Product |
| "[Customer] signed up for [Product]" | Customer → USES → Product |
| "[Campaign] drove [N] signups for [Product]" | Campaign → PROMOTES → Product |
| "[Feature] implements [Decision]" | Feature → IMPLEMENTS → Decision |
| "decided to use [tech]" | Decision → CONSTRAINS → Feature/API |
| "[Customer] upgraded / expanded" | Customer → GENERATES → RevenueEvent(expansion) |
| "[Agent/Skill] produced [Artifact]" | Agent → PERFORMS → Workflow |

---

## Conflict Resolution

When an extracted entity conflicts with an existing node:

| Conflict | Resolution |
|---|---|
| Same canonical name, same type | Merge: update properties, add new relationships |
| Same canonical name, different type | Flag for human review; do not auto-merge |
| New alias for existing entity | Add `aliases[]` property to existing node |
| Ambiguous entity name (multiple matches) | Use context window to disambiguate; if unresolvable, create with `status: unresolved` |

---

## Extraction Quality Score

After extracting from a document, compute:

```
extraction_score = (entities_extracted / entities_expected) *
                   (relationships_valid / relationships_extracted)
```

Target extraction score: > 0.80. Below 0.60 triggers a manual review flag.