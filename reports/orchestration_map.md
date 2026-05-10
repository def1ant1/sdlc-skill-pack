# Orchestration Map

## Artifact Outputs
- `reports/skill_dependency_graph.json`
- `reports/skill_dependency_graph.mmd`
- `reports/orchestration_map.md`

## Summary
- Total nodes: 273 (core: 70, skills: 203)
- Total dependencies: 625
- Unresolved dependencies: 0

## Orchestration Guidance
1. Resolve unresolved dependencies before execution planning.
2. Use topological ordering where graph is acyclic.
3. Route to collision analysis when two skills share overlapping triggers.
