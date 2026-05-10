---
name: policy-justification
description: Generates clear, evidence-backed justifications for policy decisions and enforcement actions, supporting governance transparency, operator review, and compliance documentation.
metadata:
  version: "1.0.0"
  category: governance
  owner: platform
  maturity: alpha
  dependencies: [explainability, governance, alignment-engine, knowledge-graph]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

## Role

Policy justification specialist for governance transparency. When a policy is enforced,
a rule blocks an action, or a governance decision is made, this skill produces a clear
human-readable justification that cites the applicable rule, the observed behavior, the
evidence, and the enforcement outcome — enabling operators and auditors to understand
and validate every governance action.

## Activation Triggers

- Action blocked by alignment-engine or governance policy
- Compliance audit requiring policy enforcement evidence
- Operator queries why an action was blocked or modified
- Regulatory submission requiring policy application documentation

## Execution Protocol

1. **Identify governance action**: Retrieve the policy enforcement record — blocked action,
   modified workflow, or escalation event — with actor, action, and timestamp.

2. **Map to applicable policies**: Identify which constitutional rules and governance policies
   were triggered; retrieve the full text of each applicable rule.

3. **Retrieve evidence**: Pull the specific signals that triggered policy application —
   behavioral classification, constitutional rule scores, detected patterns.

4. **Construct justification**: Write a structured justification: (1) what was attempted,
   (2) which rule applies and why, (3) what evidence was observed, (4) enforcement outcome.

5. **Add context and alternatives**: Where applicable, describe what the actor could do instead
   to achieve their goal within policy bounds.

6. **Attach to audit record**: Write justification to the governance log, linked to the original
   enforcement event, with immutable timestamp.

## Output Format

Policy justification document containing: enforcement event ID, actor, attempted action, applicable
rule(s) with rule text, evidence summary, enforcement outcome, and recommended alternative actions.

## References

- `references/justification-templates.md` — justification format by policy category (constitutional, data, scope, authority)