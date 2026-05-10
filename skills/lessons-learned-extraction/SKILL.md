---
name: lessons-learned-extraction
description: Synthesizes post-execution lessons from workflow and agent outcomes and integrates them into the organizational knowledge graph.
metadata:
  version: "0.1.0"
  category: knowledge
  owner: platform
  maturity: draft
  dependencies: ['world-model', 'sdlc-memory-token-management']

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

Post-execution knowledge synthesis. After significant workflow completions, incident
resolutions, or agent milestones, extracts generalizable lessons from the execution record
and integrates them into the organizational knowledge graph as institutional memory.
Turns one-time experiences into reusable organizational intelligence.

## Activation Triggers

- A workflow of `lesson_worthy` classification completes (success or failure)
- An incident is resolved and post-incident review is complete
- A program milestone is reached with a performance variance worth capturing
- `organizational-learning-loop` initiates a batch lessons synthesis pass
- An operator explicitly marks an execution for lessons extraction

## Execution Protocol

1. **Execution record assembly**: Collect the full execution record:
   - Workflow DAG with step outcomes and timing
   - Decisions made at each HITL gate with rationale
   - Anomalies detected and how they were handled
   - Final outcome vs. expected outcome (variance)
   - Resource consumption vs. plan

2. **Pattern identification**: Compare this execution against similar past executions from
   the knowledge graph. Identify:
   - What went better than expected? (positive lessons)
   - What went worse than expected? (negative lessons, failure patterns)
   - What decisions were made that differed from precedent? (novel approaches)

3. **Lesson synthesis**: For each identified pattern, synthesize a lesson statement:
   - `lesson_type`: `best_practice` | `failure_pattern` | `novel_approach` | `process_improvement`
   - `context`: the conditions under which this lesson applies
   - `lesson`: the generalizable insight
   - `confidence`: based on how many executions support this pattern (1 = low, 5+ = high)

4. **Knowledge graph integration**: Submit lessons to `world-model` and `sdlc-memory-token-management`
   as semantic memories. Link to originating execution records for traceability.

5. **Surfacing**: For high-confidence lessons (confidence ≥ 3), notify the skill/domain
   owners via `notification-orchestration` so teams can act on the insight.

## Output Format

```yaml
lessons_extracted:
  execution_ref: "workflow-run-2026-xxxxx"
  lessons:
    - lesson_type: failure_pattern
      context: "Large batch fine-tuning on H100 nodes with NVLink disabled"
      lesson: "Training throughput drops 40% without NVLink — always verify NVLink topology before large jobs"
      confidence: 2
      knowledge_graph_ref: "semantic/lesson/LES-2026-xxxxx"
  lessons_count: 0
  integrated_to_knowledge_graph: true
```

## Quality Gates

- Lessons must be verifiable against the execution record (no unsupported assertions)
- Lessons referencing PII or confidential data must be anonymized before storage

## References

- `references/` — Lesson taxonomy, synthesis prompt template, confidence scoring rubric
