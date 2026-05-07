# Context Budgeting

Used by `core/memory-token-management/SKILL.md` to allocate token budgets across
workflow complexity tiers, define per-area limits, and specify threshold actions.

---

## Budget Tiers

| Complexity | Total Budget | Planning | Source | Reasoning | Output | Buffer |
|---|---|---|---|---|---|---|
| `single-phase` | 8K–20K tokens | 10% | 30% | 25% | 30% | 5% |
| `multi-phase` | 20K–60K tokens | 8% | 25% | 30% | 32% | 5% |
| `full-sdlc` | 60K–200K tokens | 5% | 20% | 35% | 35% | 5% |

Select the tier based on `project.complexity` in the memory packet.

---

## Area Definitions

| Area | What It Covers | Management Rule |
|---|---|---|
| **Planning** | Workflow plans, skill chain, gate definitions, routing decisions | Keep concise; reference files not inline content |
| **Source** | Code, architecture docs, requirements, external content read into context | Load lazily — only the sections needed for the current step |
| **Reasoning** | Chain-of-thought, analysis, decision deliberation | Do not preserve verbatim — compress to accepted decision only |
| **Output** | Skill deliverables, phase outputs, reports, artifacts | Preserve by reference (file path) not inline |
| **Buffer** | Overflow headroom; never intentionally consumed | If buffer is consumed, trigger compression immediately |

---

## Budget Enforcement Rules

1. **Lazy loading**: Never load a full document into context when only a section is needed.
   Load by section heading, function, or named block.

2. **Reference over inline**: For files over 200 lines, load the path and relevant line
   range rather than the full content.

3. **Summarize before compress**: When approaching thresholds, summarize phase outputs
   before triggering full compression.

4. **One skill at a time**: Never load two domain skills' full context simultaneously.
   Flush the previous skill's working context before loading the next.

5. **Artifact metadata only**: Load artifact metadata (type, path, status) rather than
   artifact content unless the content is directly needed for the current step.

---

## Threshold Actions

| Budget Used | Action |
|---|---|
| < 50% | Normal operation |
| 50% | Log budget warning in `token_stats`; continue |
| 75% | Trigger compression (`compression-rules.md` Step 4) |
| 90% | Halt new context loads; surface alert; operator notification |
| 95% | Emergency compression; drop all non-priority-1-6 items |
| 100% | Halt workflow; escalate to human; cannot safely continue |

---

## Per-Phase Budget Guidance

| Phase | Typical Source Load | Notes |
|---|---|---|
| requirements | Medium (docs, interviews) | Load only current requirements; not full backlog |
| architecture | High (ADRs, diagrams) | Load ADR metadata; diagrams by reference |
| ai-engineering | Medium (model specs, eval results) | Load model card summaries, not full weights |
| backend | High (code, schemas) | Load file-by-file; never entire codebase |
| frontend | Medium (components, designs) | Load component index; files on demand |
| security | Medium (policies, findings) | Load finding summaries; not full scan logs |
| qa | Medium (test plans, results) | Load test summary; not full test output |
| release | Low (release notes, runbook) | Mostly output phase; minimal input loading |
| observability | Medium (metrics, dashboards) | Load dashboard summaries; not raw metrics |