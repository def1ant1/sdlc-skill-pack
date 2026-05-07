# Agent Collaboration Patterns

## Pattern 1 — Sequential Chain

**Description**: Agents execute in sequence; each agent's output is the next agent's input.

**Use when**: Task has clear dependencies; output of step N is required for step N+1.

```
Orchestrator → Agent A → Agent B → Agent C → Orchestrator
```

**Example**: Requirements → Architecture → Code Review chain.

**Rules**:
- Each agent receives only the output it needs from the prior agent
- Orchestrator validates each handoff before proceeding
- On agent failure: halt chain; do not proceed with partial output

---

## Pattern 2 — Parallel Fan-Out / Fan-In

**Description**: Orchestrator sends the same task to multiple agents simultaneously;
collects and merges results.

**Use when**: Same task benefits from multiple independent perspectives; tasks are
independent and can run concurrently.

```
              ┌─ Agent A ─┐
Orchestrator ─┼─ Agent B ─┼─ Aggregator → Orchestrator
              └─ Agent C ─┘
```

**Example**: Security agent + Quality agent reviewing the same PR in parallel.

**Rules**:
- All agents must receive identical input snapshots
- Aggregator merges results with conflict resolution rules
- Minimum quorum required (e.g., 2 of 3 agents must agree) for decision-making
- Timeout: if one agent doesn't respond in N minutes, proceed with available results

---

## Pattern 3 — Critic / Reviewer Loop

**Description**: A primary agent produces output; a critic agent reviews and provides
feedback; the primary agent revises; loop continues until quality threshold met or
max iterations reached.

**Use when**: Quality matters more than speed; self-correction improves output.

```
Primary Agent → [output] → Critic Agent → [feedback] → Primary Agent
                                                              │
                                              (until quality ≥ threshold or N iterations)
```

**Example**: draft-generation-agent produces a report; governance-agent critiques it
for policy violations; draft-generation-agent revises.

**Rules**:
- Maximum loop iterations: 3 (prevents infinite loops)
- Quality threshold must be defined before starting the loop
- If threshold not met after max iterations: escalate to human review
- Each iteration is logged with critique and revision

---

## Pattern 4 — Hierarchical Delegation

**Description**: Orchestrator delegates tasks to specialist sub-agents; each specialist
may further delegate to lower-level agents.

**Use when**: Complex task requires deep specialization; a generalist orchestrator
cannot handle all aspects.

```
Orchestrator
  ├── Architect Agent
  │     ├── Security Agent
  │     └── Performance Agent
  └── Engineering Agent
        └── QA Agent
```

**Example**: Autonomous OS orchestrates SDLC orchestration, which in turn coordinates
backend, frontend, and QA agents.

**Rules**:
- Delegation depth ≤ 4 levels (prevents runaway hierarchies)
- Each delegation level must be logged
- Sub-agents cannot escalate their own authority beyond what was delegated
- Approval gates apply at the level that would normally hold them (not bypassed by delegation)

---

## Pattern 5 — Consensus Decision

**Description**: Multiple agents evaluate a decision independently; orchestrator
aggregates votes and applies quorum rule.

**Use when**: High-stakes decision benefits from independent perspectives; avoiding
single-agent bias.

```
Orchestrator distributes decision to N agents
  Each agent returns: [decision, confidence, rationale]
  Orchestrator applies voting rule:
    - Simple majority (> 50%): for routine decisions
    - Supermajority (> 66%): for high-stakes decisions
    - Unanimous (100%): for safety-critical decisions
```

**Example**: 3 agents independently evaluate whether a LoRA model is safe to promote.

**Rules**:
- Each agent receives the same information; no agent sees another's vote before submitting
- Minority votes are logged and surfaced (for human review on high-stakes decisions)
- Disagreement > 1 agent: always escalate to human review

---

## Inter-Agent Message Format

```json
{
  "message_id": "uuid",
  "correlation_id": "parent-workflow-id",
  "from_agent": "<sender agent id>",
  "to_agent": "<recipient agent id>",
  "type": "task | result | critique | vote | escalation",
  "payload": {},
  "sent_at": "ISO8601",
  "timeout_seconds": 300
}
```

---

## Collaboration Constraints

These rules apply to all patterns:

1. No agent may communicate directly with external systems without going through connector-hub
2. All inter-agent messages are logged to telemetry
3. An agent cannot instruct another agent to perform an action above its own authority level
4. Loops must have explicit termination conditions (max iterations or quality threshold)
5. Human escalation path must be defined for every pattern