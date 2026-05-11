<!-- traceability: commit_sha=a96ac1f9902f77cc1d4b42447a30e21380b30a5a generated_at_utc=2026-05-10T21:58:01-04:00 generator=scripts/generate_release_reports.py -->
# Orchestration Map

## Artifact Outputs
- `reports/skill_dependency_graph.json`
- `reports/skill_dependency_graph.mmd`
- `reports/orchestration_map.md`

## Summary
- Total nodes: 284 (core: 0, skills: 284)
- Total dependencies: 625
- Unresolved dependencies: 0

## Orchestration Guidance
1. Resolve unresolved dependencies before execution planning.
2. Use topological ordering where graph is acyclic.
3. Route to collision analysis when two skills share overlapping triggers.
