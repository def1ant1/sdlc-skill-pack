---
name: policy-simulation
description: Simulates the organizational and operational impact of proposed policy changes before enforcement, quantifying compliance burden, behavioral change requirements, and unintended consequences.
metadata:
  version: "1.0.0"
  category: governance
  owner: governance
  maturity: alpha
  dependencies: [simulation-engine, governance, business-simulation, telemetry]

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

Pre-enforcement policy impact simulator for the governance runtime. Models how proposed
policy changes will affect agent behaviors, workflow processes, compliance burden, and
operational costs before the policy is activated — enabling evidence-based policy design
and surfacing unintended consequences that would be costly to fix post-enforcement.

## Activation Triggers

- Governance submits a proposed policy change for pre-enforcement impact analysis
- Alignment-engine proposes a new constitutional rule requiring impact assessment
- Operator requests what-if analysis before tightening an existing policy
- Regulatory requirement triggers mandatory impact assessment before policy implementation

## Execution Protocol

1. **Parse proposed policy**: Extract the policy rule, affected agents and workflows,
   enforcement mechanism, and exception criteria from the policy definition.

2. **Identify affected population**: Enumerate all agents, workflows, and processes whose
   behavior would be constrained or modified by the proposed policy.

3. **Model behavioral changes**: For each affected entity, simulate how the policy constraint
   changes its behavior — blocked actions, required approvals, additional latency,
   alternative routing.

4. **Quantify compliance burden**: Estimate the operational cost of compliance — added
   latency per workflow, additional approval steps, workflow modifications required,
   and estimated agent development effort for behavior changes.

5. **Detect unintended consequences**: Cross-check behavioral changes against other active
   policies for conflicts; identify workflows that would be blocked entirely; flag
   edge cases where the policy produces perverse incentives.

6. **Produce impact assessment**: Summarize affected population, compliance burden, risk
   reduction achieved, unintended consequences, and recommended policy refinements.

## Output Format

Policy impact assessment with: `policy_id`, `affected_entities` (count and list),
`compliance_burden_estimate` (latency impact, effort, cost), `risk_reduction_score`,
`unintended_consequences` (list with severity), `policy_conflicts` (list), and
`refinement_recommendations`.

## References

- `references/policy-simulation-model.md` — behavioral change modeling rules, compliance burden estimation, conflict detection logic