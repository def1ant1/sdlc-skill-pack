# Compression Rules

Used by `core/memory-token-management/SKILL.md` to define what to preserve, what to drop,
and in what order when compressing a memory packet to recover token budget.

---

## Trigger Thresholds

| Threshold | Action |
|---|---|
| 50% consumed | Emit budget warning; no compression yet |
| 75% consumed | Trigger compression (automatic) |
| 90% consumed | Halt new context loads; surface alert to operator |
| 100% consumed | Emergency compression; drop all non-essential context |

---

## Preservation Priority Order

When compressing, retain items in this order until the target budget is reached.
Never drop items ranked 1–6 regardless of budget pressure.

| Priority | Item | Justification |
|---|---|---|
| 1 | `decisions.accepted` | Binding — dropping causes re-litigation |
| 2 | `constraints` (all categories) | Define the solution space |
| 3 | `quality_gate_status` (all records) | Audit trail — required for escalation |
| 4 | `risks` (high + critical severity) | Active risks must stay visible |
| 5 | `open_questions` (blocking current phase) | Blocked questions halt progress |
| 6 | `next_action` | Current execution pointer |
| 7 | `artifacts` metadata (not content) | Downstream skills need location references |
| 8 | `phase_status` (all phases) | Orchestration needs full phase map |
| 9 | `decisions.pending` | Unresolved decisions (may be demoted if not blocking) |
| 10 | `risks` (low + medium severity) | Less urgent; summarize before dropping |
| 11 | `open_questions` (non-blocking) | Can be re-derived from context |
| 12 | `decisions.rejected` | Useful but recoverable from decisions log |

---

## Drop Order

When budget is still exceeded after retaining all priority items, drop in this order:

1. **Raw conversation turns** — Replace with compressed summary
2. **Superseded artifact drafts** — Keep only the current `status: final` version metadata
3. **Resolved risks** (`status: mitigated` or `status: closed`) — Drop after gate passes
4. **Closed open questions** (`resolved: true`) — Drop after gate passes
5. **Intermediate reasoning traces** — Keep only the conclusion (accepted decision)
6. **Repeated constraint mentions** — Deduplicate; keep one canonical entry per constraint

---

## Summarization Rules

When summarizing retained content to reduce token count:

| Content Type | Summarization Rule |
|---|---|
| Decision rationale | Compress to one sentence; keep the decision itself verbatim |
| Risk description | Compress to one sentence per risk; keep severity and status |
| Artifact content | Replace with metadata only (type, location, status, consumed_by) |
| Phase output prose | Compress to bullet-point summary; keep measurable outcomes |
| Gate evidence | Keep gate name, status, and one-line failure reason; drop full evidence |

---

## Compression Record

After every compression run, append to the packet:

```yaml
compression_record:
  - generation: 1
    triggered_at: "2026-05-06T00:00:00Z"
    trigger_reason: "75% budget threshold"
    tokens_before: 45000
    tokens_after: 28000
    items_dropped: ["raw_turns_1-47", "draft_v1_spec", "risk-003 (closed)"]
    items_summarized: ["decisions.accepted[0-5]", "artifacts[0-3]"]
```

---

## Post-Compression Validation

After compression, verify:

- All `decisions.accepted` entries are still present
- All `constraints` entries are still present
- All `quality_gate_status` records with `status: FAIL` are still present
- `current_phase` and `next_action` are unchanged
- `token_stats.consumed` is below 75% of `total_budget`
- `token_stats.compression_triggered = true`
- `compression_generation` has incremented by 1

If any check fails, abort compression and surface an error.