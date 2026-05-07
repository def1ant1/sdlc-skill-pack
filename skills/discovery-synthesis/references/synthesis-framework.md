# Discovery Synthesis Framework Reference

## Synthesis Process Overview

Discovery synthesis transforms raw findings from multiple sources (literature reviews, research analyses, experiments, interviews) into coherent, actionable knowledge.

```
INPUT: Multiple raw findings from heterogeneous sources
PROCESS: Evidence integration → Pattern recognition → Claim formation → Gap identification
OUTPUT: Synthesized knowledge with evidence grades and research gap map
```

---

## Evidence Integration Protocol

### Step 1: Finding Normalization

Convert all findings to a standard format:

```yaml
normalized_finding:
  finding_id: "FND-LR-042"
  source_id: "PAPER-Smith2024"
  source_type: "empirical_study"  # empirical_study | review | expert_opinion | grey_literature

  claim: "Quantization to INT8 reduces inference latency by 45% with < 2% accuracy loss"

  evidence_attributes:
    study_design: "controlled_experiment"
    sample_size: "5 benchmark datasets, 3 model families"
    effect_size: "45% latency reduction, 1.8% accuracy drop"
    conditions: "INT8 symmetric quantization, NVIDIA A100"
    replication_status: "replicated_by_3_independent_teams"

  evidence_grade: "B"  # A | B | C | D | I (see grading rubric)
  confidence: 0.82
  limitations:
    - "Results may not generalize to non-transformer architectures"
    - "Hardware-specific — A100 has native INT8 support"
```

### Step 2: Finding Clustering

Group findings into thematic clusters:

```python
def cluster_findings(findings, similarity_threshold=0.75):
    """
    Cluster findings by semantic similarity of their claims.
    Each cluster becomes a candidate synthesis theme.
    """
    embeddings = [embed(f.claim) for f in findings]
    similarity_matrix = cosine_similarity(embeddings)

    # Agglomerative clustering
    clusters = AgglomerativeClustering(
        distance_threshold=1 - similarity_threshold,
        linkage="average"
    ).fit(1 - similarity_matrix)

    return group_by_label(findings, clusters.labels_)
```

---

## Synthesis Patterns

### Pattern 1: Convergent Synthesis

When multiple independent findings support the same claim:

```
Convergence check:
  N_supporting = count(findings with direction == "supports")
  N_opposing = count(findings with direction == "opposes")
  N_neutral = count(findings with direction == "neutral")

  convergence_ratio = N_supporting / (N_supporting + N_opposing)

  IF convergence_ratio ≥ 0.80 AND N_supporting ≥ 3:
    SYNTHESIZED CLAIM: "Strong evidence supports [claim]"
    EVIDENCE GRADE: escalate to A if ≥ 1 RCT or systematic review supports
  ELIF convergence_ratio ≥ 0.60:
    SYNTHESIZED CLAIM: "Moderate evidence suggests [claim]"
    EVIDENCE GRADE: B
  ELSE:
    SYNTHESIZED CLAIM: "Conflicting evidence — see divergent synthesis"
```

### Pattern 2: Divergent Synthesis

When findings conflict — identify the conditions under which each holds:

```yaml
divergent_synthesis:
  base_claim: "Quantization improves inference efficiency"

  finding_cluster_A:
    finding_ids: [FND-001, FND-003, FND-007]
    conditions: "INT8 quantization, Transformer architecture, GPU inference"
    conclusion: "45-60% latency improvement with < 2% accuracy loss"
    confidence: HIGH

  finding_cluster_B:
    finding_ids: [FND-005, FND-009]
    conditions: "INT4 quantization, non-Transformer (LSTM), CPU inference"
    conclusion: "15-20% latency improvement with 8-12% accuracy loss"
    confidence: MEDIUM

  reconciled_claim: |
    Quantization benefits are highly architecture and precision dependent.
    INT8 on GPU Transformers: strong benefits.
    INT4 on CPU non-Transformers: modest latency, significant accuracy cost.

  moderating_variables: ["quantization_precision", "model_architecture", "hardware_type"]
```

### Pattern 3: Sequential Synthesis

Synthesize findings into an ordered process or development arc:

```
Use when: Findings describe stages of a process, historical development, or maturation curve.

Template:
  1. [Earliest finding]: [State at this stage]
  2. [Development finding]: [How state changed]
  3. [Current finding]: [Current state]
  4. [Projected finding]: [Where trajectory leads]

Evidence requirement: Each stage requires ≥ Grade B evidence.
```

---

## Research Gap Identification

```python
def identify_gaps(synthesized_claims, research_questions):
    gaps = []

    for rq in research_questions:
        # Check if research question is answered
        answering_claims = [
            c for c in synthesized_claims
            if semantic_similarity(c.claim, rq.question) > 0.70
        ]

        if not answering_claims:
            gaps.append(ResearchGap(
                gap_id=f"GAP-{rq.id}",
                gap_type="UNANSWERED_QUESTION",
                description=f"No evidence found for: {rq.question}",
                priority=rq.priority
            ))
        elif max(c.confidence for c in answering_claims) < 0.60:
            gaps.append(ResearchGap(
                gap_id=f"GAP-{rq.id}",
                gap_type="INSUFFICIENT_EVIDENCE",
                description=f"Low-confidence evidence for: {rq.question}",
                current_best_evidence=max(answering_claims, key=lambda c: c.confidence),
                priority="MEDIUM"
            ))

    return gaps
```

---

## Synthesis Output Format

```yaml
synthesis_report:
  report_id: "SYN-20260507-001"
  topic: "Quantization Methods for LLM Inference Optimization"
  synthesis_date: "2026-05-07"
  findings_synthesized: 24
  sources_reviewed: 18

  synthesized_claims:
    - claim_id: "SYN-CLAIM-001"
      claim: "INT8 quantization achieves 40-60% latency reduction on GPU inference
               with < 2% accuracy degradation for Transformer models ≥ 7B parameters"
      evidence_grade: "A"
      confidence: 0.88
      supporting_findings: [FND-001, FND-003, FND-007, FND-012]
      opposing_findings: []
      conditions: "INT8 symmetric quantization, GPU with INT8 tensor cores"

    - claim_id: "SYN-CLAIM-002"
      claim: "GPTQ outperforms naive INT4 quantization by 5-8 points on coding benchmarks"
      evidence_grade: "B"
      confidence: 0.72
      supporting_findings: [FND-009, FND-015]
      opposing_findings: [FND-019]  # One conflicting study

  research_gaps:
    - gap_id: "GAP-001"
      gap_type: "UNANSWERED_QUESTION"
      description: "No studies found on quantization impact for multimodal models"
      priority: "HIGH"
      recommended_study_design: "Controlled experiment on CLIP/Flamingo family"

  recommended_actions:
    - "Apply INT8 quantization to all production Transformer models ≥ 7B as default"
    - "Evaluate GPTQ for code generation models where INT4 is required"
    - "Commission study on multimodal quantization impact"
```