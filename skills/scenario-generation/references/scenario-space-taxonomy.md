# Scenario Space Taxonomy Reference

## Scenario Classification Dimensions

### Dimension 1: Time Horizon

| Horizon | Code | Definition | Planning Use |
|---|---|---|---|
| Immediate | TH-0 | 0–30 days | Operational decisions, incident response |
| Near-term | TH-1 | 1–6 months | Tactical planning, sprint planning |
| Medium-term | TH-2 | 6–18 months | Roadmap, resource allocation |
| Long-term | TH-3 | 18 months – 3 years | Strategic planning |
| Horizon | TH-4 | 3–10 years | Vision, foundational investment |

### Dimension 2: Uncertainty Level

| Level | Code | Definition | Scenario Type |
|---|---|---|---|
| Known | UL-0 | Outcomes and probabilities well-established | Base case projection |
| Risk | UL-1 | Known outcomes, uncertain probabilities | Risk-adjusted planning |
| Uncertainty | UL-2 | Unknown probabilities; outcomes partially known | Scenario planning |
| Ambiguity | UL-3 | Uncertain outcomes AND uncertain probabilities | Wild card / emergence |
| True ignorance | UL-4 | Cannot enumerate outcomes | Black swan preparation |

### Dimension 3: Scenario Purpose

| Purpose | Code | Description |
|---|---|---|
| Base case | SP-BC | Most likely trajectory; used as planning anchor |
| Optimistic | SP-OPT | Upside scenario; used for opportunity planning |
| Pessimistic | SP-PES | Downside scenario; used for risk planning |
| Stress test | SP-ST | Extreme downside; used to find breaking points |
| What-if | SP-WI | Specific decision or event alternative |
| Wild card | SP-WC | Low-probability, high-impact disruption |

---

## Scenario Space Coverage Requirements

A well-formed scenario set must cover:

```yaml
coverage_requirements:
  minimum_scenarios: 4
  required_types:
    - SP-BC  # Always include base case
    - SP-OPT  # At least one optimistic
    - SP-PES  # At least one pessimistic
    - SP-ST or SP-WC  # At least one extreme

  variable_coverage:
    # Each key uncertainty variable must vary across scenarios
    minimum_variable_range: 3  # Each variable tested at low/mid/high
    cross_scenario_independence: true  # Scenarios should not be nested

  probability_coherence:
    # If assigning probabilities to scenarios:
    sum_of_probabilities: 1.00
    minimum_per_scenario: 0.05  # No scenario with < 5% probability
```

---

## Uncertainty Variable Catalog

### Economic Variables

```yaml
economic_variables:
  - name: "market_growth_rate"
    pessimistic: -0.05
    base: 0.08
    optimistic: 0.18

  - name: "interest_rate_level"
    pessimistic: 0.08  # High rates = tighter credit
    base: 0.05
    optimistic: 0.02

  - name: "inflation_rate"
    pessimistic: 0.07
    base: 0.03
    optimistic: 0.02
```

### Technology Variables

```yaml
technology_variables:
  - name: "ai_capability_leap"
    pessimistic: "incremental improvement only"
    base: "steady capability scaling"
    optimistic: "breakthrough capability jump (AGI-adjacent)"

  - name: "compute_cost_trajectory"
    pessimistic: "+15% per year (energy costs)"
    base: "-20% per year (Moore's Law equivalent)"
    optimistic: "-50% per year (new hardware paradigm)"

  - name: "regulatory_ai_environment"
    pessimistic: "comprehensive mandatory compliance (EU AI Act + global equivalents)"
    base: "sector-specific voluntary guidelines"
    optimistic: "light-touch self-regulation"
```

### Competitive Variables

```yaml
competitive_variables:
  - name: "new_entrant_threat"
    pessimistic: "major tech company enters market with 10× resources"
    base: "2-3 well-funded startups compete"
    optimistic: "no credible new entrants within planning horizon"

  - name: "customer_switching_cost"
    pessimistic: "low (commoditized market)"
    base: "moderate (integration-dependent)"
    optimistic: "high (deep workflow integration)"
```

---

## Scenario Narrative Template

```yaml
scenario:
  id: "SCN-STRATEGY-2026-003"
  name: "Regulatory Headwind"
  type: SP-PES
  time_horizon: TH-2
  uncertainty_level: UL-2
  probability: 0.20

  narrative: |
    By Q4 2026, the EU AI Act is fully enforced with stricter-than-anticipated
    requirements. The US follows with sector-specific AI legislation. Compliance
    costs rise 40% and time-to-market for new AI features doubles. Enterprise
    buyers adopt a "wait-and-see" posture, delaying purchasing decisions.

  key_assumptions:
    - "EU AI Act enforcement begins September 2026 as scheduled"
    - "High-risk AI classification applies to our core product"
    - "US federal AI legislation passes in 2026 Q3"
    - "Compliance certification timeline: 6 months per jurisdiction"

  uncertainty_variable_values:
    regulatory_ai_environment: "comprehensive mandatory compliance"
    market_growth_rate: 0.03
    customer_switching_cost: "high (compliance co-dependency)"

  strategic_implications:
    threats:
      - "Compliance cost creates barrier to new feature development"
      - "SMB customers exit market (cannot afford compliance overhead)"
    opportunities:
      - "Early compliance certification becomes competitive differentiator"
      - "Compliance tooling can be productized for customer resale"

  leading_indicators:
    - "EU AI Act guidance documents published Q1 2026"
    - "Enterprise RFP requirements include AI compliance clauses"
    - "Competitor compliance announcements"

  trigger_date_to_update_scenario: "2026-06-01"
```

---

## Scenario Set Consistency Check

```
FUNCTION validate_scenario_set(scenarios):
    # Check probability sums to 1.0
    IF probability-weighted: ASSERT abs(sum(s.probability for s in scenarios) - 1.0) < 0.01

    # Check variable ranges are sensible
    FOR each variable v:
        values = [s.variable_values[v] for s in scenarios]
        ASSERT max(values) > min(values)  # Must vary across scenarios
        ASSERT no_contradictions(values)  # No logically impossible combinations

    # Check narrative coherence
    FOR each scenario s:
        ASSERT s.key_assumptions are consistent with s.uncertainty_variable_values
        ASSERT s.strategic_implications follow from s.narrative

    RETURN validation_report
```