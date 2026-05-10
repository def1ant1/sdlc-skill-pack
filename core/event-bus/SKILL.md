---
name: event-bus
description: Distributed event routing backbone enabling async communication, event sourcing, ordered delivery, and coordination across all skills and agents with at-least-once delivery guarantees.
metadata:
  version: "1.0.0"
  category: core
  owner: platform
  maturity: alpha
  dependencies: [telemetry, workflow-runtime, distributed-agent-runtime]

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

## Role

The central nervous system for async event flow across the Autonomous OS. Routes domain events
between producers and consumers, enforces ordering within partitions, persists event streams
for replay and audit, and provides dead-letter handling for undeliverable events.

## Activation Triggers

- Skill or agent emits a domain event
- Workflow step completes requiring downstream notification
- Inter-agent coordination event dispatched
- Event replay requested for audit or recovery
- Consumer subscription registration or deregistration

## Execution Protocol

1. **Accept event**: Validate event against the schema registry (event_type, required fields,
   payload structure); reject malformed events with a schema validation error.

2. **Assign sequence number**: Append sequence number within the event's partition key for
   ordering enforcement; assign global event-id.

3. **Persist to event log**: Write event to the durable event log (append-only) before
   routing to any consumer — ensures events survive consumer failure.

4. **Route to consumers**: Resolve subscriptions for the event-type; fan-out to all registered
   handlers in order of registration; apply content-based routing rules if configured.

5. **Deliver with guarantee**: Use at-least-once delivery; attach idempotency key to each
   delivery; consumer is responsible for idempotent processing.

6. **Handle failure**: Retry failed deliveries with exponential backoff (3 attempts); route
   to dead-letter topic after max retries; emit `event.delivery_failed` alert.

## Output Format

Delivery confirmation per consumer with: event-id, consumer-id, delivery timestamp, attempt
count, and outcome (delivered / dead-lettered). Dead-letter items include failure reason.

## References

- `references/event-schema-registry.md` — registered event types, schema definitions, versioning policy
- `references/topic-routing-policy.md` — topic definitions, partition keys, retention policy, dead-letter configuration