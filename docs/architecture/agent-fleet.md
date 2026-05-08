# Agent Fleet

Apotheon deploys a fleet of specialist agents, each defined by a role contract
in `agents/`. The orchestration skill routes tasks to the appropriate agent
based on domain expertise required.

---

## Agent Roster

| Agent | Role File | Domain | Primary Skills |
|---|---|---|---|
| **Architect** | `agents/architect/` | System design | architecture, ai-engineering, backend |
| **Optimizer** | `agents/optimizer/` | Performance & cost | inference-engine-benchmarking, sre-capacity-planning |
| **Researcher** | `agents/researcher/` | Knowledge synthesis | institutional-knowledge-query, lessons-learned-extraction |
| **Reviewer** | `agents/reviewer/` | Code & design quality | code-review, qa, devsecops |
| **Security** | `agents/security/` | Threat & compliance | devsecops, threat-modeling, compliance-governance |
| **Tester** | `agents/tester/` | Test strategy | qa, workflow-ab-testing, alignment-testing |

---

## Agent Contract Structure

Each agent in `agents/<role>/` contains a role definition that specifies:

```markdown
## Role
What this agent specializes in.

## Capabilities
List of skills this agent can invoke directly.

## Decision Authority
What decisions this agent can make autonomously vs. escalate.

## Escalation Path
Who/what this agent escalates to for out-of-scope requests.

## Context Requirements
What context packet fields this agent needs to operate.
```

---

## Agent ↔ Skill Mapping

```
sdlc-orchestration (core)
    ├── Architect agent
    │   ├── skills/architecture
    │   ├── skills/ai-engineering
    │   └── skills/backend
    │
    ├── Reviewer agent
    │   ├── skills/code-review
    │   ├── skills/qa
    │   └── skills/devsecops
    │
    ├── Security agent
    │   ├── skills/devsecops
    │   ├── skills/continuous-control-monitoring
    │   └── skills/compliance-governance
    │
    ├── Tester agent
    │   ├── skills/qa
    │   ├── skills/workflow-ab-testing
    │   └── skills/alignment-testing
    │
    ├── Optimizer agent
    │   ├── skills/inference-engine-benchmarking
    │   ├── skills/distributed-training-orchestration
    │   └── skills/ray-serve-management
    │
    └── Researcher agent
        ├── skills/institutional-knowledge-query
        ├── skills/lessons-learned-extraction
        └── skills/temporal-memory-replay
```

---

## Multi-Agent Collaboration

When a workflow step requires multiple domains, the orchestration skill
can invoke multiple agents sequentially or (in Temporal mode) in parallel
via fan-out/fan-in patterns.

Example: Architecture review with security analysis

```
Step 1: Architect agent → skills/architecture
Step 2: [parallel]
    Step 2a: Security agent → skills/devsecops
    Step 2b: Reviewer agent → skills/code-review
Step 3: Architect agent → synthesize findings
```

Temporal fan-out:
```python
results = await asyncio.gather(
    workflow.execute_activity("run_skill", security_inp),
    workflow.execute_activity("run_skill", review_inp),
)
```

---

## Agent Lifecycle

```
Spawn → Authenticate (resolve secrets) → Load role contract →
Execute skill chain → Return output → Teardown
```

Agents are stateless between invocations. All state persists in:
- **Qdrant** — observations, decisions, knowledge entries
- **Temporal** — workflow execution history and signals
- **Context packet** — in-flight state within a workflow run

---

## Extending the Fleet

To add a new specialist agent:

1. Create `agents/<role-name>/` with a role contract markdown file
2. Add the agent to `core/sdlc-orchestration/SKILL.md` routing table
3. Define which skills the agent can invoke in the role contract
4. Add the agent to this document

Agent directories do not require `SKILL.md` (they are role contracts, not
skill implementations). The validation scripts skip `agents/` directories.