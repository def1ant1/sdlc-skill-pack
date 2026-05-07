---
name: inbox-automation
description: Processes, classifies, drafts responses, routes, and tracks follow-up across email, Slack, and Teams.
metadata:
  version: "0.1.0"
  category: connectivity
  owner: platform
  maturity: draft
  dependencies: ['enterprise-integration-hub', 'connector-hub']
---

## Role

Autonomous processing layer for enterprise communication inboxes (email, Slack, Microsoft Teams).
Classifies incoming messages by intent and urgency, drafts contextual responses using platform
knowledge, routes messages to the appropriate agent or human owner, and tracks follow-up threads
to ensure nothing falls through the cracks.

## Activation Triggers

- New message arrives in a monitored inbox or channel (webhook or polling)
- A follow-up deadline has elapsed and no response has been sent
- A persistent agent delegates a communication task to inbox-automation
- Operator configures a new inbox or channel for monitoring
- A message thread is detected as requiring escalation (urgency signals present)

## Execution Protocol

1. **Ingest message**: Receive message payload via `enterprise-integration-hub` webhook.
   Extract: sender, recipients, channel/thread, timestamp, subject, body, attachments.

2. **Classify**: Apply multi-label classification:
   - **Intent**: `request` | `information` | `escalation` | `approval_needed` | `fyi` | `spam`
   - **Urgency**: `P1` (needs response < 1h) | `P2` (< 4h) | `P3` (< 24h) | `P4` (> 24h OK)
   - **Domain**: `finance` | `engineering` | `legal` | `hr` | `sales` | `operations` | `executive`
   - **Routing target**: specific agent or human role responsible for this domain × intent

3. **Draft response** (if appropriate):
   - For routine requests (intent=`request`, urgency=P3/P4): draft a response using platform
     knowledge, clearly marking it as AI-drafted and requiring human review
   - For P1/P2 urgent items or approval_needed: do not draft; route immediately with context packet

4. **Route**: Dispatch the classified message and optional draft to the routing target:
   - If target is a persistent agent: send via `persistent-agent-runtime` inter-agent message bus
   - If target is a human: create a task in `itsm-integration` with message context attached

5. **Follow-up tracking**: Register message in the follow-up tracker with:
   - Expected response SLA based on urgency class
   - Responsible party
   - Alert schedule: remind at 50% and 90% of SLA elapsed

## Output Format

```yaml
inbox_result:
  message_id: "MSG-EMAIL-2026-xxxxx"
  channel: email | slack | teams
  classification:
    intent: request
    urgency: P2
    domain: engineering
  routing_target: "engineering-lead@corp.com"
  draft_generated: true
  draft_requires_review: true
  follow_up_deadline: "2026-05-07T14:00:00Z"
  quality_gates_passed: true
```

## Quality Gates

- Classification confidence ≥ 0.75 before autonomous routing (else escalate to human review)
- Drafts must pass the AI disclosure check (must include AI-drafted marker)
- No PII in routing metadata beyond what is required for task assignment

## References

- `references/` — Message classification taxonomy, routing policy, follow-up SLA table, draft template library
