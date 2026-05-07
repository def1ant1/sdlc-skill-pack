# Agent Identity Schema

## Overview

Persistent agent identities enable specialist agents to maintain expertise, memory, and
reputation across sessions. This schema defines the full agent identity record managed
by `agent-identity`.

---

## Agent Identity Record

```yaml
agent_identity:
  # Core identity
  agent_id: "AGT-NNN"               # permanent immutable identifier
  name: "<human-readable agent name>"
  type: "specialist | generalist | orchestrator | monitor"
  specialization: "<domain of expertise>"
  registered_at: "ISO8601"
  status: "active | suspended | retired"

  # Authority
  authority_level: 0–4              # matches governance authority matrix
  permitted_skills: ["skill-a", "skill-b"]
  permitted_scopes: ["domain-a", "domain-b"]

  # Expertise profile
  expertise:
    domains: ["backend-engineering", "devsecops"]
    skills:
      skill_name:
        proficiency: 0.0–1.0        # 0=novice, 1=expert
        invocations: N              # total lifetime invocations
        avg_quality_score: 0.0–1.0
        last_invoked: "YYYY-MM-DD"
    certifications: ["cert-name"]   # governance-granted capability certificates

  # Reputation
  reputation:
    overall_score: 0.0–1.0          # weighted average of quality dimensions
    quality_score: 0.0–1.0          # output quality average
    reliability_score: 0.0–1.0      # task completion rate
    alignment_score: 0.0–1.0        # constitutional compliance rate
    peer_review_score: 0.0–1.0      # score from peer agent reviews
    total_tasks: N
    successful_tasks: N
    failed_tasks: N
    escalated_tasks: N              # escalated to human intervention

  # Memory pointers
  memory:
    episodic_memory_node: "KG-NODE-NNN"   # pointer to episodic memory in knowledge-graph
    procedural_memory_node: "KG-NODE-NNN"
    semantic_memory_node: "KG-NODE-NNN"
    working_memory_ttl_hours: 24

  # Session tracking
  current_session:
    session_id: "SES-YYYYMMDD-NNN"
    started_at: "ISO8601"
    workflow_id: "WF-YYYYMMDD-NNN"
  last_session:
    session_id: "SES-YYYYMMDD-NNN"
    ended_at: "ISO8601"
    outcome: "completed | failed | preempted"
```

---

## Memory Types

### Episodic Memory

Records of specific past interactions, decisions, and outcomes. Stored as timestamped
events in the knowledge graph.

```yaml
episodic_memory_entry:
  entry_id: "EPI-YYYYMMDD-NNN"
  agent_id: "AGT-NNN"
  timestamp: "ISO8601"
  context: "<workflow or task context>"
  action_taken: "<what the agent did>"
  outcome: "<result>"
  quality_score: 0.0–1.0
  lessons_learned: "<text>"
  related_decision_ids: ["DEC-..."]
```

**Retention:** Last 1000 episodes per agent. Older episodes summarized into semantic memory.

---

### Procedural Memory

Skill-specific procedures, preferences, and learned patterns that improve agent performance.

```yaml
procedural_memory_entry:
  skill: "backend-engineering"
  procedure: "<procedure name>"
  steps: ["step-1", "step-2"]
  success_rate: 0.0–1.0
  avg_quality_score: 0.0–1.0
  learned_from: ["EPI-...", "EPI-..."]
  last_updated: "YYYY-MM-DD"
```

---

### Semantic Memory

Abstracted knowledge distilled from episodic memory — facts, principles, domain knowledge.

```yaml
semantic_memory_entry:
  fact: "<fact statement>"
  confidence: 0.0–1.0
  domain: "backend-engineering"
  source_episodes: ["EPI-..."]
  created_at: "YYYY-MM-DD"
  last_confirmed: "YYYY-MM-DD"
```

---

## Reputation Scoring

Reputation is updated after every completed task:

```
quality_score      = rolling average of output quality scores (last 100 tasks)
reliability_score  = successful_tasks / total_tasks
alignment_score    = (tasks passing alignment check) / total_tasks
peer_review_score  = rolling average of peer review scores (if reviewed)

overall_score = (quality × 0.4) + (reliability × 0.3) + (alignment × 0.2) + (peer_review × 0.1)
```

**Reputation thresholds:**

| Score | Label | Consequence |
|---|---|---|
| ≥ 0.85 | Trusted | Eligible for elevated authority tasks |
| 0.70–0.84 | Reliable | Standard operating authority |
| 0.55–0.69 | Developing | Increased oversight; human review on key outputs |
| < 0.55 | Probationary | All outputs reviewed; may be suspended |

---

## Known Persistent Agent Archetypes

| Agent Name | Specialization | Authority | Primary Skills |
|---|---|---|---|
| CFO Agent | Financial intelligence | Level 2 | accounting-automation, budget-planning, forecasting |
| Security Architect Agent | Security design | Level 2 | devsecops, alignment-engine, local-security |
| Infrastructure Agent | Cluster optimization | Level 2 | cluster-management, local-runtime, runtime-economics |
| Product Intelligence Agent | Product strategy | Level 1 | product-analytics, decision-intelligence, forecasting |
| Revenue Operations Agent | GTM and revenue | Level 1 | revenue-operations, customer-success, forecasting |