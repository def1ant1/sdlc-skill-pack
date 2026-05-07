---
name: synthetic-dataset-generation
description: Generates high-quality synthetic datasets for model training, evaluation, and fine-tuning by synthesizing diverse, realistic examples with controlled distributions and ground truth labels.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [benchmark-factory, synthetic-data, model-lifecycle, data-fabric]
---

## Role

Synthetic dataset generation specialist. Creates training, fine-tuning, and evaluation datasets
by synthesizing realistic examples with controlled quality and distribution properties. Generates
data that covers target capability distributions without requiring manual annotation at scale.

## Activation Triggers

- Fine-tuning dataset required for a new capability area
- Evaluation dataset requires augmentation for underrepresented cases
- Rare-event coverage needed that real data cannot provide
- Privacy-preserving training data required to replace PII-containing real data

## Execution Protocol

1. **Define generation specification**: Specify dataset purpose (training/eval), capability area,
   target distribution (difficulty, input type, domain coverage), size, and quality criteria.

2. **Design generation prompts**: Author prompt templates that reliably produce high-quality
   examples in the target format; include few-shot demonstrations.

3. **Generate candidate examples**: Run generation in parallel batches using the highest-quality
   available model; collect raw candidate dataset.

4. **Apply quality filters**: Remove: malformed examples, duplicates, near-duplicates (>80%
   similarity), examples violating the ground truth schema, and PII-containing outputs.

5. **Balance distribution**: Measure actual distribution across specified dimensions; resample
   or generate additional examples to achieve target distribution balance.

6. **Register and package**: Write curated dataset to data-fabric with full lineage metadata;
   register in benchmark-factory if evaluation dataset; export in target format (JSONL/Parquet).

## Output Format

Synthetic dataset package with: JSONL/Parquet data file, metadata card (purpose, size, distribution,
generation model, quality filter pass rate), and data lineage record.

## References

- `references/generation-prompt-templates.md` — prompt templates by capability area, quality filter criteria, distribution measurement methodology