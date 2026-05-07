---
name: data-contract-management
description: Authors, registers, and monitors data contracts between producers and consumers, detects contract violations in real time, and enforces remediation workflows when SLAs are breached.
metadata:
  version: "1.0.0"
  category: data
  owner: data
  maturity: alpha
  dependencies: [data-fabric, schema-evolution, event-bus, telemetry]
---

## Role

Data contract lifecycle manager for the data fabric. Maintains a registry of formal agreements
between data producers and consumers specifying schema, quality, freshness, and SLA
commitments; monitors compliance in real time; and orchestrates remediation when violations
are detected.

## Activation Triggers

- New data pipeline requires a formal producer-consumer contract
- Schema-evolution detects a breaking change affecting registered contracts
- Data quality monitor reports a freshness or quality threshold breach
- Operator requests a contract audit or compliance report

## Execution Protocol

1. **Author contract**: Capture producer identifier, consumer identifier, schema version,
   quality thresholds (completeness, accuracy, uniqueness), freshness SLA, and escalation
   contacts in the standard contract YAML format.

2. **Register contract**: Assign a contract-id; store in the contract registry; link to the
   schema version in the schema registry; notify both producer and consumer.

3. **Monitor compliance**: Subscribe to data quality metrics from the data fabric telemetry
   stream; evaluate each metric against the contract thresholds at the configured check interval.

4. **Detect violations**: Classify violations by type — schema violation, quality degradation,
   freshness breach, or total unavailability; calculate violation severity.

5. **Orchestrate remediation**: Notify the responsible producer with violation details and
   SLA breach timestamp; escalate to operator if not resolved within the grace period;
   suspend consumer workflows if data quality falls below the hard floor threshold.

6. **Report compliance**: Generate periodic compliance reports per contract with historical
   SLA adherence rates and trend analysis.

## Output Format

Contract compliance record with: `contract_id`, `producer_id`, `consumer_id`, `schema_version`,
`compliance_status` (COMPLIANT/VIOLATION/SUSPENDED), `violation_type` (if applicable),
`sla_adherence_rate` (30-day), and `remediation_status`.

## References

- `references/contract-schema.md` — contract YAML format, quality threshold types, SLA violation grace periods