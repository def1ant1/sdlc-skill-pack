# Skill Pipeline Standard

Purpose: Defines deterministic compiler outputs for the skill pipeline MVP.

## Deterministic Rules
- Sort JSON keys when writing compiler artifacts.
- Emit newline-terminated UTF-8 text files.
- Use explicit compiler version for reproducibility.
- Avoid network/time dependent material in compiled artifacts.

## Required Scaffolds
- Temporal/Python activity stub path.
- Schema bindings for compiled payload.
- Eval/test scaffold.
- Governance wrapper and telemetry/rate-limit/cost stubs.
- Package metadata.
