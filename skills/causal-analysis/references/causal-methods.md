# Causal Methods Reference

## Method Selection Guide

| Method | Use When | Data Required | Key Assumption |
|---|---|---|---|
| RCT Analysis | Randomized experiment was conducted | Treatment/control groups with random assignment | Random assignment (verify balance) |
| Difference-in-Differences | Pre/post data with control group; no randomization | Panel data: treated + untreated units, before + after | Parallel trends in pre-period |
| Instrumental Variables | Selection bias; endogeneity; no clean control group | Instrument Z that affects treatment but not outcome directly | Relevance, exclusion restriction, independence |
| Regression Discontinuity | Sharp threshold determines treatment | Running variable and outcome near threshold | Continuity of potential outcomes at threshold |
| Do-Calculus / DAG | Causal graph is known or estimable | Observational data; causal graph structure | Graph structure is correct |
| Propensity Score Matching | Observational; confounders are measured | Pre-treatment covariates; outcome | No unmeasured confounders |

---

## Assumption Checklists by Method

### Difference-in-Differences

- [ ] **Parallel trends:** Pre-period trends for treated and control groups are parallel (verify with event study plot)
- [ ] **No anticipation:** Treated units did not change behavior in anticipation of treatment
- [ ] **Stable unit treatment value (SUTVA):** No spillovers between treated and control
- [ ] **Common support:** Treated and control units are similar on pre-period characteristics
- [ ] **Exogenous treatment timing:** Treatment was not selected based on outcome trajectory

### Instrumental Variables

- [ ] **Relevance:** Instrument Z has a strong first-stage effect on treatment D (F-statistic > 10)
- [ ] **Exclusion restriction:** Z affects outcome Y only through D (not directly) — must be argued theoretically
- [ ] **Independence:** Z is independent of unmeasured confounders (as-good-as-random)
- [ ] **Monotonicity:** Z affects all units' treatment in the same direction (no defiers)

### Regression Discontinuity

- [ ] **No manipulation:** Agents cannot precisely control the running variable near the threshold (McCrary density test p > 0.05)
- [ ] **Local continuity:** Potential outcomes are continuous at the threshold
- [ ] **Stable bandwidth:** Results are robust to different bandwidth choices (bandwidth sensitivity test)
- [ ] **No other discontinuities:** No other variables jump discontinuously at the same threshold

---

## Effect Estimation Guidance

### Average Treatment Effect (ATE)

Appropriate when estimating the average effect for the entire population:

```python
# DiD estimator (two-period, two-group)
ATE = (Y_treated_post - Y_treated_pre) - (Y_control_post - Y_control_pre)
SE = cluster_robust_standard_error(unit_level)
CI_95 = (ATE - 1.96*SE, ATE + 1.96*SE)
```

### Conditional Average Treatment Effect (CATE)

Appropriate when treatment effects vary across subgroups:

- Estimate CATE using Causal Forests, meta-learners (S-, T-, X-learner)
- Validate CATE estimates with honest cross-fitting to avoid overfitting
- Report CATE for relevant subgroups with confidence intervals

---

## Robustness Testing Protocol

Run at minimum 3 robustness checks for any causal estimate:

| Test | Purpose | Pass Criterion |
|---|---|---|
| Placebo treatment | Apply treatment to a pre-period window; effect should be ~0 | Placebo estimate within 1 SE of zero |
| Alternative control group | Repeat with a different, plausible control group | Direction of effect consistent |
| Bandwidth sensitivity (RD) | Vary bandwidth ±50%; results should be similar | Effect direction consistent; magnitude within 30% |
| Falsification (IV) | Test instrument on an outcome it should not affect | Null result (p > 0.10) |
| Covariate balance (PSM) | Verify covariates are balanced post-matching | Standardized mean difference < 0.10 |

---

## Robustness Score

```
robustness_score = (checks_passed / total_checks_run) × 100
```

- Score ≥ 80: High confidence — proceed with recommendation
- Score 60–79: Moderate confidence — state caveats in report
- Score < 60: Low confidence — flag as inconclusive; do not drive major decisions

---

## Effect Estimate Interpretation Guide

| Metric | Interpretation | Report As |
|---|---|---|
| ATE | Average causal effect of treatment across population | "Treatment increased Y by X units (95% CI: [a, b])" |
| ATT | Average effect on the treated (local estimate) | "Among treated units, Y increased by X units" |
| LATE (IV) | Effect on compliers only | "For units induced to treatment by Z, Y increased by X units" |
| CATE by subgroup | Heterogeneous effects | Table of subgroup effects with CIs |