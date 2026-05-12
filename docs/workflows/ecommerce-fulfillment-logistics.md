# Ecommerce Fulfillment + Logistics Skill Pack

This guide documents MB-ECOM-P0-005 fulfillment/logistics behavior and governance.

## Included skills

- `ecommerce-fulfillment`
- `shipping-carrier-selection`
- `package-dimension-optimization`
- `freight-and-pallet-analysis`
- `warehouse-slotting-analysis`
- `pick-pack-optimization`
- `returns-routing-analysis`
- `shipping-sla-risk-analysis`

## Recommendation output requirements

Every shipping recommendation must include:

1. `cost` — total estimated spend and components.
2. `delivery_time` — expected/promise window and confidence.
3. `sla_risk` — SLA breach risk score plus key drivers.

## Ecommerce ontology integration

Decisioning must reference:

- `FulfillmentOrder` as the execution object.
- `InventoryLot` for source location and quantity constraints.
- `MarketplaceListing` or order reference for customer promise context.

## Approval and external side-effect policy

The following require explicit approval before execution:

- shipping label purchases
- carrier or freight bookings
- carrier-account billable charges
- return merchandise routing authorizations that create external commitments

If approval is missing, the skill must remain in analysis-only mode and return `approval_requested`.
