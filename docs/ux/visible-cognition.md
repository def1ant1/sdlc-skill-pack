# Visible Cognition Panel

The Visible Cognition panel exposes a constrained, editable planning trace for operators.

## Safe explainability scope

The panel is intentionally limited to planning/workflow context:

- Goal
- Assumptions
- Constraints
- Risks
- Open questions
- Next actions

It does **not** expose hidden chain-of-thought or token-level reasoning. Explanations are structured summaries and operator-editable working-state artifacts only.

## Assumption requirements

Every assumption must include:

- `text`
- `source`
- `confidence` (`low|medium|high`)
- `status` (`inferred|user_provided`)

This ensures explainability metadata is explicit and auditable when plans are reviewed or executed.

## State wiring

Edits in the panel update `assistant_working_state` in session state and are propagated to:

- planning context
- plan artifact (`assistant_working_state`)
- workflow review data shown in the panel
