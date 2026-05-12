# shipping-carrier-selection

Decision-support skill for shipping carrier selection in ecommerce logistics.

## Output contract
- Emit recommendations with explicit `cost`, `delivery_time`, and `sla_risk` dimensions.
- Include assumptions, constraints, and confidence level for each recommendation.
- Link decisions to ontology entities: `FulfillmentOrder`, `InventoryLot`, and order/listing references.

## Governance requirements
- Treat bookings, label purchases, freight commitments, carrier account charges, and returns authorizations as external side effects requiring explicit approval before execution.
- If approval is absent, remain analysis-only and emit `approval_requested` with blocked actions.

## Integration hints
- Read inventory availability and allocation from `InventoryLot` and `FulfillmentOrder` relationships.
- Preserve source lineage timestamps for carrier-rate, ETA, and SLA evidence.
