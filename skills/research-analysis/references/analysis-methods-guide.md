# Research Analysis Methods Guide Reference

## Method Selection Framework

### Decision Tree: Choosing the Right Analysis Method

```
STEP 1: What is the research question type?
  → Descriptive ("What is X?") → go to Descriptive Methods
  → Comparative ("Is A different from B?") → go to Comparative Methods
  → Causal ("Does X cause Y?") → go to Causal Methods
  → Predictive ("What will X be?") → go to Predictive Methods
  → Explanatory ("Why does X happen?") → go to Qualitative Methods

STEP 2: What type of data is available?
  → Numerical, structured → Quantitative methods
  → Text, interviews, observations → Qualitative methods
  → Both → Mixed methods

STEP 3: What is the sample size?
  → n < 30 → Non-parametric or qualitative
  → 30 ≤ n < 200 → Parametric with care; check assumptions
  → n ≥ 200 → Full parametric toolkit

STEP 4: Is causation or correlation needed?
  → Correlation → correlation, regression, network analysis
  → Causation → RCT, DiD, IV, RD, structural equation modeling
```

---

## Quantitative Methods

### Descriptive Statistics

```python
# Standard descriptive analysis protocol
descriptive_summary = {
    "count": n,
    "mean": x̄,
    "median": x̃,
    "std": s,
    "min": x_min,
    "max": x_max,
    "p25": Q1,
    "p75": Q3,
    "iqr": Q3 - Q1,
    "skewness": skew(x),  # > 0: right-skewed; < 0: left-skewed
    "kurtosis": kurt(x),  # > 3: heavy tails
}

# Normality check (required before parametric tests)
shapiro_wilk_p = shapiro(x).pvalue
normality_assumed = shapiro_wilk_p > 0.05  # and n < 50
```

### Hypothesis Testing

| Test | Use Case | Assumptions | Python |
|---|---|---|---|
| t-test (independent) | Compare means of 2 groups | Normality, equal variance | `scipy.stats.ttest_ind` |
| t-test (paired) | Before/after comparison | Normality, paired observations | `scipy.stats.ttest_rel` |
| ANOVA | Compare means of 3+ groups | Normality, equal variance | `scipy.stats.f_oneway` |
| Mann-Whitney U | Non-parametric 2-group | Ordinal data | `scipy.stats.mannwhitneyu` |
| Kruskal-Wallis | Non-parametric 3+ groups | Ordinal data | `scipy.stats.kruskal` |
| Chi-square | Categorical association | n > 5 per cell | `scipy.stats.chi2_contingency` |

**Effect size reporting (required alongside p-value):**
- Cohen's d for t-tests: d < 0.2 (negligible), 0.2-0.5 (small), 0.5-0.8 (medium), > 0.8 (large)
- η² for ANOVA
- Cramér's V for chi-square

### Regression Analysis

```
Model selection protocol:
  Continuous outcome, linear relationship → OLS regression
  Continuous outcome, non-linear → polynomial or GAM
  Binary outcome → logistic regression
  Count outcome → Poisson regression
  Time-to-event → Cox proportional hazards

Assumption checks (OLS):
  1. Linearity: residual vs. fitted plot should show no pattern
  2. Independence: Durbin-Watson statistic ≈ 2
  3. Homoscedasticity: Breusch-Pagan test p > 0.05
  4. Normality of residuals: Q-Q plot
  5. No multicollinearity: VIF < 10 for all predictors

Reporting requirements:
  - Coefficients with 95% CI (not just p-values)
  - R² and adjusted R²
  - F-statistic and overall model p-value
  - Assumption violation disclosures if any
```

---

## Qualitative Methods

### Thematic Analysis

```
Protocol (Braun & Clarke 6-phase):
  1. Familiarization: Read all data; note initial impressions
  2. Open coding: Label segments with descriptive codes
  3. Theme search: Cluster codes into candidate themes
  4. Theme review: Verify themes are supported by data; refine
  5. Theme definition: Name and define each theme precisely
  6. Writing: Construct analysis using themes as structure

Quality criteria:
  - Saturation: No new themes emerging from additional data
  - Transferability: Context described fully enough for reader to judge applicability
  - Confirmability: Audit trail from data to conclusions
  - Member checking: Participants confirm themes (if research context permits)
```

### Systematic Literature Review (Supplement to PRISMA)

```yaml
coding_protocol:
  after_screening:
    extract_for_each_paper:
      - study_design: "RCT | observational | meta-analysis | ..."
      - sample_size: integer
      - primary_outcome: string
      - main_findings: string
      - effect_size: float or null
      - quality_score: 1-5 (using GRADE or equivalent)
      - limitations: list[string]

  synthesis_method:
    quantitative: "meta-analysis if ≥ 3 comparable studies; forest plot"
    qualitative: "narrative synthesis if heterogeneous"
    mixed: "convergent synthesis"
```

---

## Reporting Standards

### Statistical Reporting Format

```
Required for all quantitative findings:
  Effect: [statistic] = [value], p [< or >] [threshold], CI95 = [lower, upper], d = [effect size]

Example:
  "Academic performance improved significantly in the intervention group
   (M = 84.2, SD = 8.1) compared to control (M = 76.5, SD = 9.3),
   t(98) = 4.21, p < 0.001, 95% CI [4.1, 11.3], d = 0.84."

Required disclosures:
  - Multiple comparisons: Bonferroni or FDR correction applied (α = [adjusted threshold])
  - Missing data: n missing, method (listwise deletion / imputation)
  - Outliers: Detection method; inclusion/exclusion decision and rationale
```

### Evidence Grading

| Grade | Evidence Type | Recommendation Strength |
|---|---|---|
| A | Systematic review or RCT | Strong — act on this |
| B | Cohort study, well-designed | Moderate — likely to apply |
| C | Case-control, observational | Limited — use with caution |
| D | Expert opinion, case series | Weak — check for better evidence |
| I | Insufficient evidence | Cannot make recommendation |