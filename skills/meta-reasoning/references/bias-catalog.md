# Bias Catalog Reference

## Cognitive Bias Taxonomy for AI Reasoning

### Category 1: Anchoring and Framing Biases

| Bias | Code | Description | Detection Signal | Mitigation |
|---|---|---|---|---|
| Anchoring bias | CB-A01 | Over-relying on first information encountered | Answer changes significantly with reordered context | Re-run with shuffled context order |
| Framing effect | CB-A02 | Different conclusions from logically equivalent framings | Gain/loss framing shifts recommendation | Test both positive and negative framings |
| Status quo bias | CB-A03 | Preferring the current state without justification | "Continue existing approach" without analysis | Explicitly ask: what would you do from scratch? |
| Sunk cost fallacy | CB-A04 | Continuing based on past investment, not future value | Recommendation references past effort as justification | Re-evaluate excluding sunk costs |

---

### Category 2: Availability and Representativeness Biases

| Bias | Code | Description | Detection Signal | Mitigation |
|---|---|---|---|---|
| Availability heuristic | CB-B01 | Overweighting easily recalled examples | Recommendation biased toward salient recent cases | Request base rate statistics |
| Representativeness heuristic | CB-B02 | Judging probability by how "typical" something looks | Ignores base rates in probability estimates | Explicitly incorporate base rate data |
| Stereotyping | CB-B03 | Applying group-level patterns to individuals | Demographic markers influence recommendations | Blind evaluation without group identifiers |
| Recency bias | CB-B04 | Overweighting recent events in forecasts | Forecast driven by last 30 days vs. long-term trend | Require multi-year historical context |

---

### Category 3: Confirmation and Self-Serving Biases

| Bias | Code | Description | Detection Signal | Mitigation |
|---|---|---|---|---|
| Confirmation bias | CB-C01 | Seeking evidence that confirms prior belief | Evidence against conclusion systematically absent | Request steelman of opposing view |
| Motivated reasoning | CB-C02 | Reasoning toward preferred conclusion | Conclusion matches what stakeholder wants | Blind analysis without stated preference |
| Overconfidence | CB-C03 | Confidence intervals too narrow for uncertainty | 90% CI contains true value < 50% of the time | Calibration check; widen intervals |
| Dunning-Kruger pattern | CB-C04 | Low-quality reasoning delivered with high confidence | High confidence with factual errors | Cross-check against authoritative sources |

---

### Category 4: Logical and Structural Reasoning Errors

| Bias | Code | Description | Detection Signal | Mitigation |
|---|---|---|---|---|
| Base rate neglect | CB-D01 | Ignoring prior probability in conditional reasoning | P(A|B) stated without P(A) prior | Require Bayesian framing |
| Conjunction fallacy | CB-D02 | Assigning higher probability to specific scenario than general | P(A and B) > P(A) in output | Flag impossible probability combinations |
| Post hoc ergo propter hoc | CB-D03 | Assuming causation from temporal sequence | "X happened before Y, therefore X caused Y" | Require causal evidence beyond correlation |
| Modus tollens failure | CB-D04 | Failing to apply contrapositive correctly | Accepts invalid inferential chain | Formal logic check on inference chain |
| Ecological fallacy | CB-D05 | Applying group-level statistics to individuals | Group mean applied to individual case | Clarify level of analysis |

---

### Category 5: Training Data and Distribution Biases

| Bias | Code | Description | Detection Signal | Mitigation |
|---|---|---|---|---|
| Selection bias | CB-E01 | Training data not representative of deployment population | High accuracy on train; low on production | Stratified evaluation across subgroups |
| Measurement bias | CB-E02 | Systematic error in how training labels were created | Label errors correlate with sensitive features | Audit label quality per subgroup |
| Temporal drift | CB-E03 | World changed after training cutoff | Recommendations reference outdated information | Check facts against post-cutoff sources |
| Amplification bias | CB-E04 | Stereotypes amplified relative to training data | Model more stereotyped than its training data | Counterfactual fairness evaluation |

---

## Bias Detection Protocol

### Automated Detection

```python
FUNCTION detect_bias(reasoning_chain, output):
    detected_biases = []

    # CB-A01: Anchoring test — reorder context and check output stability
    reordered_output = run_with_shuffled_context(reasoning_chain.inputs)
    if cosine_similarity(output, reordered_output) < 0.85:
        detected_biases.append(BiasFlag(CB-A01, severity=MEDIUM))

    # CB-C03: Overconfidence test — check if stated confidence is calibrated
    if output.stated_confidence == HIGH and output.factual_accuracy < 0.80:
        detected_biases.append(BiasFlag(CB-C03, severity=HIGH))

    # CB-D01: Base rate check — scan for conditional probability claims
    if contains_conditional_probability(output) and not contains_prior(output):
        detected_biases.append(BiasFlag(CB-D01, severity=MEDIUM))

    # CB-C01: Confirmation bias — check if counterevidence is represented
    if output.evidence_for_conclusion > 3 and output.evidence_against == 0:
        detected_biases.append(BiasFlag(CB-C01, severity=HIGH))

    return detected_biases
```

---

## Bias Severity and Escalation

| Severity | Criterion | Action |
|---|---|---|
| CRITICAL | Bias leads to factually false or harmful output | Block output; regenerate with explicit bias mitigation prompt |
| HIGH | Bias significantly distorts recommendation | Flag for human review; annotate output with bias warning |
| MEDIUM | Bias may affect confidence or framing | Annotate output; generate alternative framing |
| LOW | Minor stylistic bias; does not affect conclusion | Log only; no action |

---

## Mitigation Prompt Templates

### Debiasing Prompt: Confirmation Bias

```
Review your previous analysis. Specifically:
1. List the 3 strongest arguments AGAINST your conclusion.
2. What evidence would change your recommendation?
3. Have you represented opposing views fairly?
If your conclusion changes after this review, update it.
```

### Debiasing Prompt: Overconfidence

```
You stated high confidence. Before finalizing:
1. What is the base rate for this type of prediction being correct?
2. What are the 2-3 most likely ways you could be wrong?
3. Express your confidence as a probability range (e.g., 60-75%) rather than a categorical label.
```