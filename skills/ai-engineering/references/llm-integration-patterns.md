# LLM Integration Patterns

## Pattern 1 — Direct Completion

**Use when**: Single-turn, well-defined task; no tool use; output is final.

```python
response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2048,
    system=SYSTEM_PROMPT,      # loaded from versioned prompt registry
    messages=[{"role": "user", "content": user_input}]
)
```

**Requirements**:
- System prompt must be versioned and logged with `prompt_id` and `prompt_version`
- `max_tokens` must be set explicitly — never use default
- Log `input_tokens`, `output_tokens`, `latency_ms`, and `model` to telemetry

---

## Pattern 2 — Tool Use (Function Calling)

**Use when**: LLM must take actions (search, compute, write) and observe results.

```python
tools = [
    {"name": "search", "description": "...", "input_schema": {...}},
    {"name": "write_file", "description": "...", "input_schema": {...}},
]

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4096,
    tools=tools,
    messages=messages
)

# Agentic loop
while response.stop_reason == "tool_use":
    tool_result = execute_tool(response)
    messages.append({"role": "assistant", "content": response.content})
    messages.append({"role": "user", "content": [tool_result]})
    response = client.messages.create(...)
```

**Requirements**:
- Every tool call must be logged with inputs and outputs
- Tool execution must be sandboxed via sandbox-execution skill
- Max loop iterations must be capped (default: 10); log and halt on cap

---

## Pattern 3 — RAG (Retrieval-Augmented Generation)

**Use when**: LLM needs grounding in proprietary or recent knowledge.

```
Query → retrieval-engine (hybrid search) → top-K chunks
       → inject into context with source attribution
       → LLM generates grounded response
       → response includes citations
```

**Requirements**:
- Retrieved chunks must include source, date, and access-control label
- LLM must be instructed to cite sources; validate citations in output
- If retrieved context contradicts model knowledge: prefer retrieved context
- Log retrieval latency, chunk count, and fusion scores to telemetry

---

## Pattern 4 — Structured Output

**Use when**: Output must be machine-parseable (JSON, YAML, code).

```python
# Use JSON mode or explicit schema in prompt
system = """
Respond ONLY with valid JSON matching this schema:
{
  "decision": string,
  "confidence": float (0.0–1.0),
  "reasoning": string,
  "risks": [string]
}
Do not include any text outside the JSON object.
"""
```

**Validation requirement**: Parse output against schema before use. On parse failure:
retry once with error context injected. On second failure: surface raw output for
human review.

---

## Pattern 5 — Multi-Step Chain

**Use when**: Complex task benefits from decomposition into discrete LLM steps.

```
Step 1: Analyze → structured intermediate output
Step 2: Plan   → structured plan based on Step 1 output
Step 3: Execute → final output based on plan
```

**Requirements**:
- Each step uses a separate, focused prompt (not one mega-prompt)
- Intermediate outputs are validated before passing to next step
- Chain is logged as a single workflow with step-level telemetry
- Failed intermediate step halts chain; does not attempt to proceed

---

## Prompt Engineering Standards

| Standard | Rule |
|---|---|
| Versioning | Every production prompt has a `prompt_id` and semantic version |
| Specificity | System prompt defines role, constraints, and output format explicitly |
| Safety | Include harm avoidance and confidentiality instructions in all external-facing prompts |
| Temperature | Analytical tasks: 0.0–0.3; Creative tasks: 0.7–1.0; Code generation: 0.0–0.2 |
| Token budget | Set `max_tokens` based on expected output length + 20% buffer |
| No prompt injection | Never interpolate untrusted user input directly into system prompt |

---

## Model Selection Guide

| Task Type | Preferred Model | Fallback |
|---|---|---|
| Complex reasoning, code generation | claude-sonnet-4-6 | claude-opus-4-6 |
| High-stakes decisions | claude-opus-4-6 | Human escalation |
| High-volume classification | claude-haiku-4-5 | Local LoRA (if benchmarked) |
| Local / offline | LoRA-adapted Llama (via Ollama) | claude-haiku-4-5 via API |