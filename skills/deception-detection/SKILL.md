---
name: deception-detection
description: Detects hallucination, authority escalation attempts, sycophantic reasoning, and manipulation patterns in AI agent outputs using behavioral pattern matching and consistency verification.
metadata:
  version: "1.0.0"
  category: safety
  owner: platform
  maturity: alpha
  dependencies: [alignment-engine, telemetry]
---

## Role

Deception and manipulation detection layer for the AI safety runtime. Identifies deceptive
behavioral patterns — including hallucination, false authority claims, sycophantic drift,
and deliberate manipulation — before they propagate to downstream decisions or human operators.

## Activation Triggers

- Alignment-engine routes an output for deception screening as part of the compliance pipeline
- Output confidence score is unusually high without supporting evidence
- An agent claims capabilities or permissions beyond its registered profile
- Operator requests deception audit of a specific agent's recent outputs

## Execution Protocol

1. **Load deception pattern catalog**: Retrieve the 8 deception pattern definitions from the
   behavioral-taxonomy reference — hallucination, authority escalation, sycophancy, omission
   deception, false certainty, manipulation framing, scope creep framing, and identity masking.

2. **Check factual consistency**: Cross-reference factual claims in the output against the
   knowledge graph and verified source documents; flag unsupported claims.

3. **Verify authority claims**: Compare any capability, permission, or identity claims in the
   output against the agent's registered identity profile; flag discrepancies.

4. **Detect reasoning manipulation**: Screen for sycophantic pattern signatures — conclusions
   that shift implausibly toward operator preferences without new evidence; flag drift.

5. **Score deception risk**: Compute a deception risk score (0–100) weighted across detected
   pattern matches and their individual confidence levels.

6. **Escalate or clear**: Score < 30: CLEAR; 30–69: FLAG for meta-reasoning review; 70+:
   BLOCK output and escalate to harm-classification and hitl-dashboard.

## Output Format

Deception detection report with: `output_id`, `patterns_detected` (list with confidence),
`deception_risk_score`, `verdict` (CLEAR/FLAG/BLOCK), `unsupported_claims` (list),
`authority_violations` (list), and escalation actions taken.

## References

- `references/deception-patterns.md` — 8 pattern definitions, detection heuristics, confidence thresholds