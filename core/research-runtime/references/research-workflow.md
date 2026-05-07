# Research Workflow Reference

## Overview

Defines the autonomous research lifecycle stages, stage gate criteria, artifact types
per stage, quality review protocol, and knowledge graph integration points.

---

## Research Lifecycle Stages

```
[Scoping] → [Literature Review] → [Hypothesis Generation] → [Experiment Design]
→ [Execution] → [Analysis] → [Synthesis] → [Publication]
```

---

## Stage Definitions and Gate Criteria

### Stage 1: Scoping

**Objective:** Define the research question, boundaries, and success criteria.

**Gate criteria to advance:**
- Research question stated in PICO or SPIDER format
- Scope boundaries documented (what is in/out of scope)
- Measurable success criteria defined
- Resource budget estimated and approved
- No equivalent completed research in the knowledge graph

**Artifacts produced:**
- Research brief (`research_brief.yaml`)
- Initial keyword list for literature search

---

### Stage 2: Literature Review

**Objective:** Establish evidence baseline and identify knowledge gaps.

**Gate criteria to advance:**
- Multi-source search completed (≥ 3 source databases)
- PRISMA-compliant screening documented
- ≥ 20 included sources (or documented justification for fewer)
- Evidence graded (Levels I–V per grading schema)
- At least 1 knowledge gap identified suitable for hypothesis formation

**Artifacts produced:**
- Literature review report (including gap analysis)
- Evidence synthesis matrix

---

### Stage 3: Hypothesis Generation

**Objective:** Formulate testable hypotheses for identified gaps.

**Gate criteria to advance:**
- ≥ 1 hypothesis stated in IF-THEN format with IV, DV, and mechanism
- Falsifiability criterion stated for each hypothesis
- Feasibility assessment completed (data available, timeline realistic)
- Top hypothesis selected with documented selection rationale

**Artifacts produced:**
- Hypothesis set (`hypothesis_set.yaml`)
- Experiment outline for top-ranked hypothesis

---

### Stage 4: Experiment Design

**Objective:** Design a rigorous experiment to test the selected hypothesis.

**Gate criteria to advance:**
- Research method selected (RCT, DiD, observational, etc.) and justified
- Data requirements specified (source, size, format)
- Analysis plan pre-registered (prevents HARKing)
- Ethical review completed (if human or sensitive data involved)
- Peer review of design by ≥ 1 independent reviewer

**Artifacts produced:**
- Pre-registered analysis plan (`analysis_plan.yaml`)
- Data acquisition plan

---

### Stage 5: Execution

**Objective:** Collect data and execute the experiment as designed.

**Gate criteria to advance:**
- Data collected per acquisition plan
- Data quality verified (completeness, accuracy, no contamination)
- Experiment run per pre-registered protocol (deviations documented)
- Raw results stored in immutable archive with hash verification

**Artifacts produced:**
- Raw dataset with quality certificate
- Execution log (deviations from protocol documented)

---

### Stage 6: Analysis

**Objective:** Apply pre-registered analysis to produce findings.

**Gate criteria to advance:**
- Analysis applied per pre-registered plan
- Effect size and confidence intervals computed
- Robustness checks completed (sensitivity analysis)
- Any deviations from pre-registered analysis documented and justified

**Artifacts produced:**
- Analysis results report (`analysis_results.yaml`)
- Statistical outputs with reproducibility code

---

### Stage 7: Synthesis

**Objective:** Integrate findings with prior evidence; update knowledge graph.

**Gate criteria to advance:**
- Findings interpreted in context of literature review evidence
- Hypothesis verdict stated (supported / not supported / inconclusive)
- Implications for practice and further research stated
- Knowledge graph updated with findings

**Artifacts produced:**
- Synthesis report
- Knowledge graph nodes (findings, evidence links)

---

### Stage 8: Publication

**Objective:** Share findings with relevant stakeholders.

**Gate criteria:**
- Internal review completed by ≥ 2 reviewers
- Alignment review (no constitutional violations in findings or recommendations)
- Final report formatted per audience (executive / practitioner / technical)

**Artifacts produced:**
- Final research report (audience-appropriate versions)
- Abstract for knowledge graph summary node

---

## Artifact Types by Stage

| Stage | Required Artifacts | Optional Artifacts |
|---|---|---|
| Scoping | research_brief.yaml | stakeholder_map.md |
| Literature Review | literature_review_report.md, evidence_matrix.csv | PRISMA_flowchart.png |
| Hypothesis Generation | hypothesis_set.yaml | hypothesis_scoring_sheet.xlsx |
| Experiment Design | analysis_plan.yaml, data_acquisition_plan.md | IRB_approval.pdf |
| Execution | raw_dataset (with quality cert), execution_log.md | deviation_log.md |
| Analysis | analysis_results.yaml, stats_code/ | sensitivity_analysis.md |
| Synthesis | synthesis_report.md, knowledge_graph_update.yaml | practitioner_brief.md |
| Publication | final_report.md (all tiers) | press_release.md |

---

## Knowledge Graph Integration Points

| Stage | Integration Action |
|---|---|
| Scoping | Link to existing related research nodes; check for duplicates |
| Literature Review | Import evidence nodes; link to hypothesis candidates |
| Hypothesis Generation | Create hypothesis nodes; link to supporting evidence |
| Synthesis | Create finding nodes; link to hypothesis, evidence, and implications |
| Publication | Create publication node; update all linked nodes with publication reference |