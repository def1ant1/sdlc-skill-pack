# Generation Prompt Templates Reference

## Template Architecture

Each template has four sections:
1. **System prompt** — Model role and generation constraints
2. **Schema prompt** — Expected output format
3. **Diversity prompt** — Instructions for variety and coverage
4. **Quality gate** — Inline validation criteria

---

## Template Catalog

### Template 1: Instruction-Following Pair

**Use for:** Generating (instruction, response) pairs for instruction-tuning datasets.

```
SYSTEM PROMPT:
You are a synthetic data generator. Your task is to create high-quality
instruction-following examples for the domain: {domain}.

Constraints:
- Instructions must be realistic and practical (plausibly from a real user)
- Responses must be correct, complete, and appropriately detailed
- Avoid fictional scenarios involving real people by name
- Do not generate harmful, illegal, or deceptive content
- Do not reproduce copyrighted text verbatim

SCHEMA PROMPT:
Generate exactly one example in this JSON format:
{
  "instruction": "...",
  "context": "..." or null,
  "response": "...",
  "difficulty": "easy" | "medium" | "hard",
  "domain": "{domain}",
  "skills_demonstrated": ["skill1", "skill2"]
}

DIVERSITY PROMPT (fill in per batch):
Generate an example with:
- Difficulty: {difficulty}
- Sub-domain: {subdomain}
- Response style: {concise | detailed | step-by-step | conversational}
- User persona: {novice | intermediate | expert}
DO NOT repeat examples from previous batches. Previously covered topics: {covered_topics}.

QUALITY GATE (model must self-check before output):
Before outputting, verify:
□ Instruction is unambiguous
□ Response fully addresses the instruction
□ No factual errors in response
□ Response length is appropriate for difficulty
□ Example is distinct from covered_topics list
```

---

### Template 2: Code Generation Example

```
SYSTEM PROMPT:
Generate realistic code generation benchmark items for {programming_language}.
Each item is a programming task with:
1. A natural language specification
2. Type hints and function signatures (if applicable)
3. At least 3 test cases with expected outputs
4. A reference solution

Constraints:
- Tasks must be implementable without external libraries (standard lib only)
- Test cases must cover edge cases (empty input, boundary values, error conditions)
- Solutions must be idiomatic {programming_language}

SCHEMA PROMPT:
{
  "task_description": "...",
  "function_signature": "def function_name(param: type) -> return_type:",
  "test_cases": [
    {"input": "...", "expected_output": "...", "note": "..."},
    ...
  ],
  "reference_solution": "...",
  "difficulty": "easy" | "medium" | "hard",
  "concepts": ["recursion", "dynamic_programming", ...]
}

DIVERSITY PROMPT:
Difficulty: {difficulty}
Core concept: {concept}  # From: [arrays, strings, graphs, trees, dp, math, sorting, ...]
Avoid these concepts in this batch: {excluded_concepts}
```

---

### Template 3: Factual Q&A with Citation

```
SYSTEM PROMPT:
Generate factual question-answer pairs for {knowledge_domain}.
Every answer must cite its source using [Source: ...] notation.
Only generate Q&A pairs where the answer is verifiable and stable
(not opinion-dependent or subject to rapid change).

SCHEMA PROMPT:
{
  "question": "...",
  "answer": "...",
  "sources": ["Source: [Title, Author/Organization, Year]"],
  "answer_type": "factual" | "procedural" | "conceptual",
  "confidence": "high" | "medium",
  "temporal_stability": "stable" | "may_change"
}

QUALITY GATE:
□ Question has exactly one correct answer
□ Answer is accurate as of knowledge cutoff {cutoff_date}
□ Sources are real (do not fabricate citations)
□ Answer does not include subjective claims without attribution
```

---

### Template 4: Multi-Turn Dialogue

```
SYSTEM PROMPT:
Generate a realistic multi-turn dialogue for a {role} assistant.
The dialogue should demonstrate {target_skill} over {n_turns} turns.

Dialogue quality requirements:
- User turns must be realistic and varied (rephrasing, follow-ups, corrections)
- Assistant turns must be coherent with conversation history
- Dialogue must have a natural arc (opening, development, resolution)
- Do not have the assistant behave in ways that violate safety guidelines

SCHEMA PROMPT:
{
  "dialogue_id": "DLG-{id}",
  "domain": "...",
  "target_skill": "...",
  "turns": [
    {"role": "user", "content": "..."},
    {"role": "assistant", "content": "..."},
    ...
  ],
  "quality_dimensions": {
    "coherence": 1-5,
    "helpfulness": 1-5,
    "naturalness": 1-5
  }
}

DIVERSITY PROMPT:
User communication style: {formal | casual | technical | confused | impatient}
Problem complexity: {simple | moderate | complex}
Resolution type: {resolved | partially_resolved | escalated}
```

---

## Batch Generation Configuration

```yaml
batch_config:
  template_id: "TEMPLATE-001"
  target_count: 10000
  batch_size: 50  # Items per API call
  domain: "software_engineering"

  diversity_matrix:
    # Ensure coverage across all combinations
    difficulty: [easy, medium, hard]
    subdomain: [frontend, backend, devops, security, ml]
    response_style: [concise, detailed, step-by-step]

  coverage_tracking:
    method: "sliding_window"
    window_size: 500  # Track last 500 generated items for diversity
    similarity_threshold: 0.75  # Reject if cosine similarity > 0.75 with recent item

  quality_filter:
    auto_reject_if:
      - "instruction contains known harmful pattern"
      - "response contains factual error (via fact-check model)"
      - "cosine_similarity_to_recent > 0.75"
      - "response length < 50 words AND difficulty != easy"
    human_review_sample_rate: 0.05  # 5% manual review
```

---

## Anti-Pattern Checklist

Generated examples must NOT contain:

```
□ Fabricated citations or sources
□ Personally identifiable information (real names, addresses, SSNs)
□ Instructions for creating weapons, malware, or harmful substances
□ Biased stereotyping of demographic groups
□ Logically inconsistent chains of reasoning presented as correct
□ Claims presented as factual that are actually opinions
□ Exact reproduction of copyrighted content (> 20 verbatim tokens)
□ Adversarial patterns designed to jailbreak models
```