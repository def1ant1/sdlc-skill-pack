---
name: persistent-agent-runtime
description: Manages always-on named enterprise agents with standing mandates, proactive trigger evaluation, and inter-agent messaging.
metadata:
  version: "0.1.0"
  category: cognitive
  owner: platform
  maturity: draft
  dependencies: ['agent-kernel', 'cognitive-runtime', 'workflow-runtime', 'event-bus']
---

## Role

Lifecycle manager for always-on named enterprise agents (CFO Agent, Security Architect Agent,
Compliance Agent, etc.). Maintains agent heartbeats, evaluates standing mandate triggers on
each monitoring cycle, routes inter-agent messages, manages agent-specific memory namespaces,
and escalates items that exceed autonomous action authority to the `hitl-dashboard`.

## Activation Triggers

- Platform startup: boot all registered persistent agents from their stored mandate configs
- `governance` registers a new named agent definition
- An agent's monitoring cycle timer fires (per-agent configurable interval)
- An `event-bus` event matches a standing mandate trigger pattern
- Operator issues a directive to a specific named agent via `operator-console`
- An agent requests inter-agent coordination with another named agent

## Execution Protocol

1. **Agent registry**: Maintain a registry of all named agents with their mandate configs,
   last-heartbeat timestamp, current belief state snapshot, and action authority scope.

2. **Heartbeat loop**: On each agent's monitoring interval:
   a. Fetch fresh telemetry and world-model state relevant to the agent's domain
   b. Evaluate all standing mandate trigger conditions against current state
   c. For triggered conditions within authority scope: execute autonomous action
   d. For triggered conditions above authority scope: create escalation in `hitl-dashboard`
   e. Update agent's belief state snapshot; record heartbeat

3. **Inter-agent messaging**: Route messages between named agents via a typed message bus.
   Enforce that agents can only message agents listed in their `coordination_peers` config.
   Log all inter-agent messages for audit.

4. **Directive handling**: When an operator issues a directive via `operator-console`,
   validate it against the target agent's directive acceptance policy, then inject it
   into the agent's next evaluation cycle as a high-priority mandate item.

5. **Memory isolation**: Each agent has an isolated memory namespace in `sdlc-memory-token-management`.
   Agents cannot read each other's memory without explicit cross-agent data-sharing authorization.

## Output Format

```yaml
agent_runtime:
  operation: heartbeat | directive | message | escalation
  agent_id: "cfo-agent"
  status: healthy | degraded | suspended | escalated
  actions_taken: []
  escalations_created: []
  next_heartbeat_at: "2026-05-07T12:00:00Z"
  audit_ref: "AGENT-RT-2026-xxxxx"
```

## References

- `references/` — Mandate config schema, trigger evaluation engine spec, authority scope taxonomy
