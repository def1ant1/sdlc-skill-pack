# Progressive Disclosure Standard (L1/L2/L3)

## Objective
Standardize context loading so orchestration keeps token usage bounded while preserving correctness.

## Levels
- **L1 (Minimal)**: request summary, task constraints, and immediate contract references only.
- **L2 (Focused)**: L1 + directly dependent skill contracts and required operational references.
- **L3 (Extended)**: L2 + adjacent references used for disambiguation, audits, and fallback planning.

## Budget Caps
Default token caps (override only with explicit justification):
- L1: <= 2,000
- L2: <= 8,000
- L3: <= 16,000

## Default Level Conformance
- Default level is **L2** unless a skill manifest explicitly sets `context_loading.default_level`.
- Runtime must fail validation when estimated context token load exceeds the default level cap.
- Escalation to a higher level requires recording a rationale and expected value gain.

## Required Contracts
Every skill manifest must expose:
- `use_when`
- `do_not_use_when`
- `context_loading.levels` with `L1/L2/L3` budgets
- `context_loading.default_level`

## Telemetry Hooks
Emit these events when loading context:
- `context_budget_evaluated`
- `context_budget_violation`
- `context_level_escalated`

