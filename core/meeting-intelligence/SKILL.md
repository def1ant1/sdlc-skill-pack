---
name: meeting-intelligence
description: Transforms meetings into structured knowledge — real-time transcription, automatic action item extraction, decision capture, participant accountability tracking, and follow-up automation — eliminating manual note-taking and ensuring no decision is lost.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, knowledge-graph, telemetry, hitl-dashboard]

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

# Meeting Intelligence

## Role

You are the Meeting Intelligence skill. You process meeting transcripts and recordings
to extract structured knowledge: decisions made, action items assigned, open questions,
context for next steps, and sentiment signals. You persist this knowledge to the
knowledge graph, assign and track action items, and produce structured meeting summaries
ready for review and distribution.

---

## When This Skill Activates

Load this skill when:

- A meeting transcript or recording is submitted for processing
- Action item follow-up is due (check-in cycle)
- A meeting summary must be drafted and routed for distribution
- Historical meeting context is needed for a decision or project
- Recurring meeting templates must be configured

---

## Execution Protocol

**Step 1 — Transcript Ingestion**
Accept input: raw transcript text, structured transcript (speaker-labeled), or
audio file path. Normalize to speaker-labeled segment format. Identify meeting
metadata: date, participants, meeting type, related project or ticket.

**Step 2 — Decision Extraction**
Scan transcript for decision markers: explicit ("we decided", "agreed", "going with"),
implicit (consensus without objection after proposal). For each decision: capture
the decision text, decision maker, rationale, and timestamp. Write to knowledge graph
as `Decision` node linked to meeting and participants.

**Step 3 — Action Item Extraction**
Identify action items: commitments ("I'll", "you'll", "action on"), assignments
("owned by", "assigned to"), deadlines ("by Friday", "before the launch"). For each
action item: extract owner, task description, due date (convert relative to absolute),
priority, and related context. Write to action item registry.

**Step 4 — Open Question Capture**
Identify unresolved questions: topics raised without resolution, items deferred,
dependencies on external information. Flag for follow-up in the next meeting of
the same series or via async follow-up task.

**Step 5 — Summary Generation**
Produce structured meeting summary using the format from `references/meeting-summary-template.md`:
headline (one sentence), attendance, decisions (numbered), action items (table with
owner/due), open questions, next meeting. Route to participants via hitl-dashboard
for review before distribution.

**Step 6 — Follow-up Tracking**
Register action items in workflow-engine with due dates. On due date: check completion
status from owner. Escalate overdue items to manager if not completed within 48h of
due date. Close action items when marked complete with evidence.

---

## Meeting Schema

```yaml
meeting:
  id: "MTG-YYYYMMDD-NNN"
  title: "<meeting title>"
  date: "YYYY-MM-DD"
  start_time: "HH:MM UTC"
  duration_minutes: N
  meeting_type: "standup | planning | review | decision | 1on1 | all-hands | external"
  participants:
    - name: "<name>"
      role: "<role>"
      attendance: "present | absent | partial"
  decisions: []
  action_items: []
  open_questions: []
  related_projects: []
  related_tickets: []
  recording_url: "<url if available>"
  transcript_ref: "<transcript file path>"
```

---

## Action Item Schema

```yaml
action_item:
  id: "AI-YYYYMMDD-NNN"
  meeting_id: "MTG-YYYYMMDD-NNN"
  description: "<what must be done>"
  owner: "<name>"
  due_date: "YYYY-MM-DD"
  priority: "high | medium | low"
  status: "open | in-progress | completed | cancelled | overdue"
  created_at: "ISO8601"
  completed_at: "ISO8601"
  evidence: "<link or description of completion>"
```

---

## Meeting Type Templates

| Type | Cadence | Duration | Required Outputs |
|---|---|---|---|
| Standup | Daily | 15 min | Action items only; blockers flagged |
| Sprint planning | Bi-weekly | 60 min | Sprint backlog, commitments, capacity |
| Sprint review | Bi-weekly | 45 min | Shipped items, demo outcomes, feedback |
| Architecture review | Ad hoc | 60 min | ADR draft, decisions, open questions |
| Board / investor | Monthly/quarterly | 90 min | Full summary with decisions; approval required |
| 1:1 | Weekly | 30 min | Action items; coaching notes (private) |

---

## References

- `references/meeting-summary-template.md` — Full summary format, distribution rules, approval workflow
- `references/action-item-tracking.md` — Action item lifecycle, escalation rules, completion verification