# Runtime Backends

Used by `core/local-runtime/SKILL.md` to define available local inference backends,
their capabilities, configuration requirements, and health check specifications.

---

## Ollama

| Property | Value |
|---|---|
| Port | 11434 |
| API | REST (OpenAI-compatible) |
| Health check | `GET http://localhost:11434/api/tags` |
| Model format | GGUF |
| Quantization | Q2_K, Q3_K_M, Q4_K_M, Q5_K_M, Q6_K, Q8_0 |
| Max context | Model-dependent (up to 128K with context extension) |
| Streaming | Yes (`/api/generate`, `/api/chat`) |
| Concurrency | 1 request by default; increase with `OLLAMA_NUM_PARALLEL` |
| Best for | Development, general use, quick iteration, embeddings |

**Connector ID**: `ollama-local`

**Start command**: `ollama serve`

**Model management**:
```bash
ollama pull qwen2.5:7b         # Pull 7B model
ollama pull qwen2.5:72b-q4_k_m # Pull 72B at Q4 quantization
ollama list                     # List loaded models
ollama rm qwen2.5:7b            # Remove model
```

---

## vLLM

| Property | Value |
|---|---|
| Port | 8000 |
| API | OpenAI-compatible REST |
| Health check | `GET http://localhost:8000/health` |
| Model format | HuggingFace (AWQ, GPTQ, FP8, BF16) |
| Quantization | AWQ, GPTQ, FP8, BF16, FP16 |
| Max context | Model-dependent (128K+ with chunked prefill) |
| Streaming | Yes (SSE) |
| Concurrency | High (continuous batching) |
| Best for | Production throughput, multi-user serving |

**Connector ID**: `vllm-local`

**Start command**:
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --quantization awq \
  --gpu-memory-utilization 0.90 \
  --max-model-len 32768
```

---

## llama.cpp (llama-server)

| Property | Value |
|---|---|
| Port | 8080 |
| API | REST (OpenAI-compatible via llama-server) |
| Health check | `GET http://localhost:8080/health` |
| Model format | GGUF |
| Quantization | Q2_K through Q8_0 |
| Max context | 32K (configurable, VRAM-dependent) |
| Streaming | Yes |
| Concurrency | Low (1–4 slots) |
| Best for | Very low VRAM, CPU fallback, embedded use |

**Connector ID**: `llamacpp-local`

---

## SGLang

| Property | Value |
|---|---|
| Port | 30000 |
| API | REST + JSON schema enforcement |
| Health check | `GET http://localhost:30000/health` |
| Model format | HuggingFace (BF16, AWQ, FP8) |
| Quantization | FP16, BF16, AWQ, FP8 |
| Max context | 128K |
| Streaming | Yes |
| Concurrency | High (RadixAttention cache) |
| Best for | Structured JSON output, constrained generation, tool calling |

**Connector ID**: `sglang-local`

---

## Transformers (HuggingFace)

| Property | Value |
|---|---|
| Interface | Python library (no HTTP server) |
| Model format | HuggingFace checkpoint |
| Quantization | FP16, BF16, 8-bit (bitsandbytes), 4-bit (GGUF via llama.cpp) |
| Streaming | Partial (with `TextStreamer`) |
| Best for | Fine-tuning, LoRA, research, non-served inference |

**Note**: Not exposed via connector; called directly from Python scripts.

---

## Backend Selection Priority

When multiple backends are healthy:

1. **vLLM** — prefer for production, high-throughput, multi-user
2. **SGLang** — prefer when structured JSON output is required
3. **Ollama** — prefer for development, single-user, embedding tasks
4. **llama.cpp** — fallback when VRAM < 8GB or backends 1–3 are down
5. **Cloud** — final fallback when all local backends are unavailable

---

## DGX Spark Hardware Reference

| Spec | Value |
|---|---|
| GPU | NVIDIA GB10 Superchip (Grace Blackwell) |
| GPU Memory | 128 GB unified (NVLink-C2C) |
| CPU | 20-core ARM Neoverse N2 |
| RAM | 128 GB LPDDR5X |
| Storage | 4 TB NVMe |
| Thermal | Fanless (passive cooling) |
| Power | 60W TDP |

**VRAM allocation targets**:
- Reserve 10 GB for OS and overhead
- Allocate up to 90% of remaining (≈105 GB) for model inference
- 72B model at Q4_K_M ≈ 40 GB VRAM — two can run simultaneously
- 32B model at AWQ ≈ 20 GB VRAM — four can run simultaneously