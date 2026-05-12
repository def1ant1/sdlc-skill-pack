---
name: marketplace-scenario-analysis
description: Ecommerce extension skill for marketplace-scenario-analysis with organizational-memory-aware analysis and safety controls.
metadata:
  version: 0.1.0
  category: ecommerce-intelligence
  owner: Apotheon
  maturity: alpha
---

# marketplace scenario analysis

## Purpose
Supports ecommerce decision workflows for **marketplace-scenario-analysis**.

## Core requirements
- Integrate outputs with organizational memory primitives (`memory.fact`, `memory.timeseries`, `memory.signal`, `memory.snapshot` as relevant).
- Include source provenance and confidence metadata for generated findings.
- Surface uncertainty and require human review for high-risk conclusions.

## Safety
- This skill is analysis-first and must not execute irreversible external actions.
- If used with simulator workflows, execution mode remains **dry-run only**.
