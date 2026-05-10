---
name: zero-trust-policy-authoring
description: Authors zero-trust policy definitions, scope declarations, and exception management workflows for the zero-trust-runtime.
metadata:
  version: "0.1.0"
  category: security
  owner: platform
  maturity: draft
  dependencies: ['zero-trust-runtime', 'governance']

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

Policy authoring and lifecycle management for `zero-trust-runtime`. Provides structured
workflows for defining, reviewing, approving, publishing, and retiring OPA policy bundles
that govern all agent-to-agent and skill-to-skill authorization in the Enterprise OS.
Ensures policies are peer-reviewed, tested, and versioned before enforcement.

## Activation Triggers

- A new skill or agent is registered and requires an access policy
- An existing policy requires a scope change (new capability added or removed)
- A policy exception is requested (temporary broadened access for a maintenance window)
- Quarterly policy review cycle is due
- `security-architect-agent` requests a policy audit or remediation

## Execution Protocol

1. **Policy authoring**: Accept a policy definition in the platform's policy DSL:
   - `subject`: the agent or skill being granted access
   - `target`: the resource (skill, data store, external system)
   - `actions`: list of permitted actions
   - `conditions`: contextual constraints (time window, confidence level, approval state)
   - `rationale`: business justification (required for audit)

2. **Static validation**: Validate the policy:
   - Syntax check against the OPA Rego schema
   - Least-privilege check: flag any policy granting broader scope than the subject's declared capabilities
   - Conflict detection: check for contradictions with existing policies

3. **Peer review gate**: Route the policy for review:
   - P0 skills and agents: require security-architect-agent + human security lead sign-off
   - Other skills: require security-architect-agent automated review only

4. **Test**: Run the policy against the policy test suite (synthetic allow/deny scenarios).
   All test cases must pass before publishing.

5. **Publish**: Submit the approved policy to `zero-trust-runtime` for live reload.
   Version the policy bundle. Record the author, approvers, and effective date.

6. **Exception management**: For time-limited exceptions:
   - Require explicit expiry timestamp (max 72 hours)
   - Auto-revert to baseline policy on expiry
   - Alert `security-architect-agent` when exception is active

## Output Format

```yaml
policy_authoring:
  policy_id: "policy/cfo-agent/erp-integration/read-financials"
  version: "1.2.0"
  status: draft | in_review | approved | active | retired
  published_at: null
  expires_at: null
  test_results: passed | failed
  peer_review:
    security_agent: approved
    human_reviewer: null
```

## Quality Gates

- Zero policies published without passing the test suite
- Exception policies must have an expiry — no permanent exceptions

## References

- `references/` — Policy DSL specification, test suite format, review workflow
