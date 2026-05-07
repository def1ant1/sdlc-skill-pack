# Benchmark Catalog

Used by `core/model-evaluation/SKILL.md` to define all benchmark suites, their
evaluation prompts, scoring methods, and applicability by use case.

---

## Standard Benchmarks

### MMLU (Massive Multitask Language Understanding)
- **Measures**: General knowledge and reasoning across 57 subjects
- **Format**: 4-choice multiple choice
- **Scoring**: Accuracy (% correct)
- **Use for**: General reasoning capability baseline
- **Prompt format**: `"The following is a multiple choice question...\nAnswer: "`
- **Pass threshold**: Model-size dependent (70B: ≥ 78%, 32B: ≥ 72%, 7B: ≥ 60%)

### HumanEval
- **Measures**: Python code generation; tests run to verify correctness
- **Format**: Function signature + docstring → complete the function
- **Scoring**: Pass@1 (% of solutions passing all unit tests on first attempt)
- **Use for**: Code generation models
- **Pass threshold**: ≥ 70% for production coding use

### IFEval (Instruction Following Evaluation)
- **Measures**: Adherence to explicit formatting and constraint instructions
- **Format**: Natural language instructions with verifiable output constraints
- **Scoring**: Prompt-level accuracy and instruction-level accuracy
- **Use for**: Any model used for structured output, skill execution, tool calling
- **Pass threshold**: ≥ 85% instruction-level accuracy

### TruthfulQA
- **Measures**: Tendency to generate false but plausible-sounding answers
- **Format**: Open-ended questions where common misconceptions exist
- **Scoring**: % of truthful responses (lower score = more hallucination)
- **Use for**: Hallucination baseline measurement
- **Pass threshold**: ≥ 80% truthful

---

## Custom Apotheon Suites

### Tool-Call Accuracy Suite
- **Measures**: Correct tool selection and parameter formatting for Apotheon skills
- **Format**: 50 scenarios requiring tool invocation; scored on correct tool + correct params
- **Scoring**: Tool selection accuracy × parameter accuracy
- **Use for**: Any model used for orchestration or skill delegation
- **Pass threshold**: ≥ 90% combined accuracy

### Long-Context Fidelity Suite
- **Measures**: Accuracy when the context window is 50–80% full with relevant documents
- **Format**: Insert 20K–50K tokens of context; ask 10 questions answerable only from context
- **Scoring**: % of questions answered correctly from context (not hallucinated)
- **Use for**: Models used for long-document workflows, code analysis
- **Pass threshold**: ≥ 80% at 50% fill; ≥ 65% at 80% fill

### RAG Hallucination Suite
- **Measures**: Rate of hallucination when a retrieval context is provided
- **Format**: Provide 5 retrieved chunks; ask a question where the answer is in the chunks; measure if model invents facts not in chunks
- **Scoring**: % of responses containing only context-grounded facts
- **Use for**: Any model used with VectorRAG or GraphRAG
- **Pass threshold**: ≤ 5% hallucination rate (≥ 95% grounded)

### Orchestration Benchmark
- **Measures**: Intent classification accuracy against the Apotheon orchestration fixture
- **Format**: 30 benchmark prompts from `tests/fixtures/orchestration-prompts.json`
- **Scoring**: % of prompts classified to correct SDLC phase
- **Use for**: Models used as the orchestration control plane brain
- **Pass threshold**: ≥ 90% accuracy (matches existing regression suite)

---

## Benchmark Selection by Use Case

| Use Case | Required Benchmarks | Optional |
|---|---|---|
| General reasoning | MMLU, IFEval | TruthfulQA |
| Code generation | HumanEval, IFEval | MBPP |
| Orchestration / routing | Orchestration Benchmark, IFEval | MMLU |
| Tool calling | Tool-Call Accuracy, IFEval | — |
| Long-document analysis | Long-Context Fidelity, TruthfulQA | RAG Hallucination |
| RAG / retrieval | RAG Hallucination, TruthfulQA | Long-Context Fidelity |
| Full production promotion | All core benchmarks | — |

---

## Latency Benchmarks

| Test | Method | Target (DGX Spark) |
|---|---|---|
| Time-to-first-token (TTFT) | Single request, 500-token prompt | < 500ms |
| Tokens per second (throughput) | Single stream, 2000-token completion | > 30 tok/s |
| Concurrent throughput | 4 concurrent requests | > 20 tok/s per request |
| Long-prompt TTFT | 8K-token prompt, 500-token completion | < 3s |