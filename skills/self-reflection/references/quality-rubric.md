# Quality Rubric Reference

## Output Quality Dimensions

### Dimension 1: Accuracy (30% weight)

**Definition:** The degree to which claims, facts, and computations in the output are correct.

| Score | Rubric |
|---|---|
| 5 | All factual claims verified; no errors; all computations correct |
| 4 | Minor factual imprecision (e.g., approximate date); no material errors |
| 3 | 1–2 factual errors that do not undermine main conclusion |
| 2 | Multiple factual errors; some material to conclusion |
| 1 | Pervasive factual errors; output is misleading |

---

### Dimension 2: Completeness (20% weight)

**Definition:** The degree to which the output addresses all aspects of the request.

| Score | Rubric |
|---|---|
| 5 | All stated requirements addressed; no gaps |
| 4 | All major requirements addressed; minor gaps in details |
| 3 | Most requirements addressed; 1 significant gap |
| 2 | Key requirements partially addressed; 2+ significant gaps |
| 1 | Fundamental requirement unaddressed |

---

### Dimension 3: Reasoning Quality (25% weight)

**Definition:** The logical coherence and depth of the reasoning chain.

| Score | Rubric |
|---|---|
| 5 | Clear, valid inference chain; assumptions stated; counterarguments addressed |
| 4 | Sound reasoning with minor unsupported leaps |
| 3 | Generally valid but reasoning gaps reduce confidence in conclusion |
| 2 | Reasoning flawed; conclusion not well-supported by evidence |
| 1 | Reasoning invalid or absent; conclusion asserted without support |

---

### Dimension 4: Clarity and Structure (15% weight)

**Definition:** How easy the output is to understand and act on.

| Score | Rubric |
|---|---|
| 5 | Excellent organization; appropriate format for audience; no ambiguity |
| 4 | Well-structured; minor clarity issues |
| 3 | Adequately structured; some sections unclear or too verbose |
| 2 | Poorly organized; reader must reconstruct intended meaning |
| 1 | Unstructured; incomprehensible |

---

### Dimension 5: Appropriate Uncertainty (10% weight)

**Definition:** Whether confidence is appropriately expressed given available evidence.

| Score | Rubric |
|---|---|
| 5 | Confidence precisely calibrated; uncertainty clearly communicated |
| 4 | Appropriate hedging on uncertain claims; minor overconfidence |
| 3 | Inconsistent hedging; some claims overconfident |
| 2 | Systematically overconfident; critical uncertainties not disclosed |
| 1 | False certainty on speculative claims |

---

## Composite Quality Score

```
quality_score = (
    accuracy × 0.30 +
    completeness × 0.20 +
    reasoning_quality × 0.25 +
    clarity × 0.15 +
    uncertainty × 0.10
)

# Normalize to 0-100:
quality_score_normalized = (quality_score / 5) × 100
```

### Quality Thresholds

| Score Range | Quality Label | Action |
|---|---|---|
| 90–100 | Excellent | Deliver as-is |
| 75–89 | Good | Minor refinement recommended |
| 60–74 | Acceptable | Specific improvements required |
| 45–59 | Substandard | Major revision required |
| < 45 | Unacceptable | Regenerate from scratch |

---

## Reflection Prompt Templates

### General Reflection Prompt

```
Review the output above against these criteria:

1. ACCURACY: Are all factual claims correct? List any you are uncertain about.
2. COMPLETENESS: Does this fully address what was asked? What is missing?
3. REASONING: Are the conclusions well-supported? Where is the reasoning weakest?
4. CLARITY: Would the intended audience understand this? What is unclear?
5. UNCERTAINTY: Have you appropriately signaled where you are less confident?

Score each dimension 1-5 using the rubric. Then provide:
- Your composite quality score (out of 100)
- The top 1-2 improvements that would most increase quality
- A revised output incorporating those improvements
```

### Task-Specific Reflection Templates

**Code Review:**
```
Review the generated code for:
1. Correctness: Does it handle all edge cases?
2. Security: Any OWASP Top 10 vulnerabilities?
3. Performance: Any obvious inefficiencies?
4. Maintainability: Is it readable and documented?
Rate 1-5 per dimension and revise.
```

**Analysis Report:**
```
Review this analysis for:
1. Are the data sources authoritative and cited?
2. Is the statistical reasoning valid?
3. Are alternative explanations considered?
4. Are the recommendations actionable and prioritized?
```

---

## Improvement Identification Protocol

```
FUNCTION identify_improvements(output, quality_scores):
    improvements = []

    # Priority: lowest-scoring dimensions first
    FOR dimension IN sorted(quality_scores, key=score, ascending=True):
        IF quality_scores[dimension] < 4.0:
            improvement = {
                dimension: dimension,
                current_score: quality_scores[dimension],
                specific_issue: diagnose_issue(output, dimension),
                specific_fix: recommend_fix(output, dimension),
                expected_score_after_fix: estimate_score(dimension, fix)
            }
            improvements.append(improvement)

    # Cap at top 3 improvements — don't overwhelm
    RETURN improvements[:3]
```

---

## Self-Reflection Output Format

```yaml
self_reflection_result:
  output_id: "OUT-20260507-042"
  reflection_timestamp: "2026-05-07T14:00:00Z"

  dimension_scores:
    accuracy: 4
    completeness: 3
    reasoning_quality: 4
    clarity: 5
    uncertainty: 3

  composite_score: 78.5
  quality_label: "Good"

  top_improvements:
    - dimension: "completeness"
      issue: "Missing analysis of Option C from the original request"
      fix: "Add Option C evaluation in section 3"
    - dimension: "uncertainty"
      issue: "Revenue projection stated without confidence interval"
      fix: "Add ±15% confidence range to all revenue figures"

  revised_output_provided: true
```