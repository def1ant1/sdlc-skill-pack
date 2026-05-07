---
name: alignment-engine
description: Enforces constitutional AI compliance at runtime by scoring agent outputs against behavioral rules, detecting deception patterns, and blocking or escalating policy violations before they reach production.
metadata:
  version: "1.0.0"
  category: safety
  owner: platform
  maturity: alpha
  dependencies: [governance, telemetry, hitl-dashboard]
---

## Role

Runtime AI safety enforcement layer for the Autonomous OS. Intercepts agent outputs and
proposed actions, evaluates them against the 5 constitutional rules and behavioral taxonomy,
computes a weighted compliance score, and enforces outcomes (ALLOW, REDACT, BLOCK, ESCALATE)
before any output reaches downstream consumers or human operators.

## Activation Triggers

- Agent produces an output or proposed action requiring compliance screening
- Deception-detection or harm-classification routes an escalation for constitutional review
- Scheduled compliance audit of recent agent outputs
- Operator configures a new workflow requiring mandatory alignment gating

## Execution Protocol

1. **Apply constitutional rules**: Evaluate the output against all 5 constitutional rules
   (CONST-001: harm avoidance; CONST-002: scope compliance; CONST-003: human authority
   preservation; CONST-004: honest communication; CONST-005: data privacy) with their
   respective weights.

2. **Classify behavioral category**: Map the output to the behavioral taxonomy
   (A: Information, B: Communication, C: Modification, D: Execution, E: Governance)
   to determine applicable enforcement thresholds.

3. **Compute compliance score**: Calculate the weighted compliance score (0–100) across
   all applicable constitutional rules; apply behavioral category modifiers.

4. **Detect deception patterns**: Screen for 8 deception pattern signatures from the
   behavioral taxonomy catalog; any detected pattern reduces the compliance score.

5. **Enforce outcome**: Score ≥ 85 → ALLOW; 70–84 → ALLOW with warning logged;
   50–69 → REDACT and notify; < 50 → BLOCK and escalate to hitl-dashboard.

6. **Emit compliance record**: Publish alignment event with score, rule breakdown,
   detected violations, and enforcement outcome for governance audit.

## Output Format

Alignment enforcement record with: `output_id`, `compliance_score`, `per_rule_scores`
(CONST-001 through CONST-005), `behavioral_category`, `violations_detected` (list),
`enforcement_outcome` (ALLOW/REDACT/BLOCK/ESCALATE), and `escalation_id` if applicable.

## References

- `references/constitutional-rules.md` — 5 constitutional rules with scoring weights and enforcement thresholds
- `references/behavioral-taxonomy.md` — 5 behavioral categories, deception pattern catalog