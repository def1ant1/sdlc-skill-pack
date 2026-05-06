# Quality Gate Catalog

Defines pass/fail criteria for every SDLC phase transition.
Enforced by `core/orchestration/SKILL.md` Step 4.
Referenced by `scripts/validation/validate_workflow_state.py`.

---

## Gate Format

Each gate entry uses this structure:

```
Gate ID:           unique identifier
Transition:        "Phase A → Phase B"
Category:          structural | artifact | security | quality | governance
Fail Action:       block | warn | escalate
Criteria:          ordered list of pass conditions
Evidence Required: artifacts that must exist before gate can be evaluated
Remediation:       what to do when the gate fails
```

---

## GATE-001: requirements-complete

```
Gate ID:    GATE-001
Transition: Requirements → Architecture
Category:   structural + artifact
Fail Action: block
```

### Criteria

All criteria must pass:

1. A product requirements document (PRD) or equivalent scope brief exists.
2. At least three user stories are defined, each with an actor, action, and outcome.
3. Acceptance criteria exist for every user story (testable, unambiguous).
4. Functional and non-functional requirements are separated.
5. At least one non-functional requirement addresses performance, reliability, or security.
6. Scope boundaries are stated — what is explicitly out of scope is documented.
7. No acceptance criterion uses vague language: "fast", "easy", "nice-looking" are non-compliant without measurable targets.

### Evidence Required

- PRD or scope brief document
- User story list with acceptance criteria

### Remediation

- Missing PRD: produce one using `shared/templates/prd-template.md`
- Vague acceptance criteria: apply INVEST/SMART criteria to rewrite
- Missing NFRs: elicit from stakeholder context or apply sensible defaults documented as assumptions

---

## GATE-002: architecture-approved

```
Gate ID:    GATE-002
Transition: Architecture → Backend / AI Engineering / Frontend
Category:   artifact + structural
Fail Action: block
```

### Criteria

All criteria must pass:

1. A system design document exists covering: components, data flows, and integration points.
2. Service boundaries are defined with explicit interface contracts (API surface or event schema).
3. At least one ADR exists for each major technology decision (framework, database, AI provider, auth strategy).
4. Non-functional requirements (latency, throughput, availability, security posture) are addressed in the design.
5. No component is labelled "TBD" without a documented plan to resolve it.
6. Data model covers primary entities, relationships, and data ownership.
7. The architecture references applicable standards from `shared/standards/architecture-principles.md`.

### Evidence Required

- System design document
- At least one ADR (in `shared/templates/adr-template.md` format)
- Service boundary map or component diagram

### Remediation

- Missing ADR: produce one for every decision marked "TBD"
- Undefined service boundaries: resolve using service boundary checklist in `skills/system-architecture/references/`
- NFRs unaddressed: add quality attribute section using `skills/system-architecture/references/quality-attributes.md`

---

## GATE-003: ai-design-approved

```
Gate ID:    GATE-003
Transition: AI Engineering → Backend Engineering
Category:   artifact + governance
Fail Action: block
```

### Criteria

All criteria must pass:

1. AI architecture document specifies model provider, model version or family, and rationale.
2. Prompt design specification exists with: input schema, output schema, and at least one example.
3. Eval plan defines: success metrics, failure modes, and at least three evaluation test cases.
4. AI risk classification is assigned using the risk tiers in `shared/standards/ai-governance-baseline.md`.
5. Human oversight requirements are stated for the assigned risk tier.
6. Data handling for model inputs is specified (what data reaches the model, data minimization approach).
7. Fallback behavior is defined for model unavailability and for out-of-distribution inputs.

### Evidence Required

- AI architecture document
- Prompt design specification
- Eval plan with success metrics
- AI risk classification

### Remediation

- Missing eval plan: produce using eval plan template in `skills/ai-engineering/`
- Missing risk classification: apply the risk matrix from `shared/standards/ai-governance-baseline.md`
- No fallback defined: add degraded-mode behavior to the architecture document

---

## GATE-004: backend-implementation-ready

```
Gate ID:    GATE-004
Transition: Backend Engineering → DevSecOps
Category:   artifact + structural
Fail Action: block
```

### Criteria

All criteria must pass:

1. API specification exists in OpenAPI 3.x or equivalent format.
2. All endpoints have: HTTP method, path, request schema, response schema, and error responses.
3. Authentication and authorization strategy is defined (not deferred).
4. Database schema covers all entities, with primary keys, foreign keys, and index strategy noted.
5. Service implementation plan lists all components, their responsibilities, and dependencies.
6. Error handling conventions are defined (error format, status code mapping).
7. No endpoint accepts unbounded input without stated validation rules.

### Evidence Required

- OpenAPI specification
- Database schema
- Service implementation plan

### Remediation

- Missing auth strategy: select from patterns in `shared/standards/security-baseline.md`
- Incomplete error handling: apply error convention from `shared/standards/` API standards
- Unbounded inputs: add validation rules to request schemas

---

## GATE-005: security-review-passed

```
Gate ID:    GATE-005
Transition: DevSecOps → QA Automation
Category:   security + governance
Fail Action: block (critical findings) | warn (low findings)
```

### Criteria

All criteria must pass for `block` to clear:

1. Threat model exists and covers all service entry points identified in the architecture.
2. OWASP Top 10 coverage is documented — each category is either mitigated or explicitly accepted as out of scope with rationale.
3. No finding rated `critical` or `high` severity is left without an assigned remediation task.
4. Secrets management approach is defined — no hardcoded credentials, tokens, or keys in design artifacts.
5. Authentication and authorization controls are reviewed against the backend specification.
6. For AI systems: prompt injection defense is included in the threat model.
7. For AI systems: model input data classification is documented and aligns with the data governance policy.
8. Supply chain controls are addressed (dependency pinning, lock files, provenance for AI model artifacts).

Criteria rated `warn` (do not block, but log in memory packet):

- Static analysis has not yet been run (acceptable before implementation is complete)
- Low-severity findings are documented but not yet remediated

### Evidence Required

- Threat model document
- Security findings list with severity ratings
- OWASP coverage checklist

### Remediation

- Critical/high finding open: assign remediation task, track in memory packet, re-run gate after fix
- Missing threat model: produce using threat model template in `skills/devsecops/`
- AI risks not addressed: extend threat model with AI-specific attack surface

---

## GATE-006: test-strategy-accepted

```
Gate ID:    GATE-006
Transition: QA Automation → Release Management
Category:   quality + artifact
Fail Action: block
```

### Criteria

All criteria must pass:

1. Test strategy document exists covering: unit, integration, and end-to-end layers.
2. Coverage targets are defined (minimum % per layer or by feature criticality).
3. At least one end-to-end test scenario is specified for each primary user journey.
4. Regression baseline is defined — what constitutes a regression, and how it is detected.
5. For AI systems: eval harness design is specified with deterministic assertions on output schema and at least three LLM evaluation cases.
6. Performance test approach is defined for any endpoint with a latency SLO.
7. Security test cases from the DevSecOps gate are included in the test plan.
8. Test data strategy is defined — how sensitive data is handled in test environments.

### Evidence Required

- Test strategy document
- Test case suite (at minimum: titles, inputs, expected outcomes)
- AI eval harness design (if AI is in scope)

### Remediation

- Missing coverage targets: apply coverage policy from `shared/standards/` testing standards
- No end-to-end scenarios: derive from user stories in the PRD
- AI eval missing: produce using eval plan from `skills/ai-engineering/`

---

## GATE-007: release-readiness-confirmed

```
Gate ID:    GATE-007
Transition: Release Management → Observability
Category:   structural + governance
Fail Action: block
```

### Criteria

All criteria must pass:

1. Release checklist is complete with no open blockers.
2. All upstream gate statuses in the memory packet are `PASS`.
3. Deployment plan covers: target environment, deployment steps, configuration management, and smoke test procedure.
4. Rollback procedure is defined and tested (or explicitly stated as untested with a noted risk).
5. Changelog or release notes are drafted.
6. Feature flags are defined for any functionality that requires staged rollout.
7. Approval sign-offs required by the release policy are documented.

### Evidence Required

- Release checklist (complete)
- Deployment plan with rollback
- Memory packet showing all upstream gates as PASS

### Remediation

- Upstream gate FAIL: resolve the failing gate before release gate can be evaluated
- No rollback plan: produce using rollback template in `skills/release-management/`
- Missing approval: identify approver, record as open blocker, block release

---

## GATE-008: operations-readiness-confirmed

```
Gate ID:    GATE-008
Transition: Observability → SRE / Incident Response
Category:   structural + quality
Fail Action: warn
```

### Criteria

All criteria should pass (warn on failure, do not block):

1. SLO definitions exist for all externally-facing endpoints (latency, availability, error rate).
2. Alerting strategy is defined — alert conditions, routing, and on-call escalation path.
3. Structured logging is specified — log format, fields, and PII handling.
4. Dashboard requirements are documented.
5. Runbook stubs exist for at least the three most likely failure modes.

### Evidence Required

- SLO definitions
- Alert strategy document
- Runbook stubs

### Remediation

- Missing SLOs: derive from NFRs in the architecture document
- No runbooks: produce stubs using `skills/sre-incident-response/`

---

## Gate Status Values

| Status | Meaning |
|---|---|
| `PASS` | All block-level criteria met; workflow may advance |
| `PASS_WITH_WARNINGS` | Block-level criteria met; one or more warn-level criteria failed; warnings logged in memory packet |
| `FAIL` | One or more block-level criteria failed; workflow is halted |
| `NOT_EVALUATED` | Gate has not been reached yet |
| `SKIPPED` | Gate explicitly waived by user with documented rationale (rare; must be logged in memory packet) |

---

## Cross-Gate Rules

1. A gate may only be evaluated when all its `Evidence Required` artifacts exist in the memory packet or are provided directly.
2. A `FAIL` status on any gate prevents all downstream gates from being evaluated.
3. Gate waivers (`SKIPPED`) require explicit user acknowledgement and a documented rationale in the memory packet.
4. Gate re-evaluation is permitted after remediation — the prior `FAIL` record is retained and the new result is appended.
5. Gate results feed `scripts/orchestration/validate_workflow_state.py` for automated enforcement.