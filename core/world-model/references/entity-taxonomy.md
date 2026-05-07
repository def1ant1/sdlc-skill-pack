# World Model Entity Taxonomy & Observation Schema

## Entity Types

| Type | Examples | Volatile Attributes | Stable Attributes |
|------|----------|--------------------|--------------------|
| `project` | PROJ-123, Initiative-Alpha | status, health_score, blockers, spend_to_date | owner, budget, deadline, team |
| `system` | api-gateway, ml-pipeline | availability_pct, p95_latency_ms, error_rate | tech_stack, owner_team, SLA |
| `person` | alice@corp.com | current_projects, capacity_pct | role, department, skills |
| `risk` | RISK-089 | likelihood, impact, mitigation_status | risk_type, domain, owner |
| `budget` | Q2-Engineering | burn_rate_usd, forecast_to_complete | total_budget_usd, period |
| `compliance` | SOC2-CC6.1, GDPR-Art.32 | control_status, evidence_age_days | framework, control_id, owner |
| `incident` | INC-2026-0512 | status, mttr_minutes, active_responders | severity, affected_systems |

---

## Observation Schema

```yaml
observation:
  entity_id: "project/PROJ-123"         # Namespaced entity identifier
  entity_type: project                   # Must match entity type taxonomy
  attribute: "status"                    # Attribute name (kebab-case)
  value: "at_risk"                       # Observed value (type varies by attribute)
  source: "program-governance-agent"     # Observation source ID
  source_credibility: 0.90               # Source credibility weight [0.0–1.0]
  confidence: 0.85                       # Confidence in this specific observation [0.0–1.0]
  timestamp: "2026-05-07T10:00:00Z"     # ISO 8601 observation time
  evidence_refs: []                      # Supporting evidence pointers (optional)
```

---

## Source Credibility Registry

| Source | Credibility Weight | Rationale |
|--------|--------------------|-----------|
| ERP system integration | 0.98 | Authoritative system of record |
| Named persistent agent (primary domain) | 0.90 | Domain expert with direct access |
| Named persistent agent (secondary domain) | 0.70 | Cross-domain inference |
| Telemetry system | 0.95 | Direct metric measurement |
| Human operator assertion | 0.85 | High trust but subject to human error |
| Derived inference (skill output) | 0.65 | Computed, not directly observed |
| External feed | 0.50 | Low trust until validated |

---

## Bayesian Update Parameters

```python
def bayesian_update(prior: float, likelihood: float, credibility: float) -> float:
    """
    Update belief state for a binary attribute (in_risk / not_in_risk).
    prior: current P(hypothesis=True)
    likelihood: P(observation | hypothesis=True)
    credibility: source credibility weight applied to likelihood
    """
    # Credibility-weighted likelihood
    weighted_likelihood = credibility * likelihood + (1 - credibility) * 0.5

    # Bayes update (unnormalized)
    posterior_true = weighted_likelihood * prior
    posterior_false = (1 - weighted_likelihood) * (1 - prior)

    # Normalize
    return posterior_true / (posterior_true + posterior_false)


# Initial priors by entity type and attribute
DEFAULT_PRIORS = {
    "project.status.at_risk": 0.15,       # 15% of projects are at risk by default
    "system.availability_pct": 0.995,     # Systems expected to be up
    "compliance.control_status.failing": 0.05,  # 5% of controls failing by default
    "incident.active": 0.02,              # 2% chance of active incident
}
```

---

## Contradiction Resolution Protocol

```
CONTRADICTION DETECTED when:
  |new_observation.value - current_belief.mode| > contradiction_threshold[attribute_type]
  AND current_belief.confidence > 0.80
  AND new_observation.source_credibility > 0.60

Resolution steps:
  1. Create CONTRADICTION record:
       entity_id, attribute, belief_value, observation_value,
       belief_source, observation_source, detected_at
  2. Set attribute state → UNCERTAIN (block downstream decisions depending on it)
  3. Escalate to the domain-responsible persistent agent
  4. Agent investigates and asserts a resolution observation with confidence=1.0
  5. World model accepts authoritative assertion → clears CONTRADICTION

Contradiction thresholds:
  categorical attributes: any value change conflicts with confidence > 0.80 belief
  numeric attributes: |delta| > 2 × attribute_noise_floor
```

---

## Staleness Rules

```yaml
staleness_policy:
  volatile_attributes:
    stale_after_hours: 24
    action_on_stale: mark_STALE, notify_responsible_agent
  stable_attributes:
    stale_after_days: 30
    action_on_stale: mark_STALE (informational only)

  # Per entity-type overrides
  overrides:
    system.availability_pct:
      stale_after_minutes: 5  # Real-time metric — stale quickly
    incident.status:
      stale_after_minutes: 30
    budget.burn_rate_usd:
      stale_after_hours: 4
```