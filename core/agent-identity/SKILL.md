---
name: agent-identity
description: Maintains persistent agent expertise profiles, episodic, procedural, and semantic memory across sessions, and computes reputation scores based on task quality, reliability, and alignment history.
metadata:
  version: "1.0.0"
  category: cognitive
  owner: platform
  maturity: alpha
  dependencies: [knowledge-graph, telemetry, agent-kernel]
---

## Role

Persistent identity and memory manager for the Autonomous OS agent population. Maintains
durable agent profiles that survive session boundaries, accumulating episodic task history,
procedural skill patterns, and semantic domain knowledge; computes reputation scores used
by cognitive-runtime for agent selection and trust calibration.

## Activation Triggers

- Agent session completes and memory consolidation is required
- Cognitive-runtime queries agent capability and reputation for task assignment
- Agent identity profile requires update following reputation score recalculation
- Operator requests an agent capability audit or memory inspection

## Execution Protocol

1. **Consolidate episodic memory**: At session end, summarize completed tasks into episodic
   memory records — task type, outcome, quality score, and lessons learned; prune episodes
   beyond the retention window.

2. **Update procedural memory**: Extract reusable procedure patterns from successful task
   executions; store as retrievable procedural records indexed by task type and domain.

3. **Maintain semantic memory**: Update domain knowledge assertions in the semantic memory
   store; resolve conflicts between new and existing knowledge using recency weighting.

4. **Compute reputation score**: Calculate the weighted reputation score —
   quality_score × 0.4 + reliability_score × 0.3 + alignment_score × 0.2 + peer_review × 0.1;
   update the agent identity record.

5. **Serve capability queries**: Respond to cognitive-runtime queries for agents matching
   a capability requirement with matching agents ranked by reputation score.

6. **Enforce memory quotas**: Apply per-agent memory quotas by pruning oldest low-value
   episodes when capacity limits are reached.

## Output Format

Agent identity record with: `agent_id`, `agent_type`, `reputation_score`, `episodic_memory_count`,
`procedural_patterns_count`, `semantic_assertions_count`, `task_history_summary`
(30-day), and `capability_tags`.

## References

- `references/agent-identity-schema.md` — identity record YAML, 3 memory types, reputation scoring, persistence