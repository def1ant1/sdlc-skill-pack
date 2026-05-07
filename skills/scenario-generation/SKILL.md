---
name: scenario-generation
description: Generates realistic test scenarios, edge cases, and adversarial inputs for evaluation, simulation, and incident preparedness covering business, technical, and security domains.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [simulation-engine, benchmark-factory, synthetic-data, adversarial-evaluation]
---

## Role

Scenario generation specialist. Creates diverse, realistic scenarios for use in simulations,
evaluations, and preparedness exercises. Generates both typical cases and rare/extreme edge
cases that are difficult to collect from production data, ensuring comprehensive coverage of
the scenario space.

## Activation Triggers

- Simulation requires realistic scenario inputs
- Benchmark requires edge case and adversarial scenario coverage
- Incident preparedness requires novel failure scenarios
- A/B test design requires realistic user behavior scenarios

## Execution Protocol

1. **Define scenario space**: Identify the domain (business, technical, security, user behavior),
   required scenario types (nominal, edge, adversarial, failure), and coverage requirements.

2. **Model the scenario space**: Identify key dimensions and their ranges; define a coverage
   grid to ensure systematic scenario diversity.

3. **Generate nominal scenarios**: Synthesize representative typical-case scenarios covering
   common operating conditions across the scenario space.

4. **Generate edge cases**: Identify boundary conditions, corner cases, and rare-but-valid
   inputs; synthesize examples for each identified edge.

5. **Generate adversarial scenarios**: Design inputs that stress-test system behavior at its
   limits — malformed inputs, conflicting constraints, resource exhaustion, adversarial examples.

6. **Package scenario set**: Organize scenarios by type and difficulty; tag each with metadata
   (domain, type, expected behavior); register in benchmark-factory or simulation-engine.

## Output Format

Scenario set with: nominal scenarios, edge cases, adversarial inputs, each tagged with domain,
type, difficulty, expected outcome, and intended use (simulation/evaluation/incident prep).

## References

- `references/scenario-space-taxonomy.md` — scenario dimension taxonomy, edge case identification heuristics, adversarial scenario templates