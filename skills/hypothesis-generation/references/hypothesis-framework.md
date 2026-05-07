# Hypothesis Framework Reference

## Abductive Reasoning Protocol

Abductive reasoning generates the simplest explanation that accounts for all observed evidence.

### Steps:
1. **Identify anomaly or gap:** What observation is unexplained or what question is unanswered?
2. **List competing explanations:** Generate 3–7 candidate explanations using "What if...?" prompts
3. **Apply parsimony:** Prefer the simplest explanation that accounts for all evidence
4. **Check falsifiability:** Each explanation must be testable — state what would disprove it
5. **Rank by evidence:** Score each against existing evidence; select the top-ranked for hypothesis formation

---

## SMART Hypothesis Criteria

Every hypothesis must satisfy all 5 SMART criteria:

| Criterion | Definition | Test Question |
|---|---|---|
| Specific | Unambiguously identifies IV, DV, and mechanism | "Could two researchers design the same experiment from this hypothesis?" |
| Measurable | DV can be quantified or classified | "Is there a numeric metric or categorical outcome we can observe?" |
| Achievable | Data is available or collectable within the project | "Can we actually obtain the data needed?" |
| Relevant | Hypothesis answers a meaningful research question | "Does answering this change what we know or what we do?" |
| Time-bound | A testable experiment can be completed within the project timeline | "Can we get results within N months?" |

---

## IF-THEN Hypothesis Structure

**Template:**
```
IF [manipulation of independent variable (IV)],
THEN [expected change in dependent variable (DV)],
BECAUSE [proposed causal mechanism].
```

**Example:**
```
IF an AI agent's system prompt includes explicit constitutional rules with numeric compliance
thresholds,
THEN the agent's rate of scope-violating actions (measured on the alignment benchmark)
will decrease by ≥ 20% compared to an agent without such rules,
BECAUSE explicit rule articulation activates the model's instruction-following capability
and creates a salient reference point during generation.
```

**Falsification criterion:** This hypothesis is false if the alignment benchmark shows
no statistically significant difference (p > 0.05) between the two conditions, or if
the difference is < 5%.

---

## Hypothesis Scoring Rubric

Score each candidate hypothesis before selecting the top one for experimentation:

### Novelty Score (0–10)

| Score | Criteria |
|---|---|
| 0–2 | Hypothesis is well-established in the literature |
| 3–5 | Minor variant of an existing finding |
| 6–8 | Meaningful extension to a new domain or context |
| 9–10 | Genuinely novel — no prior literature addresses this directly |

### Feasibility Score (0–10)

| Score | Criteria |
|---|---|
| 0–2 | Data unavailable or would take > 12 months to collect |
| 3–5 | Data available but requires significant preparation |
| 6–8 | Data largely available; experiment designable within 90 days |
| 9–10 | Data immediately available; experiment can start within 2 weeks |

### Information Gain Score (0–10)

| Score | Criteria |
|---|---|
| 0–2 | Answering this changes little — result is largely predictable |
| 3–5 | Provides useful confirmation or boundary condition |
| 6–8 | Would meaningfully update the state of knowledge |
| 9–10 | High-impact finding that changes direction or practice |

### Business Relevance Score (0–10)

| Score | Criteria |
|---|---|
| 0–2 | Purely academic; no near-term application |
| 3–5 | Indirectly relevant to organizational goals |
| 6–8 | Directly relevant; result would inform a decision |
| 9–10 | High-stakes decision waiting on this finding |

**Composite hypothesis score:**
```
composite = novelty × 0.25 + feasibility × 0.30 + information_gain × 0.25 + business_relevance × 0.20
```

---

## Experiment Design Outline Template

Produced for the top-ranked hypothesis:

```yaml
experiment_outline:
  hypothesis_id: "HYP-20260507-003"
  hypothesis: "IF ... THEN ... BECAUSE ..."

  design:
    type: "RCT"  # RCT | DiD | Observational | Quasi-experimental
    treatment_condition: "Description of the intervention"
    control_condition: "Description of the control"
    unit_of_analysis: "agent session | user | request | etc."

  data_requirements:
    outcome_variable: "alignment_benchmark_score"
    primary_measurement: "Percentage of scope-violating actions"
    sample_size_required: 200  # Per condition; from power analysis
    data_sources: ["alignment-testing skill", "agent execution logs"]
    data_collection_duration_days: 30

  analysis_plan:
    primary_method: "t-test (two-sample, two-tailed)"
    significance_level: 0.05
    minimum_detectable_effect: "20% reduction in violation rate"
    power: 0.80

  success_criteria: "p < 0.05 AND effect size >= 20%"
  failure_criteria: "p >= 0.05 OR effect size < 5%"

  estimated_duration_days: 45
  resource_estimate: "2 engineer-weeks + compute budget $X"
```