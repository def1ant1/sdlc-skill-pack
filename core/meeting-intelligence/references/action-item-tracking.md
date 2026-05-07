# Action Item Tracking

## Lifecycle States

```
open → in-progress → completed
open → cancelled
open → overdue (automatic on due date + 1)
in-progress → overdue (automatic if due date passes)
overdue → completed (if owner completes and marks done)
overdue → escalated (automatic at +48h overdue)
```

---

## Assignment Rules

When extracting action items from a meeting transcript:

1. **Always assign an owner** — if the transcript doesn't name an owner, flag as "Unassigned" for meeting organizer to resolve before distribution
2. **Convert relative dates** — "by Friday" → `YYYY-MM-DD` (absolute); "next sprint" → first day of next sprint; "ASAP" → next business day
3. **Default priority**: Medium; upgrade to High if:
   - Linked to a P0 or P1 incident
   - Mentioned as blocking another person or team
   - Due within 24 hours
4. **Link to ticket if mentioned** — if a ticket number is mentioned, record in `related_ticket`

---

## Escalation Protocol

| Event | Action | Notification |
|---|---|---|
| Action item reaches due date + 0 | Status → overdue | Reminder to owner |
| Overdue + 24h | Escalation attempt 1 | DM to owner |
| Overdue + 48h | Escalate to manager | DM to manager; include context |
| Overdue + 5 days | Critical escalation | Flag in weekly meeting report |

Escalation pauses if:
- Owner marks item as "in-progress" with a revised due date
- Owner explicitly accepts revised due date (no auto-approval)

---

## Completion Verification

When an owner marks an action item complete, the system requests:

1. **Brief description of what was done** (required)
2. **Link to evidence** (PR, ticket, document, email — optional but encouraged)

If no evidence provided: mark as complete but flag as unverified. Reviewer can challenge.

---

## Meeting Action Item Summary (Weekly Report)

```
ACTION ITEM STATUS SUMMARY — Week of YYYY-MM-DD
================================================
Total open items:     N
  Due this week:      N
  Overdue:            N  ← escalated to meeting organizers
  Completed (7 days): N

OVERDUE ITEMS
  [AI-ID] [Task] → Owner: [name] → Was due: [date] → Overdue: N days
  ...

DUE THIS WEEK
  [AI-ID] [Task] → Owner: [name] → Due: [date]
  ...
```

This summary is included in the weekly executive review prepared by executive-reporting.

---

## Integration with Knowledge Graph

All action items are written to the knowledge graph as `ActionItem` nodes with edges to:
- The `Meeting` node (created_in)
- The `Person` node (owned_by)
- Relevant `Project` or `Decision` nodes (related_to)

This enables queries like:
- "Show all open action items for [person]"
- "What action items came out of the architecture review meeting?"
- "Which decisions have outstanding action items?"