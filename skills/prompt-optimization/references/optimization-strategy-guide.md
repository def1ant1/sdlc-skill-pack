# Prompt Optimization — Optimization Strategy Guide

## Optimization Scope Taxonomy

| Target Type | Examples | Optimization Levers |
|-------------|---------|-------------------|
| System prompt | Skill behavioral instructions | Instruction reordering, CoT scaffolding, persona framing |
| Few-shot examples | In-context demonstrations | Example selection, ordering, format normalization |
| Output format spec | JSON schema, markdown template | Schema simplification, constraint relaxation |
| Model parameters | Temperature, top-p, max_tokens | Grid search over valid ranges |
| Retrieval query | RAG search strings | Query expansion, HyDE, re-ranking |

---

## Optimization Workflow

```
1. Register optimization target
   ├── target_id: "skill/code-review/system-prompt"
   ├── baseline_variant: current production prompt
   └── reward_signal: quality_score | task_accuracy | latency_p95

2. Generate variant candidates
   ├── Strategy: LLM-assisted mutation (see below)
   ├── Strategy: DSPy/TextGrad gradient-based refinement
   └── Strategy: Human-authored alternatives

3. Register variants with reinforcement-optimizer
   └── Algorithm: Thompson Sampling (default)

4. A/B test in production (shadow or live)
   ├── Route X% of traffic to each variant
   └── Collect reward signals per invocation

5. Check convergence (every 10 trials)
   └── P(best arm is best) ≥ 0.95?

6. Promote winner
   ├── If improvement ≥ 5% → auto-promote (non-critical skills)
   └── If P0 skill or HITL-facing → require human approval

7. Archive experiment record
```

---

## LLM-Assisted Prompt Mutation Strategies

### Strategy 1: Instruction Decomposition

Break monolithic instructions into numbered steps to improve instruction following.

**Before:**
```
Review the code for bugs, security issues, style problems, and performance.
```

**After:**
```
Review the code in the following order:
1. Security: check for injection, auth bypass, data exposure
2. Correctness: identify logic errors and edge cases
3. Performance: flag O(n²) or worse complexity, unnecessary allocations
4. Style: check naming, structure, and readability
```

---

### Strategy 2: Chain-of-Thought Scaffolding

Add explicit reasoning steps before the output.

```
Before providing your answer, think through:
- What is the core question being asked?
- What information is available vs. missing?
- What are the 2–3 most likely answers and their confidence?

Then provide your answer in the requested format.
```

---

### Strategy 3: Persona + Authority Framing

```
You are a senior software engineer with 15 years of experience in
distributed systems security. You are reviewing code for a financial
services company where security vulnerabilities have regulatory consequences.
```

---

### Strategy 4: Negative Space Constraints

Explicitly state what NOT to do to reduce hallucination and scope creep.

```
Do NOT:
- Suggest refactors beyond the scope of the reported bug
- Add comments or docstrings to unchanged code
- Request more information before providing a review
```

---

## Prompt Quality Evaluation Rubric

| Dimension | Weight | Scoring Guidance |
|-----------|--------|-----------------|
| Task completion | 35% | Did the output fully address the objective? |
| Accuracy | 30% | Are claims and code correct? |
| Format compliance | 15% | Does output match the required schema/format? |
| Conciseness | 10% | Is the output appropriately concise (not padded)? |
| Safety | 10% | Does output avoid harmful or policy-violating content? |

Automated scoring via a judge LLM (e.g., `claude-opus-4-6`) on a [0, 1] scale per dimension.
Overall `quality_score = Σ(weight × dimension_score)`.

---

## Optimization Experiment Registry Schema

```yaml
optimization_experiment:
  experiment_id: "OPT-EXP-2026-xxxxx"
  target_id: "skill/code-review/system-prompt"
  target_type: system_prompt | few_shot | output_format | model_params
  reward_signal: quality_score
  optimization_algorithm: thompson_sampling
  created_at: "2026-05-07T00:00:00Z"
  status: running | converged | promoted | expired

  variants:
    - variant_id: "baseline"
      description: "Current production prompt"
      is_control: true
      prompt_hash: "sha256:abc123"

    - variant_id: "cot-v1"
      description: "Added chain-of-thought reasoning scaffold"
      is_control: false
      prompt_hash: "sha256:def456"
      mutation_strategy: chain_of_thought

    - variant_id: "decomposed-v1"
      description: "Decomposed instructions into numbered steps"
      is_control: false
      prompt_hash: "sha256:ghi789"
      mutation_strategy: instruction_decomposition

  convergence_criteria:
    min_trials_per_arm: 50
    p_best_threshold: 0.95
    max_duration_days: 30
```

---

## Model Parameter Search Space

```yaml
model_param_search:
  temperature:
    type: float
    range: [0.0, 1.0]
    step: 0.1
    default: 0.7

  top_p:
    type: float
    range: [0.5, 1.0]
    step: 0.05
    default: 0.95

  max_tokens:
    type: int
    options: [512, 1024, 2048, 4096, 8192]
    default: 2048

  frequency_penalty:
    type: float
    range: [0.0, 1.0]
    step: 0.1
    default: 0.0

search_strategy: grid | random | bayesian_optimization
budget_trials: 50
```