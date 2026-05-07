---
name: schema-evolution
description: Detects breaking and non-breaking schema changes across the data fabric, coordinates backward-compatible migrations, and enforces contract compliance before changes reach production consumers.
metadata:
  version: "1.0.0"
  category: data
  owner: data
  maturity: alpha
  dependencies: [data-fabric, data-contract-management, event-bus, telemetry]
---

## Role

Schema change lifecycle manager for the data fabric. Intercepts proposed schema changes,
classifies their impact as breaking or non-breaking, coordinates migration execution with
all registered data consumers, and enforces a compatibility gate before changes reach
production pipelines.

## Activation Triggers

- Producer registers a schema change via the data fabric API
- Data-contract-management detects a contract violation caused by an upstream schema change
- Operator submits a planned schema migration for review and coordination
- Automated schema drift detection flags a production schema divergence

## Execution Protocol

1. **Parse proposed change**: Extract field additions, removals, type changes, constraint
   modifications, and name changes from the schema diff.

2. **Classify impact**: Categorize each change — non-breaking (additive: new optional fields,
   relaxed constraints); breaking (removals, type narrowing, required field additions, renames).

3. **Identify affected consumers**: Query the data contract registry to enumerate all downstream
   consumers with active contracts referencing the changed schema.

4. **Coordinate migration**: For breaking changes, notify all affected consumers with the
   proposed change, migration timeline, and backward-compatibility window; collect acknowledgments.

5. **Enforce compatibility gate**: Block promotion of breaking schema changes until all
   registered consumers have updated their contracts or explicitly opted into the new schema.

6. **Execute and verify**: Apply the schema change; run contract compliance validation for all
   consumers; emit `schema.evolved` event with migration summary.

## Output Format

Schema evolution record with: `schema_id`, `change_classification` (breaking/non-breaking),
`affected_consumers` (count and list), `migration_plan` (timeline and steps),
`compatibility_gate_status` (OPEN/BLOCKED), and post-migration compliance results.

## References

- `references/schema-compatibility-rules.md` — breaking change taxonomy, compatibility window policy, migration coordination protocol