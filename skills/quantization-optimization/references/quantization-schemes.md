# Quantization Schemes Reference

## Scheme Comparison Table

| Scheme | Bits | Size Reduction | Quality Retention | Hardware Support | Best For |
|---|---|---|---|---|---|
| FP16 | 16 | ~50% vs FP32 | 99%+ | All modern GPUs | Default inference |
| BF16 | 16 | ~50% vs FP32 | 99%+ | Ampere+, TPUs | Training and inference |
| INT8 | 8 | ~75% vs FP32 | 97–99% | All GPUs (cuBLAS) | Good balance; production default |
| GPTQ | 4 (int4) | ~87% vs FP32 | 92–96% | GPU (CUDA) | GPU deployment; good quality |
| AWQ | 4 (int4) | ~87% vs FP32 | 94–97% | GPU (CUDA) | Better quality than GPTQ at same size |
| INT4 (naive) | 4 | ~87% vs FP32 | 85–92% | Broad | Edge/mobile when size is critical |
| GGUF Q4_K_M | 4 mixed | ~85% vs FP32 | 93–95% | CPU + Apple Silicon | Local/edge inference on CPU |
| GGUF Q8_0 | 8 | ~75% vs FP32 | 98%+ | CPU + Apple Silicon | CPU inference, higher quality |

---

## Calibration Data Requirements

Calibration data is used to minimize quantization error by observing actual activation distributions.

| Scheme | Calibration Required | Recommended Calibration Size | Data Characteristics |
|---|---|---|---|
| INT8 (dynamic) | No | N/A | Dynamic per-token scaling |
| INT8 (static) | Yes | 128–512 samples | Representative of deployment inputs |
| GPTQ | Yes | 128–512 samples | Dataset that reflects target use cases |
| AWQ | Yes | 32–128 samples | Smaller dataset; uses activation-aware selection |
| INT4 (naive) | No | N/A | Symmetric quantization; no calibration |

**Calibration data selection:**
- Must be representative of the model's primary deployment use case
- Should include edge-case inputs (long context, technical vocabulary, non-English)
- Must NOT include test/evaluation data (contamination risk)
- Recommended: use a curated 256-sample subset from the production request distribution

---

## Quality Floor Thresholds

These thresholds define the minimum acceptable quality retention by capability tier:

| Capability Tier | Quality Floor (benchmark retention) | Recommended Scheme |
|---|---|---|
| Reasoning | 97% of FP16 baseline | INT8 or BF16 only |
| Advanced | 95% of FP16 baseline | INT8, GPTQ (Q4_K_M equivalent) |
| Standard | 92% of FP16 baseline | GPTQ, AWQ |
| Micro | 88% of FP16 baseline | AWQ, INT4 |
| Nano | 85% of FP16 baseline | INT4, GGUF Q4_K_M |

**Measurement:** Quality floor is measured by running the full capability benchmark suite
on the quantized model and computing the retention rate: `quantized_score / fp16_score`.

---

## Hardware Compatibility Matrix

| Scheme | NVIDIA A100/H100 | NVIDIA RTX 4090 | AMD MI300 | Apple M-series | Intel CPU |
|---|---|---|---|---|---|
| FP16/BF16 | Native | Native | Native | Native (MPS) | FP32 fallback |
| INT8 | cuBLAS | cuBLAS | ROCm | CoreML | VNNI (limited) |
| GPTQ | ExLlama v2 | ExLlama v2 | Limited | No | No |
| AWQ | AutoAWQ | AutoAWQ | Limited | No | No |
| GGUF | llama.cpp | llama.cpp | llama.cpp | llama.cpp (METAL) | llama.cpp |

---

## Quantization Execution Protocol

```
1. ASSESS: Determine target hardware, VRAM budget, and quality floor
2. SELECT: Choose scheme from compatibility matrix and quality table
3. PREPARE: Curate 128–512 calibration samples from production request distribution
4. QUANTIZE: Run quantization tool with calibration data:
   - INT8: bitsandbytes or AutoGPTQ with calibration dataset
   - GPTQ: AutoGPTQ with wbits=4, groupsize=128
   - AWQ: AutoAWQ with w_bit=4, q_group_size=128
5. VALIDATE: Run full benchmark suite; compute quality retention rate
6. COMPARE: If quality_retention < floor → try INT8 or increase bits
7. REGISTER: Submit quantized artifact to model-lifecycle with provenance
```

---

## Layer-Wise Sensitivity Analysis

Not all model layers are equally sensitive to quantization. Standard practice:

- First and last transformer layers: keep in FP16 (most sensitive to quantization)
- Attention layers: quantize carefully; test with INT8 before INT4
- MLP/FFN layers: most tolerant; safe for INT4
- Embedding layers: typically kept in FP16 or INT8

GPTQ and AWQ automatically perform per-layer sensitivity analysis; report the
`layer_sensitivity_scores` as part of the quantization artifact metadata.