# Policy Justification Templates Reference

## Justification Framework

Every policy decision must be justified across three dimensions:
1. **Necessity** — Why this policy is needed
2. **Proportionality** — Why the scope and strength are appropriate
3. **Alternatives** — Why alternatives were not selected

---

## Template Catalog

### Template 1: Regulatory Compliance Justification

**Use for:** Policies driven by legal or regulatory requirements.

```markdown
## Policy Justification: {Policy Name}

### Regulatory Basis
**Regulation:** {Regulation name and citation (e.g., GDPR Article 32)}
**Obligation:** {What the regulation specifically requires}
**Applicable to:** {Which systems, users, or data are in scope}
**Enforcement date:** {When compliance is required}
**Penalty for non-compliance:** {Fines, sanctions, or operational risk}

### Necessity Analysis
{Explain how the proposed policy satisfies the regulatory obligation.
Reference specific regulatory text or guidance documents.}

### Proportionality Analysis
The policy scope is proportionate because:
- **Population affected:** {N users / X% of total users}
- **Impact on affected users:** {Description of friction or constraint}
- **Risk mitigated:** {Severity and likelihood of the regulatory risk}
- **Proportionality test:** The compliance benefit outweighs the friction cost
  because {quantified or qualified rationale}.

### Alternatives Considered
| Alternative | Why Rejected |
|-------------|--------------|
| {Alt 1} | {Reason — e.g., does not fully satisfy regulation} |
| {Alt 2} | {Reason — e.g., higher cost with equivalent compliance} |

### Approval Chain
| Approver | Role | Date |
|----------|------|------|
| {Name} | Legal / Compliance | {Date} |
| {Name} | CTO / CISO | {Date} |
```

---

### Template 2: Security Policy Justification

**Use for:** Policies driven by security risk management.

```markdown
## Policy Justification: {Policy Name}

### Risk Statement
**Threat:** {Description of threat actor, vector, and target}
**Vulnerability addressed:** {What weakness this policy mitigates}
**Risk rating (before policy):** {CRITICAL | HIGH | MEDIUM | LOW}
**Risk rating (after policy):** {Expected risk reduction}
**Evidence basis:** {Incident history, threat intel source, penetration test finding}

### Policy Mechanism
{Explain exactly how the policy mitigates the risk.
Map each policy control to the threat it addresses.}

### Necessity Analysis
{Why is the policy necessary? Could the risk be accepted without this policy?
Reference risk appetite statement if available.}

### Proportionality Analysis
**Controls selected:** {List of controls}
**Estimated effectiveness:** {Expected risk reduction %}
**Operational impact:** {Friction score, throughput impact}
**Cost:** {Implementation cost, ongoing cost}
**Benefit-cost ratio:** {Expected loss avoided / total policy cost}

### Alternatives Considered
| Alternative | Risk Reduction | Operational Impact | Cost | Why Rejected |
|-------------|---------------|-------------------|------|--------------|
| {Alt 1} | {X%} | {Low/Med/High} | {$} | {Reason} |

### Sunset Condition
This policy should be reviewed if:
- {Condition 1: e.g., threat is remediated at source}
- {Condition 2: e.g., alternative control becomes available}
**Next review date:** {Date}
```

---

### Template 3: Operational Efficiency Justification

**Use for:** Policies driven by cost reduction or process optimization.

```markdown
## Policy Justification: {Policy Name}

### Business Case
**Problem statement:** {What inefficiency or cost is being addressed}
**Current state:** {Metrics describing the current problem}
**Target state:** {Metrics describing the desired outcome}
**Expected benefit:** {Quantified improvement: cost savings, time savings, error reduction}

### Policy Design
{Describe the policy and how it addresses the problem.
Include rollout plan if phased.}

### Impact Assessment
**Affected stakeholders:** {List of teams or roles affected}
**Positive impacts:** {Benefits delivered to stakeholders}
**Negative impacts:** {Constraints, friction, or costs imposed}
**Net impact:** {Net positive/negative and to whom}

### Alternatives Considered
| Alternative | Expected Benefit | Implementation Effort | Why Rejected |
|-------------|-----------------|----------------------|--------------|
| {Alt 1} | {Benefit} | {Effort} | {Reason} |

### Success Metrics
| Metric | Baseline | Target | Measurement Method | Review Date |
|--------|----------|--------|--------------------|-------------|
| {Metric 1} | {Value} | {Target} | {Method} | {Date} |
```

---

### Template 4: AI Safety Policy Justification

**Use for:** Policies governing AI system behavior, autonomy, or deployment.

```markdown
## Policy Justification: {Policy Name}

### Safety Concern
**Harm scenario:** {Description of the harm this policy prevents}
**Harm category:** {PHYSICAL | FINANCIAL | REPUTATIONAL | PRIVACY | SOCIETAL}
**Severity:** {CRITICAL | HIGH | MEDIUM | LOW}
**Likelihood (without policy):** {Probability or frequency estimate}

### Constitutional Alignment
This policy enforces constitutional rule: {CONST-001 | CONST-002 | CONST-003 | CONST-004 | CONST-005}
**Rule text:** {Exact rule text}
**Policy contribution:** {How the policy operationalizes the rule}

### Behavioral Impact Analysis
**Capability restricted:** {What the AI system can no longer do}
**Capability preserved:** {What the AI system can still do}
**User impact:** {How users are affected}
**Legitimate use cases impacted:** {Any valid uses that become harder}
**Mitigation for impacted cases:** {How legitimate uses can still be served}

### Evidence and Precedent
{Reference to red team findings, alignment research, or prior incidents
that justify the policy.}

### Oversight Mechanism
**Who enforces:** {Technical control / Human review / Audit}
**Override capability:** {Who can override and under what conditions}
**Audit trail:** {How enforcement is logged}
```

---

## Justification Quality Checklist

Before finalizing any justification:

```
□ Necessity is established with evidence (not assumption)
□ Proportionality analysis includes both benefits AND costs
□ All material alternatives are documented with rejection reasons
□ Success metrics are specific and measurable
□ Sunset or review condition is defined
□ Affected stakeholders have been consulted or notified
□ Approval chain is complete
□ Justification references authoritative sources (regulation text, threat intel, etc.)
```