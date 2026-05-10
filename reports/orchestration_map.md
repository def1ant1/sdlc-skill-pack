<!-- traceability: commit_sha=8f5d1d079a1114123bb53dd06f2cc3f29ccd13b3 generated_at_utc=2026-05-10T16:35:03-04:00 generator=scripts/generate_release_reports.py -->
# Orchestration Map

## Artifact Outputs
- `reports/skill_dependency_graph.json`
- `reports/skill_dependency_graph.mmd`
- `reports/orchestration_map.md`

## Summary
- Total nodes: 284 (core: 70, skills: 214)
- Total dependencies: 625
- Unresolved dependencies: 0

## Orchestration Guidance
1. Resolve unresolved dependencies before execution planning.
2. Use topological ordering where graph is acyclic.
3. Route to collision analysis when two skills share overlapping triggers.
