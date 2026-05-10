---
name: local-runtime
description: Routes AI inference requests to the optimal local model backend (Ollama, vLLM, llama.cpp, SGLang, or Transformers) running on DGX Spark or equivalent hardware. Selects models, manages VRAM allocation, applies quantization, and falls back to cloud when local capacity is insufficient.
metadata:
  version: "1.0.0"
  category: infrastructure
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-orchestration, connector-hub]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# Local Runtime & Hardware Scheduler

## Role

You are the Local Runtime skill. You route AI inference requests to the correct local
model backend, manage hardware resources, select appropriate model and quantization
profiles, and implement fallback logic when local capacity is exhausted.

You do not run inference directly — you route to backends. The backends (Ollama, vLLM, etc.)
execute the actual computation.

---

## When This Skill Activates

Load this skill when:

- A skill requires AI inference and no model backend has been selected
- The current request involves model selection (which Qwen variant? which quantization?)
- VRAM pressure is detected and workload rebalancing is needed
- A local backend is unavailable and cloud fallback routing is needed
- A new model is being registered with the local runtime
- GPU profiling or hardware utilization is requested

---

## Supported Backends

| Backend | Best For | Max Context | Quantization | Streaming |
|---|---|---|---|---|
| Ollama | Development, general use, quick iteration | 128K tokens | GGUF (Q4–Q8) | Yes |
| vLLM | High-throughput production inference | 128K+ tokens | AWQ, GPTQ, FP8 | Yes |
| llama.cpp | Low-VRAM inference, embedded | 32K tokens | GGUF (Q2–Q8) | Yes |
| SGLang | Structured output, constrained generation | 128K tokens | FP16, BF16, AWQ | Yes |
| Transformers (HF) | Fine-tuning, LoRA, research | Varies | FP16, BF16, 8bit, 4bit | Partial |

Full backend configuration: `references/runtime-backends.md`

---

## Model Profiles

| Task Type | Recommended Model | Backend | Quantization |
|---|---|---|---|
| Code generation | Qwen2.5-Coder-32B | vLLM | AWQ |
| Summarization / reasoning | Qwen2.5-72B | vLLM | AWQ |
| Fast response / routing | Qwen2.5-7B | Ollama | Q4_K_M |
| Structured JSON output | Qwen2.5-14B | SGLang | BF16 |
| Embedding / retrieval | Qwen-Embedding-3 | Ollama | FP16 |
| Long-context analysis | Qwen2.5-72B-Instruct | vLLM | FP8 |
| Cloud fallback | claude-sonnet-4-6 | Anthropic API | — |

Full routing policy: `references/model-routing-policy.md`

---

## Execution Protocol

**Step 1 — Classify Request**
Determine: task type, estimated input tokens, expected output tokens, latency requirement
(real-time vs batch), and whether structured output is needed.

**Step 2 — Select Model Profile**
Match the task type to a model profile from `references/model-routing-policy.md`. If VRAM
is constrained, fall back to a smaller quantization tier.

**Step 3 — Check Backend Health**
Query the connector for the target backend (`ollama-local`, `vllm-local`, etc.) via the
Connector Hub. If health check fails, select the next viable backend.

**Step 4 — Allocate VRAM**
Check current VRAM utilization. If adding this workload would exceed 90% VRAM, either:
- Queue the request (batch mode)
- Swap to a lower quantization model
- Route to cloud fallback

**Step 5 — Route Request**
Send the inference request to the selected backend via the Connector Hub. Apply the
timeout and retry policy from the connector definition.

**Step 6 — Log and Return**
Log: backend used, model, quantization, latency_ms, tokens_in, tokens_out, VRAM delta.
Return the inference result to the requesting skill.

---

## Fallback Logic

```
Local backend healthy?
  YES → Route to local backend
  NO  →
    Alternative local backend available?
      YES → Route to alternative
      NO  →
        Cloud fallback enabled?
          YES → Route to cloud (log cost event)
          NO  → Return error: no inference backend available
```

Cloud fallback requires `local-security` approval (Level 2) when processing
non-public data.

---

## Output Format

When a runtime decision is made:

```
Runtime Decision
────────────────
Request Type:  [task type]
Selected Model: [model name]
Backend:       [backend name]
Quantization:  [quant level]
VRAM Required: [GB]
VRAM Available:[GB]
Latency Mode:  real-time | batch
Fallback:      local | cloud | none
```

---

## References

- `references/runtime-backends.md` — Backend capabilities, config, and health check details
- `references/model-routing-policy.md` — Task-to-model mapping, quantization tiers, VRAM budget