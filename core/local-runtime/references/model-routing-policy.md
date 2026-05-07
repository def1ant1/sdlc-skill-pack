# Model Routing Policy

Used by `core/local-runtime/SKILL.md` to determine which model and backend to use
for a given inference request, based on task type, VRAM availability, and latency needs.

---

## Task-to-Model Routing Table

| Task Type | Primary Model | Backend | Quantization | VRAM (approx) | Latency |
|---|---|---|---|---|---|
| Code generation (complex) | Qwen2.5-Coder-32B-Instruct | vLLM | AWQ | 20 GB | medium |
| Code generation (fast) | Qwen2.5-Coder-7B-Instruct | Ollama | Q4_K_M | 5 GB | fast |
| Reasoning / analysis (deep) | Qwen2.5-72B-Instruct | vLLM | AWQ | 40 GB | slow |
| Reasoning / analysis (fast) | Qwen2.5-32B-Instruct | vLLM | AWQ | 20 GB | medium |
| Summarization | Qwen2.5-14B-Instruct | Ollama | Q5_K_M | 10 GB | medium |
| Structured JSON output | Qwen2.5-14B-Instruct | SGLang | BF16 | 28 GB | medium |
| Tool calling / function use | Qwen2.5-72B-Instruct | vLLM | FP8 | 70 GB | slow |
| Embedding / retrieval | Qwen-Embedding-3 | Ollama | FP16 | 2 GB | fast |
| Long-context (>32K tokens) | Qwen2.5-72B-Instruct | vLLM | FP8 | 70 GB | slow |
| Quick routing / classification | Qwen2.5-7B-Instruct | Ollama | Q4_K_M | 5 GB | very fast |
| Strategic synthesis (highest quality) | claude-sonnet-4-6 | Anthropic API (cloud) | — | 0 GB | cloud |
| Cloud fallback (default) | claude-haiku-4-5-20251001 | Anthropic API (cloud) | — | 0 GB | cloud |

---

## VRAM Budget Tiers

| Available VRAM | Tier | Max Model Size | Recommended Backend |
|---|---|---|---|
| < 8 GB | minimal | 7B Q4 | llama.cpp |
| 8–20 GB | constrained | 14B Q4 | Ollama |
| 20–40 GB | standard | 32B AWQ | vLLM or Ollama |
| 40–80 GB | full | 72B AWQ | vLLM |
| 80–128 GB | extended | 72B FP8 + secondary model | vLLM (multi-model) |

---

## Quantization Fallback Chain

When the primary quantization level cannot fit in available VRAM, fall back in order:

```
FP16 → BF16 → AWQ → FP8 → GPTQ → Q8_0 → Q6_K → Q5_K_M → Q4_K_M → Q3_K_M → Q2_K
```

If Q2_K does not fit, fall back to a smaller model (e.g. 72B → 32B → 14B → 7B).
If no local model fits, route to cloud fallback.

---

## Cloud Fallback Rules

Cloud fallback is permitted when:

1. All local backends report unhealthy or insufficient VRAM
2. The task requires capabilities not available locally (e.g., very long context > 200K tokens)
3. The operator has explicitly requested cloud routing

Cloud fallback is **NOT** permitted when:

- The request contains PII, PHI, or confidential customer data (requires local-security approval first)
- The workspace is configured with `cloud_fallback: disabled`
- The request is already in a fallback chain (no cloud-to-cloud re-routing)

---

## Latency Classes

| Class | Max Time-to-First-Token | Use Case |
|---|---|---|
| `real-time` | < 500ms | Interactive chat, streaming UI |
| `interactive` | < 5s | Tool calls, assistant responses |
| `batch` | < 60s | Document analysis, code review |
| `async` | No limit | Long-running workflows, background tasks |

The latency class is declared by the requesting skill. If undeclared, assume `interactive`.
Real-time requests always route to the fastest available model, ignoring quality preferences.

---

## Model Selection Algorithm

```
1. Get task_type, input_tokens, output_tokens_est, latency_class, allow_cloud
2. Look up primary model from routing table
3. Check: does primary model fit in available VRAM?
   YES → Check: is backend healthy?
         YES → Use primary model
         NO  → Apply quantization fallback chain
   NO  → Apply quantization fallback chain
         Still no fit? → Use smaller model
         Still no fit? → Route to cloud (if allow_cloud and allowed by policy)
4. Log routing decision with rationale
```