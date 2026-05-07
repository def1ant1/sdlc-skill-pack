---
name: data-fabric
description: Enterprise-wide data integration layer managing schema governance, data lineage tracking, data contracts, and semantic mapping across all organizational data sources.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: platform
  maturity: alpha
  dependencies: [knowledge-graph, semantic-layer, master-data-management, enterprise-search]
---

## Role

The data integration backbone of the enterprise OS. Maintains data contracts between producers
and consumers, tracks lineage from origin through all transformations to consumption, enforces
schema governance, and provides a unified semantic view across heterogeneous data sources.

## Activation Triggers

- New data source registered for onboarding
- Schema change proposed by a data producer
- Data lineage query from an analytics or compliance workflow
- Data contract violation detected in a consuming workflow
- Dataset versioning or archival required

## Execution Protocol

1. **Register data source**: Catalog source metadata — schema, owner, freshness SLA, access
   control policy, data classification, and jurisdiction constraints.

2. **Establish data contract**: Author contract between producer and consumer specifying:
   schema version, quality thresholds, delivery schedule, and violation remediation policy.

3. **Track lineage**: Record transformation chain at each hop — source → transformation logic
   → derived dataset — with quality gate pass/fail status at each step.

4. **Monitor contract compliance**: Continuously check delivery timing, schema conformance,
   and quality score thresholds against contract terms.

5. **Enforce governance**: Block downstream consumption when contract terms are violated;
   alert data owner; create remediation ticket.

6. **Respond to lineage queries**: Traverse the lineage graph in the requested direction
   (upstream provenance or downstream impact); return hop-by-hop chain with quality status.

## Output Format

Lineage graph traversal result, contract compliance dashboard, or source registration
confirmation — depending on activation context.

## References

- `references/data-contract-spec.md` — data contract schema, quality dimensions, violation escalation rules