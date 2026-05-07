# Causal Attribution Reference

## Attribution Method Catalog

### Method 1: Activation Patching

**Use for:** Identifying which model components mediate a specific behavior.

```
Protocol:
1. Run model on "clean" input x_clean → record all intermediate activations A_clean
2. Run model on "corrupted" input x_corrupt → record activations A_corrupt
3. FOR each component c (attention head, MLP layer, residual stream position):
   a. Run x_corrupt with A_clean[c] patched in (replacing A_corrupt[c])
   b. Measure change in output metric: Δ_c = metric(patched) - metric(corrupted)
4. Attribute importance: I(c) = Δ_c / (metric(clean) - metric(corrupted))
5. Components with I(c) > 0.1 are causally important for this behavior
```

**Limitation:** Identifies where behavior is encoded; does not explain why.

---

### Method 2: Counterfactual Tracing

**Use for:** Attributing workflow outcome changes to specific input or decision changes.

```
For a workflow W producing output O from inputs I:

counterfactual_attribution(factor_f):
    O_actual = W(I)
    I_cf = I WITH f → f_counterfactual
    O_cf = W(I_cf)
    attribution_score(f) = metric(O_actual) - metric(O_cf)

# Example: What caused revenue to drop 15% this quarter?
attribution_scores:
    pricing_change: -8%    # Removing pricing change would recover 8%
    market_contraction: -5%  # Removing market change would recover 5%
    competitor_entry: -2%  # Removing competitor entry recovers 2%
```

---

### Method 3: Shapley Value Attribution

**Use for:** Fair allocation of credit/blame among multiple contributing factors.

```
Shapley value for factor i:
  φ_i = Σ_{S ⊆ F\{i}} [|S|!(|F|-|S|-1)!/|F|!] × [v(S∪{i}) - v(S)]

  where:
    F = set of all factors
    S = subset of factors not including i
    v(S) = model output when only factors in S are active

Approximation (for |F| > 10):
  Use KernelSHAP with n_samples = 1000 permutations

Attribution interpretation:
  φ_i > 0: factor i positively contributed to outcome
  φ_i < 0: factor i negatively contributed (detracted)
  Σ φ_i = v(F) - v(∅)  # Shapley values sum to total effect
```

---

### Method 4: Evidence-Weighted Causal Graph

**Use for:** Multi-step causal chains with observable intermediate evidence.

```yaml
causal_graph:
  nodes:
    - id: "marketing_spend"
      type: "input"
      observed_value: 2000000
    - id: "brand_awareness"
      type: "intermediate"
      observed_value: 0.34
      counterfactual_value: 0.21  # Without marketing spend
    - id: "new_customer_acquisition"
      type: "intermediate"
      observed_value: 12400
    - id: "revenue"
      type: "outcome"
      observed_value: 4800000

  edges:
    - from: "marketing_spend"
      to: "brand_awareness"
      causal_effect: 0.61  # Normalized effect size
      evidence_strength: 0.82  # Based on historical correlation + RCT
    - from: "brand_awareness"
      to: "new_customer_acquisition"
      causal_effect: 0.74
      evidence_strength: 0.91
    - from: "new_customer_acquisition"
      to: "revenue"
      causal_effect: 0.88
      evidence_strength: 0.96

  path_attribution:
    marketing_spend → revenue (via awareness):
      total_effect: 0.61 × 0.74 × 0.88 = 0.398
      confidence: 0.72
```

---

## Attribution Confidence Scoring

```
confidence_score = evidence_quality × sample_adequacy × assumption_validity

evidence_quality:
  RCT or natural experiment: 1.0
  Quasi-experimental (DiD, IV): 0.8
  Observational with controls: 0.6
  Correlational only: 0.3

sample_adequacy:
  n > 10,000: 1.0
  1,000 < n ≤ 10,000: 0.8
  100 < n ≤ 1,000: 0.6
  n ≤ 100: 0.4

assumption_validity:
  All assumptions tested and met: 1.0
  Minor violations, sensitivity checked: 0.8
  Moderate violations, bounds reported: 0.6
  Major violations: 0.3
```

---

## Attribution Report Format

```yaml
causal_attribution_report:
  report_id: "CAT-20260507-001"
  question: "What caused the 15% drop in Q1 revenue?"
  method_used: "counterfactual_tracing + shapley"
  confidence_score: 0.78

  attributed_factors:
    - factor: "pricing_increase"
      attribution_pct: -53.3
      shapley_value: -960000
      evidence_strength: 0.85
      confidence_interval: [-1100000, -820000]

    - factor: "market_contraction"
      attribution_pct: -33.3
      shapley_value: -600000
      evidence_strength: 0.72
      confidence_interval: [-780000, -420000]

    - factor: "competitor_entry"
      attribution_pct: -13.3
      shapley_value: -240000
      evidence_strength: 0.61
      confidence_interval: [-380000, -100000]

  total_explained: -1800000  # Should match actual revenue drop
  unexplained_residual: 0  # Revenue drop was -1.8M, fully attributed

  limitations:
    - "Competitor entry effect may be underestimated due to lagged response"
    - "Market contraction measured using proxy indicator (industry index)"

  recommended_actions:
    - "Consider pricing rollback for price-sensitive segments"
    - "Monitor competitor market share monthly"
```