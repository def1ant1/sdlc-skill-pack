---
name: quantization-optimization
description: Applies INT4/INT8/GPTQ/AWQ quantization to reduce model size and inference latency while validating quality retention against capability benchmarks before production deployment.
metadata:
  version: "1.0.0"
  category: model-lifecycle
  owner: platform
  maturity: alpha
  dependencies: [model-lifecycle, benchmark-factory, cluster-management, telemetry]
---

## Role

Model quantization pipeline manager for the model lifecycle. Selects the optimal
quantization scheme for a model's deployment target, applies quantization with calibration
data, validates quality retention, and produces a deployment-ready quantized artifact
registered in the model registry.

## Activation Triggers

- Model-lifecycle flags a model as too large for target deployment hardware
- Cluster-management reports VRAM budget exceeded for a model placement
- Operator requests quantization of a specific model for edge or local deployment
- Model-routing requires a lower-resource variant of a model for cost optimization

## Execution Protocol

1. **Assess quantization requirements**: Determine target hardware constraints (VRAM, compute
   type), acceptable quality floor (minimum benchmark retention %), and latency targets.

2. **Select quantization scheme**: Choose based on target and quality requirements — INT8
   (minimal quality loss, broad hardware support), GPTQ (good quality/size balance, GPU),
   AWQ (activation-aware, better quality retention), INT4 (maximum compression, edge).

3. **Prepare calibration data**: Curate a representative calibration dataset covering the
   model's primary use cases; quality of calibration data directly impacts quantization quality.

4. **Apply quantization**: Execute the selected quantization algorithm with calibration data;
   record quantization parameters, layer-wise sensitivity scores, and output artifact metadata.

5. **Validate quality retention**: Run full benchmark suite on quantized model; compute quality
   retention rate per capability domain; flag any domain below the quality floor threshold.

6. **Register quantized artifact**: Submit to model-lifecycle with quantization scheme, compression
   ratio, quality retention metrics, and hardware compatibility matrix.

## Output Format

Quantization report with: `source_model_id`, `quantized_model_id`, `scheme` (INT4/INT8/GPTQ/AWQ),
`compression_ratio` (%), `vram_reduction` (%), `quality_retention_rate` (per domain and overall),
`latency_improvement` (%), and hardware compatibility matrix.

## References

- `references/quantization-schemes.md` — scheme comparison, calibration data requirements, quality floor thresholds, hardware compatibility matrix