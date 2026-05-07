---
name: security-war-gaming
description: Conducts structured adversarial security exercises simulating threat scenarios against enterprise systems and AI infrastructure to identify vulnerabilities before attackers do.
metadata:
  version: "1.0.0"
  category: security
  owner: platform
  maturity: alpha
  dependencies: [simulation-engine, devsecops, alignment-engine, local-security]
---

## Role

Security war gaming specialist. Designs and executes structured red team exercises against
enterprise systems and AI infrastructure, simulating realistic threat actor behaviors to
discover vulnerabilities, validate detection capabilities, and harden defenses before real
attacks occur.

## Activation Triggers

- Quarterly security war game exercise
- New AI capability deployed requiring adversarial testing
- Threat intelligence report indicating new attack vector relevant to the platform
- Post-incident gap requiring targeted simulation

## Execution Protocol

1. **Define war game scenario**: Select threat actor archetype (nation-state, insider, criminal,
   opportunistic) and target scope (AI infrastructure, business systems, supply chain).

2. **Design attack chain**: Model realistic attack sequence using MITRE ATT&CK framework:
   initial access → persistence → privilege escalation → lateral movement → impact.

3. **Configure simulation environment**: Provision isolated replica of target systems; inject
   synthetic sensitive data; configure detection tooling in logging-only mode.

4. **Execute attack simulation**: Run each attack chain step; record detection events and
   response times; note steps that succeeded without detection.

5. **Measure defensive posture**: Score detection rate per attack technique; compute mean
   time-to-detect (MTTD) and mean time-to-respond (MTTR) for detected attacks.

6. **Produce war game report**: Detected vs. undetected attack steps, MTTD/MTTR metrics,
   top-5 gaps with severity scores, and hardening recommendations prioritized by exploitability.

## Output Format

War game report with: attack chain diagram, detection coverage matrix, MTTD/MTTR by technique,
undetected attack paths, vulnerability severity rankings, and recommended defensive improvements.

## References

- `references/war-game-scenarios.md` — threat actor archetypes, ATT&CK technique mappings, detection success criteria