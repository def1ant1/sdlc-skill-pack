# Adaptive Intake Policy

## Purpose

The adaptive intake orchestrator classifies incoming conversation intent and routes to the next safe action while minimizing unnecessary back-and-forth.

## Routing behavior

1. **Classify intent** into a structured intent object (`intent`, `risk_level`, `default_action`, `required_fields`).
2. **Determine missing required fields** from known `facts`.
3. **Apply best assumptions** only when `use_best_assumptions=true`.
   - Assumptions are loaded from `assumptions_catalog`.
   - Used assumptions are persisted in `assumptions_used`.
   - Missing fields without assumptions are persisted in `open_questions`.
4. **Choose next safe action**:
   - `ask_clarifying_question` when required info is still missing and clarifying is allowed.
   - `defer_execution` when missing info remains but clarification budget is exhausted.
   - otherwise the intent's `default_action`.

## Clarifying question budget

- Normal flows: at most **one** clarifying question (`clarifying_questions_asked < 1`).
- High-risk flows: multiple clarifications are allowed until safety-critical fields are captured.

High-risk can be triggered by:
- intent classification with `risk_level=high`, or
- policy override `policy.high_risk=true`.

## Policy boundaries

- The orchestrator is **decision support only** and must not directly perform irreversible external actions.
- For high-risk domains (medical/legal/financial advice), default is conservative routing (`request_handoff`) until required facts are present.
- If assumptions mode is disabled, missing required information must stay explicit in `open_questions` and should not be silently inferred.

## Contract surfaces

- `schemas/conversation-state.schema.json`: session/user/facts/policy input shape.
- `schemas/conversation-intent.schema.json`: normalized intent classification output shape.
- `scripts/orchestration/route_conversation_intent.py`: CLI entry point for deterministic routing in automation.
