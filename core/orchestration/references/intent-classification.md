# Intent Classification Matrix

Used by `core/orchestration/SKILL.md` Step 1 to map user signals to SDLC phases and primary skills.

---

## How to Use This Matrix

1. Tokenize the user's request into key nouns, verbs, and qualifiers.
2. Scan the **Primary Signals** column for matches. A match on any signal in a row is sufficient to activate that row's phase.
3. Scan **Supporting Signals** to confirm or strengthen classification confidence.
4. Scan **Negative Signals** — if these are the dominant signals, this phase is likely **not** the right match.
5. If multiple rows match, collect all matched phases and treat the request as `multi-phase`.
6. If no row matches with confidence, classify as `unknown` and follow the Unknown Intent protocol below.

---

## Classification Matrix

### Requirements Engineering

| Attribute | Values |
|---|---|
| **Phase** | `requirements` |
| **Primary Skill** | `requirements-engineering` |
| **Primary Signals** | "requirements", "PRD", "user story", "acceptance criteria", "scope", "feature spec", "product brief", "epics", "use cases", "traceability", "stakeholder", "backlog item", "functional requirements", "non-functional requirements" |
| **Supporting Signals** | "define what", "capture needs", "clarify scope", "write stories", "document requirements", "prioritize features" |
| **Negative Signals** | "implement", "code", "deploy", "test", "review PR" |
| **Typical Complexity** | `single-phase` |
| **Upstream Dependencies** | none |
| **Common Downstream** | `system-architecture`, `qa-automation` |

---

### System Architecture

| Attribute | Values |
|---|---|
| **Phase** | `architecture` |
| **Primary Skill** | `system-architecture` |
| **Primary Signals** | "architecture", "design", "ADR", "system design", "service boundary", "data model", "API design", "integration pattern", "component diagram", "non-functional requirements", "scalability", "reliability", "technology choice", "tech stack" |
| **Supporting Signals** | "how should we structure", "what pattern", "monolith vs", "microservices", "event-driven", "design decision", "tradeoffs", "quality attributes" |
| **Negative Signals** | "implement the code", "write the function", "fix this bug" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `requirements` (when present) |
| **Common Downstream** | `backend-engineering`, `ai-engineering`, `devsecops` |

---

### AI Engineering

| Attribute | Values |
|---|---|
| **Phase** | `ai-engineering` |
| **Primary Skill** | `ai-engineering` |
| **Primary Signals** | "LLM", "AI", "agent", "RAG", "embeddings", "vector database", "prompt", "model selection", "fine-tuning", "inference", "evaluation", "evals", "AI safety", "hallucination", "context window", "retrieval", "tool use", "Claude", "GPT", "generative AI" |
| **Supporting Signals** | "AI-powered", "AI-enabled", "intelligent", "NLP", "chatbot", "recommendation system", "classification model", "AI pipeline" |
| **Negative Signals** | "no AI involved", "traditional algorithm", "rules-based only" |
| **Typical Complexity** | `multi-phase` |
| **Upstream Dependencies** | `architecture` |
| **Common Downstream** | `backend-engineering`, `devsecops`, `qa-automation`, `compliance-governance` |

---

### Backend Engineering

| Attribute | Values |
|---|---|
| **Phase** | `backend` |
| **Primary Skill** | `backend-engineering` |
| **Primary Signals** | "API", "REST", "GraphQL", "gRPC", "service", "backend", "database", "schema", "endpoint", "controller", "repository", "ORM", "authentication", "authorization", "server", "microservice", "event", "queue", "message broker", "implementation plan" |
| **Supporting Signals** | "build the service", "implement the API", "write the backend", "data access layer", "business logic", "CRUD" |
| **Negative Signals** | "frontend only", "UI only", "no backend" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `architecture` |
| **Common Downstream** | `devsecops`, `qa-automation`, `frontend-engineering` |

---

### Frontend Engineering

| Attribute | Values |
|---|---|
| **Phase** | `frontend` |
| **Primary Skill** | `frontend-engineering` |
| **Primary Signals** | "frontend", "UI", "React", "Vue", "Angular", "component", "page", "accessibility", "responsive", "design system", "CSS", "state management", "client-side", "web app", "user interface", "UX" |
| **Supporting Signals** | "build the UI", "implement the page", "make it accessible", "design the component" |
| **Negative Signals** | "backend only", "no UI", "API only" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `architecture`, `backend-engineering` |
| **Common Downstream** | `qa-automation`, `code-review` |

---

### DevSecOps / Security

| Attribute | Values |
|---|---|
| **Phase** | `security` |
| **Primary Skill** | `devsecops` |
| **Primary Signals** | "security", "threat model", "OWASP", "vulnerability", "CVE", "secrets management", "authentication", "authorization", "JWT", "OAuth", "RBAC", "supply chain", "SAST", "DAST", "penetration test", "hardening", "encryption", "TLS", "zero trust", "CI security", "DevSecOps" |
| **Supporting Signals** | "is this secure", "security review", "check for vulnerabilities", "secure this", "compliance scan" |
| **Negative Signals** | "no security concerns", "internal tool only", "prototype only" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `backend-engineering` or `architecture` |
| **Common Downstream** | `qa-automation`, `compliance-governance` |

---

### QA and Test Automation

| Attribute | Values |
|---|---|
| **Phase** | `qa` |
| **Primary Skill** | `qa-automation` |
| **Primary Signals** | "test", "QA", "coverage", "unit test", "integration test", "end-to-end test", "regression", "test strategy", "test plan", "automation", "pytest", "jest", "playwright", "cypress", "performance test", "load test", "AI eval", "evaluation harness" |
| **Supporting Signals** | "write tests for", "validate the behavior", "ensure correctness", "test this function", "test coverage" |
| **Negative Signals** | "no tests needed", "prototype only", "skip testing for now" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `backend-engineering` or `frontend-engineering` |
| **Common Downstream** | `release-management` |

---

### Code Review

| Attribute | Values |
|---|---|
| **Phase** | `code-review` |
| **Primary Skill** | `code-review` |
| **Primary Signals** | "review", "PR", "pull request", "code quality", "refactor", "maintainability", "readability", "technical debt", "smell", "lint", "static analysis", "feedback on this code", "review this implementation" |
| **Supporting Signals** | "is this code good", "what can be improved", "clean up this code", "code feedback" |
| **Negative Signals** | "implement new feature", "write from scratch" |
| **Typical Complexity** | `single-phase` |
| **Upstream Dependencies** | none (can operate independently) |
| **Common Downstream** | `qa-automation`, `devsecops` |

---

### Release Management

| Attribute | Values |
|---|---|
| **Phase** | `release` |
| **Primary Skill** | `release-management` |
| **Primary Signals** | "release", "deploy", "deployment", "CI/CD", "pipeline", "rollout", "rollback", "version", "semver", "changelog", "feature flag", "canary", "blue-green", "GitOps", "Helm", "Kubernetes deploy", "release checklist", "release readiness" |
| **Supporting Signals** | "ship it", "go to production", "release plan", "deployment strategy", "release notes" |
| **Negative Signals** | "local only", "not deploying yet", "development only" |
| **Typical Complexity** | `single-phase` or `multi-phase` |
| **Upstream Dependencies** | `qa-automation`, `devsecops` |
| **Common Downstream** | `observability`, `sre-incident-response` |

---

### Observability

| Attribute | Values |
|---|---|
| **Phase** | `observability` |
| **Primary Skill** | `observability` |
| **Primary Signals** | "observability", "logging", "metrics", "traces", "SLO", "SLA", "dashboard", "alert", "monitoring", "Datadog", "Prometheus", "Grafana", "OpenTelemetry", "distributed tracing", "error rates", "latency" |
| **Supporting Signals** | "how do we know it's working", "visibility into", "operational readiness", "detect issues in production" |
| **Negative Signals** | "no production deployment", "prototype only" |
| **Typical Complexity** | `single-phase` |
| **Upstream Dependencies** | `release-management` |
| **Common Downstream** | `sre-incident-response` |

---

### SRE and Incident Response

| Attribute | Values |
|---|---|
| **Phase** | `operations` |
| **Primary Skill** | `sre-incident-response` |
| **Primary Signals** | "incident", "outage", "postmortem", "on-call", "runbook", "mitigation", "triage", "SRE", "reliability", "downtime", "degradation", "page", "PagerDuty", "blameless", "root cause", "remediation", "incident report" |
| **Supporting Signals** | "something is broken in production", "investigate this failure", "create a postmortem", "what happened" |
| **Negative Signals** | "pre-production", "planning phase", "no incidents yet" |
| **Typical Complexity** | `single-phase` |
| **Upstream Dependencies** | `observability` |
| **Common Downstream** | `executive-reporting` |

---

### Compliance and Governance

| Attribute | Values |
|---|---|
| **Phase** | `compliance` |
| **Primary Skill** | `compliance-governance` |
| **Primary Signals** | "compliance", "audit", "governance", "SOC 2", "GDPR", "HIPAA", "PCI", "ISO 27001", "policy", "control", "evidence", "risk register", "data classification", "AI Act", "regulatory", "traceability matrix" |
| **Supporting Signals** | "are we compliant", "audit evidence", "policy mapping", "governance review", "risk classification" |
| **Negative Signals** | "ignore compliance for now", "prototype only, no compliance" |
| **Typical Complexity** | `multi-phase` |
| **Upstream Dependencies** | `devsecops`, `qa-automation` |
| **Common Downstream** | `executive-reporting` |

---

### Executive Reporting

| Attribute | Values |
|---|---|
| **Phase** | `reporting` |
| **Primary Skill** | `executive-reporting` |
| **Primary Signals** | "status report", "executive summary", "leadership update", "delivery health", "roadmap status", "risk summary", "stakeholder brief", "board report", "program update", "OKR status" |
| **Supporting Signals** | "summarize for leadership", "what's the delivery status", "report out on this project" |
| **Negative Signals** | "technical deep dive", "implementation details" |
| **Typical Complexity** | `single-phase` |
| **Upstream Dependencies** | any completed phase (reports on current state) |
| **Common Downstream** | none |

---

## Multi-Phase Detection

A request is `multi-phase` when two or more distinct phase rows produce a confident match.

### Common Multi-Phase Patterns

| Pattern Name | Phases | Example Trigger |
|---|---|---|
| `design-and-build` | architecture → backend | "Design and implement a payment service" |
| `build-and-secure` | backend → security | "Build a user auth API and make it secure" |
| `build-and-test` | backend → qa | "Implement the search service and write tests" |
| `secure-and-release` | security → release | "Security review and release plan for v2.0" |
| `ai-full-stack` | architecture → ai-engineering → backend → devsecops → qa | "Build a production-grade AI document processing API" |
| `feature-complete` | requirements → architecture → backend → qa → release | "Build a complete new feature end-to-end" |
| `ops-review` | observability → sre → reporting | "Review our production health and write a status report" |

---

## Unknown Intent Protocol

Classify as `unknown` when:

- No primary signal matches with reasonable confidence
- The request is contradictory (signals from 5+ phases with no clear anchor)
- The request is too vague to safely route (e.g., "help me with my project")

### Unknown Intent Response

Do not guess. Ask exactly **one** clarifying question:

```
To route your request correctly, I need one clarification:

Are you focused on [Option A], [Option B], or [Option C]?

- Option A: <phase description>
- Option B: <phase description>
- Option C: <phase description>
```

Use the three most likely phases based on partial signal matches as the options.

Do not present more than three options.

---

## Classification Confidence Levels

| Level | Criteria | Action |
|---|---|---|
| `high` | 2+ primary signals match; no strong negative signals | Route directly |
| `medium` | 1 primary signal + 1 supporting signal | Route with brief confirmation |
| `low` | Only supporting signals match; or primary signals are ambiguous | Ask one clarifying question |
| `none` | No signals match | Classify as `unknown` |

---

## Notes

- A single request may produce `high` confidence matches on multiple phases simultaneously. This is expected and correct. Collect all matching phases and build a multi-phase skill chain.
- Negative signals reduce confidence but do not override strong primary signal matches unless they are the **dominant** signals in the request.
- When in doubt, classify more broadly and let the Workflow Plan confirmation step allow the user to narrow scope.