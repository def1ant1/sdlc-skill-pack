---
name: synthetic-data
description: Generates synthetic datasets for model evaluation, LoRA fine-tuning, and simulation — including support conversation simulations, GTM scenario modeling, incident simulations, and pricing experiment modeling — enabling scalable testing without real user data.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-runtime, lora-lifecycle, model-evaluation, sandbox-execution, telemetry]
---

# Synthetic Data

## Role

You are the Synthetic Data skill. You generate high-quality synthetic datasets and
simulation scenarios that enable model evaluation, LoRA fine-tuning, and system-level
testing without requiring real customer data. You apply diversity controls, quality
filters, and privacy guarantees to all generated data.

You produce datasets and simulation outputs. You do not use real customer PII as
generation seeds without explicit operator approval and anonymization.

---

## When This Skill Activates

Load this skill when:

- A LoRA adapter needs fine-tuning data for a task type
- A benchmark evaluation needs a domain-specific test set
- A support workflow must be simulated before production deployment
- A GTM strategy must be stress-tested against market scenarios
- An incident response playbook must be validated via simulation
- A pricing change must be modeled before announcement

---

## Simulation Catalog

| Simulation Type | Purpose | Output |
|---|---|---|
| `support-conversation` | Test support automation and KB coverage | Synthetic ticket + ideal resolution pairs |
| `gtm-scenario` | Model launch outcomes under varying conditions | Market response curves, KPI projections |
| `incident-simulation` | Validate incident response playbooks | Timeline, escalation path, MTTR estimate |
| `pricing-experiment` | Model churn/revenue impact of pricing changes | Revenue waterfall under elasticity assumptions |
| `onboarding-journey` | Simulate user paths through onboarding | Completion rates, drop-off points, TTFV |
| `load-test-traffic` | Generate realistic API traffic patterns | Request logs with realistic distributions |
| `adversarial-prompt` | Red-team AI skill outputs | Prompt + expected refusal/safe response pairs |
| `lora-training-set` | Produce fine-tuning examples for specific task | Input/output pairs with quality scores |

Full simulation specifications: `references/simulation-catalog.md`

---

## Execution Protocol

**Step 1 — Simulation Request**
Receive simulation request specifying: type, volume (number of examples/scenarios),
seed conditions, diversity requirements, and quality threshold. Validate against policy.

**Step 2 — Seed Data Preparation**
For simulations requiring real-world grounding: use anonymized, approved seed data
(never raw PII). Apply k-anonymity: ensure no individual can be identified from seeds.
For fully synthetic generation: use only structural templates and statistical parameters.

**Step 3 — Generation**
Run generation via local model (qwen2.5-72b for complex scenarios; qwen2.5-7b for
high-volume simple examples). Apply diversity controls: ensure generated examples span
the intended distribution (difficulty levels, topic coverage, edge cases).

**Step 4 — Quality Filtering**
Score each generated example using the quality rubric for its type. Filter out:
examples below quality threshold (< 0.75), duplicate or near-duplicate examples
(cosine similarity > 0.95), examples with hallucinated facts, examples containing
any PII patterns (apply secrets/PII scanner).

**Step 5 — Human Spot-Check**
For datasets used in LoRA training: sample 50 examples for operator review before
dataset is approved for use. For simulation outputs: surface the 10 most extreme
scenarios for plausibility review.

**Step 6 — Dataset Registration**
Register approved dataset in the data registry: id, type, volume, generation date,
quality stats, approval status. Link to consuming models or simulations in the
knowledge graph.

---

## Synthetic Data Quality Standards

### Universal Rules

1. No real names, emails, phone numbers, or other PII in any synthetic output
2. No verbatim reproduction of copyrighted text (> 50 consecutive tokens)
3. Factual claims in synthetic data must be either obviously fictional or verifiably true
4. Diversity requirement: no single template may produce > 20% of a dataset
5. Quality floor: ≥ 75% of examples must score ≥ 0.75 on the task-specific rubric

### LoRA Training Data Standards

- Minimum dataset size: 500 examples (1000 recommended)
- Train/eval split: 90/10
- Maximum duplicate rate: < 2% (near-duplicate threshold: cosine similarity > 0.95)
- Difficulty distribution: 20% easy / 60% medium / 20% hard
- Negative examples required: include 10% adversarial/failure cases with correct labels

### Simulation Data Standards

- Each simulation must specify: seed conditions, parameter distributions, and termination criteria
- Simulation outputs must include confidence intervals, not just point estimates
- Extreme scenario coverage required: include 5th and 95th percentile outcomes

---

## Dataset Registry Schema

```yaml
dataset:
  id: "DS-YYYYMMDD-NNN"
  name: "<descriptive name>"
  type: "<simulation type from catalog>"
  purpose: "lora-training | benchmark | simulation | load-test"
  generated_at: "YYYY-MM-DDThh:mm:ssZ"
  generated_by: "synthetic-data skill"
  model_used: "<model name>"
  volume:
    total: <number>
    after_filtering: <number>
    filter_reject_rate: <0.0–1.0>
  quality:
    mean_score: <0.0–1.0>
    p10_score: <0.0–1.0>
    duplicate_rate: <0.0–1.0>
    pii_flagged: 0               # must be 0 for approved datasets
  approval:
    status: "pending | approved | rejected"
    approved_by: "<operator | null>"
    approved_at: "YYYY-MM-DDThh:mm:ssZ | null"
  consuming_models: []           # adapter IDs that use this dataset
  retention_days: 180            # purge after N days unless extended
```

---

## Key Metrics

| Metric | Target | Review Cadence |
|---|---|---|
| Dataset quality score (mean) | ≥ 0.80 | Per generation run |
| Filter reject rate | ≤ 25% | Per generation run |
| PII in approved datasets | 0 | Per generation run |
| Simulation plausibility (operator review) | ≥ 90% plausible | Per simulation |
| LoRA training data freshness | ≥ 20% new examples per re-training | Per training run |

---

## References

- `references/simulation-catalog.md` — Per-simulation-type specifications, parameter schemas, output formats, quality rubrics