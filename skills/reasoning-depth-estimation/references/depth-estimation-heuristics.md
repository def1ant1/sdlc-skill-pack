# Depth Estimation Heuristics Reference

## Reasoning Depth Taxonomy

| Depth Level | Label | Description | Model Tier Recommended |
|---|---|---|---|
| 0 | Recall | Single fact retrieval; no reasoning required | Nano |
| 1 | Lookup | Multi-fact retrieval with simple combination | Micro |
| 2 | Inference | Apply one logical rule or transformation | Micro–Standard |
| 3 | Composition | Chain 2–3 reasoning steps; intermediate conclusions | Standard |
| 4 | Analysis | Decompose complex problem; consider alternatives | Standard–Advanced |
| 5 | Synthesis | Integrate multiple domains; construct novel framework | Advanced |
| 6 | Meta-reasoning | Reason about reasoning; identify uncertainty sources | Advanced–Reasoning |
| 7 | Novel research | Open-ended problems without known solution structure | Reasoning |

---

## Depth Estimation Heuristics

### Heuristic 1: Question Word Analysis

```python
def depth_from_question_word(prompt):
    # These signals correlate with reasoning depth
    signals = {
        "what is": 0,        # Recall
        "what are": 0,
        "when did": 0,
        "who is": 0,
        "define": 1,
        "list": 1,
        "summarize": 2,
        "compare": 3,
        "explain why": 3,
        "analyze": 4,
        "evaluate": 4,
        "design": 5,
        "synthesize": 5,
        "critique": 5,
        "what if": 4,
        "how would you": 4,
        "develop a framework": 6,
        "research": 7,
        "prove": 6,
    }
    for signal, depth in sorted(signals.items(), key=lambda x: -x[1]):
        if signal in prompt.lower():
            return depth
    return 2  # Default: inference level
```

### Heuristic 2: Multi-Step Indicator Detection

```python
def depth_from_structure(prompt):
    indicators = {
        # +1 per indicator detected
        "step by step": +1,
        "first.*then.*finally": +1,       # Regex: sequential structure
        "consider.*trade-off": +1,
        "given that.*what": +1,           # Conditional reasoning
        "assuming.*derive": +1,
        r"\d+\.\s": +1,                   # Numbered sub-questions
        "justify your": +1,
        "what are the implications": +1,
        "under what conditions": +1,
        "prove that": +2,                 # Formal proof
    }
    total_depth_adjustment = sum(
        weight for pattern, weight in indicators.items()
        if re.search(pattern, prompt, re.IGNORECASE)
    )
    return total_depth_adjustment
```

### Heuristic 3: Domain Complexity Adjustment

```python
DOMAIN_BASE_DEPTHS = {
    "factual_recall": 0,
    "code_simple": 2,
    "code_complex": 4,
    "mathematics_basic": 2,
    "mathematics_advanced": 6,
    "legal_reasoning": 5,
    "medical_diagnosis": 5,
    "strategic_planning": 6,
    "scientific_research": 7,
    "creative_writing": 3,
    "data_analysis": 4,
    "causal_inference": 5,
}

def domain_depth_adjustment(detected_domain):
    return DOMAIN_BASE_DEPTHS.get(detected_domain, 3)
```

---

## Composite Depth Estimation

```python
def estimate_reasoning_depth(prompt, detected_domain):
    base = depth_from_question_word(prompt)
    structural_bonus = depth_from_structure(prompt)
    domain_floor = domain_depth_adjustment(detected_domain)

    raw_estimate = max(base + structural_bonus, domain_floor)
    # Clamp to [0, 7]
    depth_estimate = max(0, min(7, raw_estimate))

    confidence = compute_confidence(prompt, depth_estimate)

    return DepthEstimate(
        depth=depth_estimate,
        confidence=confidence,
        recommended_tier=DEPTH_TO_TIER[depth_estimate]
    )

DEPTH_TO_TIER = {
    0: "Nano",
    1: "Nano",
    2: "Micro",
    3: "Standard",
    4: "Standard",
    5: "Advanced",
    6: "Advanced",
    7: "Reasoning"
}
```

---

## Confidence Calibration

```
Confidence in depth estimate:
  HIGH (0.85+):
    - Question structure is clear and unambiguous
    - Domain is well-classified
    - No conflicting signals

  MEDIUM (0.65-0.84):
    - Mixed signals (simple structure but complex domain)
    - Ambiguous question framing

  LOW (< 0.65):
    - Prompt is very short (< 20 tokens) — insufficient signal
    - Domain is unclear or spans multiple domains
    - Novel question type not in training distribution

Action on LOW confidence:
  → Use "safe" depth estimate: round UP to next tier
  → Flag for post-execution review (compare actual vs. estimated depth)
```

---

## Depth Estimation Evaluation

Track accuracy of depth estimates against observed difficulty:

```
Evaluation protocol (monthly calibration run):
  1. Sample 500 requests from production with known outcomes
  2. Label actual_depth using post-hoc analysis:
       actual_depth = highest_tier_needed_to_achieve_quality_threshold
  3. Compute depth estimation accuracy:
       accuracy = mean(|estimated_depth - actual_depth| ≤ 1)  # Within 1 level
  4. If accuracy < 0.75: recalibrate heuristic weights

Tracking metrics:
  - Under-estimation rate: estimated < actual (routes to under-powered model)
  - Over-estimation rate: estimated > actual (routes to over-powered model = waste)
  - Target: under_estimation_rate < 0.10 (cost of under-estimation > over-estimation)
```

---

## Depth Estimation Record

```yaml
depth_estimation:
  request_id: "REQ-WF042-STEP3"
  prompt_tokens: 156
  detected_domain: "strategic_planning"
  question_word_depth: 5
  structural_bonus: 2
  domain_floor: 6
  raw_estimate: 7
  final_depth_estimate: 7
  confidence: 0.82
  recommended_tier: "Reasoning"
  explanation: "Strategic planning domain (floor=6) + 'develop a framework' signal + numbered sub-questions (+1)"
```