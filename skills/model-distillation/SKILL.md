---
name: model-distillation
description: Transfers knowledge from large teacher models to smaller student models through structured distillation, producing quantifiably capable local inference models with validated quality retention.
metadata:
  version: "1.0.0"
  category: model-lifecycle
  owner: platform
  maturity: alpha
  dependencies: [model-lifecycle, benchmark-factory, dataset-curation, telemetry]
---

## Role

Teacher-to-student knowledge transfer orchestrator for the model lifecycle. Manages the
full distillation pipeline — training data generation via teacher inference, student training
with knowledge distillation loss, and rigorous capability validation — producing smaller
models suitable for local or edge deployment.

## Activation Triggers

- Model-lifecycle identifies a capability tier where local inference would improve cost-efficiency
- Federated-runtime requires a locally deployable model for an air-gapped deployment
- Operator initiates a distillation project for a specific capability domain
- Model-routing overflow policy requires a local fallback model for a capability

## Execution Protocol

1. **Define distillation scope**: Specify the teacher model, target student architecture,
   capability domains to transfer, and acceptable quality floor (minimum benchmark retention %).

2. **Generate distillation dataset**: Run teacher model inference over curated prompts for
   the target capability domains; collect (input, teacher output, teacher logits) triples;
   apply dataset-curation for quality filtering.

3. **Configure distillation training**: Set knowledge distillation loss weight (soft target
   loss + hard target cross-entropy); configure temperature scaling for logit softening;
   set student training hyperparameters.

4. **Train student model**: Execute training run; monitor distillation loss convergence and
   capability benchmark scores at checkpoints; apply early stopping if benchmark scores plateau.

5. **Validate capability retention**: Run full benchmark suite comparing teacher and student;
   compute capability retention rate per domain; flag any domain below the quality floor.

6. **Register student model**: Submit to model-lifecycle with distillation provenance, capability
   retention metrics, and deployment tier recommendation.

## Output Format

Distillation report with: `teacher_model_id`, `student_model_id`, `capability_domains` (list),
`parameter_reduction` (%), `capability_retention_rate` (per domain and overall), `benchmark_scores`
(teacher vs. student), and deployment tier recommendation.

## References

- `references/distillation-protocol.md` — distillation loss configuration, temperature scaling guide, quality floor thresholds