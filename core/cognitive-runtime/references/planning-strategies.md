# Planning Strategies

## Overview

The cognitive-runtime selects a planning strategy based on objective type, available information,
risk tolerance, and time constraints. Strategy selection happens at the beginning of every planning
cycle and may change during execution if conditions shift.

---

## Strategy Catalog

### Sequential Strategy

**When to use:** Dependencies between sub-goals are strict; parallelism is not safe; resources are constrained.

**Characteristics:**
- One sub-goal executes at a time
- Each sub-goal's output feeds the next
- Lower resource demand; higher time-to-completion

**Risk profile:** Low risk of conflict; higher schedule risk if any step delays.

**Example application:** Regulated compliance workflows, schema migrations, security audits.

---

### Parallel Strategy

**When to use:** Sub-goals are independent; resources permit concurrent execution; time pressure is high.

**Characteristics:**
- Independent sub-goals execute simultaneously
- Results aggregated at synchronization points
- Higher resource demand; lower time-to-completion

**Risk profile:** Resource contention risk; conflict risk at merge points.

**Parallelism detection rule:** Sub-goal B is parallelizable with A if B's inputs do not depend on A's outputs AND they do not share write access to the same resources.

**Example application:** Multi-service feature development, parallel benchmark evaluation runs.

---

### Speculative Strategy

**When to use:** High uncertainty about which path will succeed; failure recovery cost is low; exploration has value.

**Characteristics:**
- Multiple alternative approaches initiated in parallel
- First successful completion wins; others are cancelled
- Higher resource cost; best-case latency

**Risk profile:** Resource waste if early winner found; acceptable if uncertainty is high.

**Decision trigger:** Confidence < 0.4 on preferred approach AND at least 2 viable alternatives exist.

**Example application:** Model architecture search, A/B testing plan execution, technology selection.

---

### Conservative Strategy

**When to use:** High stakes; irreversible actions; production impact; novel situation with low confidence.

**Characteristics:**
- Extensive validation at each step before proceeding
- Human approval gates on all non-trivial decisions
- Smaller blast radius by design; explicit rollback plan at every step

**Risk profile:** Lowest execution risk; highest time cost.

**Trigger conditions:**
- Action safety level ≥ 2
- Production system affected
- Estimated impact > $10K or > 100 users

**Example application:** Production database migrations, financial transactions, security configuration changes.

---

### Adaptive Strategy

**When to use:** Environment is dynamic; conditions change during execution; plan staleness is likely.

**Characteristics:**
- Plan monitored continuously against actual conditions
- Replanning triggered when deviation threshold exceeded (>20% variance from expected)
- Rolling horizon: only nearest steps planned in detail; later steps planned at coarser granularity

**Replanning triggers:**
- Step outcome deviates from expected by >20%
- External condition change detected (market shift, incident, policy change)
- Dependency completion time exceeds deadline by >10%

**Example application:** Long-horizon strategic plans, market-responsive GTM execution, incident response.

---

## Strategy Selection Rules

```
IF objective has strict sequential dependencies THEN sequential
ELSE IF objective has ≥ 3 independent sub-goals AND resources available THEN parallel
ELSE IF planner confidence < 0.4 AND failure cost is low THEN speculative
ELSE IF action safety level ≥ 2 OR irreversible actions present THEN conservative
ELSE IF planning horizon > 4 weeks THEN adaptive
ELSE sequential  # default for well-understood objectives
```

---

## Replanning Triggers

| Trigger | Threshold | Action |
|---|---|---|
| Step delay | >20% over estimated duration | Recompute critical path |
| Outcome deviation | >20% from expected value | Replan affected branch |
| Blocker detected | Any hard blocker | Pause branch; find alternative path |
| External condition change | Any significant context shift | Full replan from current state |
| Confidence collapse | Planner confidence drops below 0.3 | Escalate to human review |

---

## Plan Version History

Every replan creates a new version of the goal tree (v1, v2, …). All versions are retained in the
knowledge graph with timestamps and replan reasons for audit and retrospective analysis.