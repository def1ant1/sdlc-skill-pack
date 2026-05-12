# MASTER BACKLOG — Ecommerce Arbitrage, Marketplace, and Sourcing Extension

**Status:** Active extension backlog  
**Purpose:** Extend the Apotheon enterprise operating system toward ecommerce arbitrage, marketplace operations, sourcing intelligence, catalog normalization, logistics orchestration, and multi-channel commerce automation.

This document supplements:

- `MASTER_BACKLOG.md`
- `APOTHEON_DOMAIN_SKILL_ENHANCEMENT_BACKLOG.md`
- `APOTHEON_DOCKER_DEPLOYMENT_BACKLOG.md`

---

# Strategic Goal

Transform Apotheon into a governed AI-assisted commerce operating system capable of:

```text
product sourcing
marketplace arbitrage
pricing intelligence
inventory optimization
multi-channel listing operations
supplier intelligence
freight/logistics optimization
market demand forecasting
catalog normalization
customer fulfillment workflows
returns/refunds analysis
profitability optimization
```

while enforcing:

```text
HITL approvals
marketplace policy compliance
anti-fraud protections
financial controls
tax/legal boundaries
rate-limit governance
scraping governance
```

---

# P0 — Ecommerce Arbitrage Runtime Foundation

## MB-ECOM-P0-001 — Marketplace ontology and canonical commerce entities

**Status:** Completed (2026-05-11)


Create:

```text
schemas/entities/Marketplace.json
schemas/entities/MarketplaceListing.json
schemas/entities/Supplier.json
schemas/entities/ProductCatalogItem.json
schemas/entities/InventoryLot.json
schemas/entities/FulfillmentOrder.json
schemas/entities/ShipmentTracking.json
schemas/entities/PricingSnapshot.json
schemas/entities/MarketplaceFeeProfile.json
schemas/entities/ProductConditionReport.json
schemas/entities/ProductAcquisitionOpportunity.json
references/ecommerce-ontology.md
```

Acceptance criteria:

- Supports cross-marketplace normalization.
- Supports used/refurbished/collector inventory.
- Tracks condition grading and acquisition confidence.
- Supports marketplace fee modeling.
- Implemented canonical schemas in `schemas/entities/*-schema.json` for all listed commerce entities.
- Added ontology reference with relationships, key normalization strategy, and payload examples in `references/ecommerce-ontology.md`.

---

## MB-ECOM-P0-002 — Marketplace ingestion and scraping governance layer

**Status:** Completed (2026-05-11)

Create:

```text
core/marketplace-ingestion/
core/scraping-governor/
schemas/marketplace-source.schema.json
references/marketplace-data-policy.md
scripts/marketplaces/validate_source_policy.py
```

Supported source categories:

```text
Facebook Marketplace
eBay
Craigslist
Bring a Trailer
GovDeals
auction platforms
salvage auctions
dealer inventory feeds
wholesale liquidation feeds
Amazon
Walmart Marketplace
Etsy
Shopify stores
regional classifieds
```

Requirements:

- robots.txt awareness where applicable
- terms-of-service policy tracking
- rate-limit enforcement
- proxy governance
- anti-ban throttling
- source lineage tracking
- duplicate listing detection
- structured extraction schema

Acceptance criteria:

- Sources declare legal/policy metadata.
- Ingestion runs in dry-run mode.
- Listings include source timestamp and retrieval lineage.
- Marketplace policy violations fail closed.

---

## MB-ECOM-P0-003 — Multi-marketplace pricing intelligence engine

**Status:** Completed (2026-05-11)

Create:

```text
core/pricing-intelligence/
skills/marketplace-price-normalization/
skills/marketplace-fee-analysis/
skills/marketplace-profitability-analysis/
skills/dynamic-margin-analysis/
skills/competitor-pricing-intelligence/
reports/marketplace_pricing_report.md
```

Capabilities:

```text
cross-marketplace price normalization
fee normalization
shipping normalization
tax normalization
expected margin analysis
price trend analysis
sell-through estimation
market saturation scoring
listing competitiveness scoring
```

Acceptance criteria:

- Outputs net profitability after fees/shipping/taxes.
- Marketplace-specific fee profiles supported.
- Confidence score attached to pricing recommendations.

---

## MB-ECOM-P0-004 — Product sourcing and acquisition intelligence

**Status:** Completed (2026-05-11)

Create:

```text
skills/product-sourcing-intelligence/
skills/supplier-discovery/
skills/local-liquidation-analysis/
skills/auction-opportunity-analysis/
skills/wholesale-price-comparison/
skills/product-condition-estimation/
skills/product-authenticity-risk-analysis/
skills/acquisition-priority-scoring/
```

Capabilities:

```text
supplier scoring
liquidation sourcing
auction sourcing
local pickup arbitrage
condition-adjusted pricing
counterfeit/fraud risk indicators
expected resale margin
velocity scoring
```

Acceptance criteria:

- Outputs include explicit acquisition rationale, assumptions, and risk profile.
- Purchases require approval gates on all purchase action pathways.
- Fraud/counterfeit indicators surfaced prominently in scoring outputs.
- Margin, velocity, fraud/counterfeit risk, and confidence scoring model included across sourcing recommendations.

---

## MB-ECOM-P0-005 — Ecommerce logistics and fulfillment orchestration

**Status:** Completed (2026-05-11)

Create:

```text
skills/ecommerce-fulfillment/
skills/shipping-carrier-selection/
skills/package-dimension-optimization/
skills/freight-and-pallet-analysis/
skills/warehouse-slotting-analysis/
skills/pick-pack-optimization/
skills/returns-routing-analysis/
skills/shipping-sla-risk-analysis/
```

Capabilities:

```text
carrier comparison
shipping label estimation
warehouse routing
batch shipment optimization
regional fulfillment analysis
returns cost analysis
fulfillment SLA monitoring
```

Acceptance criteria:

- Shipping recommendations include cost/time/risk tradeoffs.
- Shipping purchases require approval.
- Integrates with inventory and order entities.


Implemented skill pack:

```text
skills/ecommerce-fulfillment/
skills/shipping-carrier-selection/
skills/package-dimension-optimization/
skills/freight-and-pallet-analysis/
skills/warehouse-slotting-analysis/
skills/pick-pack-optimization/
skills/returns-routing-analysis/
skills/shipping-sla-risk-analysis/
```

Implementation notes:

- Standardized shipping recommendation outputs to require explicit `cost`, `delivery_time`, and `sla_risk` dimensions.
- Integrated fulfillment decision context with `FulfillmentOrder` and `InventoryLot` ontology entities for inventory-aware routing decisions.
- Enforced approval gates for shipping purchases and other external side effects before execution; missing approvals force analysis-only mode with `approval_requested`.


---

# P1 — Marketplace Operations and Automation

## MB-ECOM-P1-001 — Marketplace listing operations

Create:

```text
skills/marketplace-listing-generation/
skills/product-title-optimization/
skills/product-description-generation/
skills/listing-seo-optimization/
skills/listing-image-analysis/
skills/listing-quality-scoring/
skills/listing-compliance-validation/
```

Requirements:

- Marketplace-specific listing templates.
- SEO keyword optimization.
- Duplicate listing detection.
- Compliance checks against marketplace prohibited-content rules.
- Human approval before publishing.

Acceptance criteria:

- Listings include structured metadata.
- Compliance violations fail closed.
- Listings support draft mode.

---

## MB-ECOM-P1-002 — Inventory synchronization and catalog management

Create:

```text
core/catalog-normalization/
skills/multi-channel-inventory-sync/
skills/catalog-deduplication/
skills/sku-relationship-analysis/
skills/bundle-product-analysis/
skills/reorder-threshold-analysis/
```

Acceptance criteria:

- Inventory state can sync across marketplaces.
- Duplicate SKUs and stale listings detected.
- Reorder recommendations generated.

---

## MB-ECOM-P1-003 — Ecommerce analytics and profitability dashboard

Create:

```text
apps/ecommerce-dashboard/
reports/ecommerce_profitability_dashboard.json
reports/ecommerce_operations_report.md
```

Required metrics:

```text
gross margin
net margin
sell-through rate
days-on-market
inventory aging
return rate
shipping cost ratio
marketplace fee ratio
conversion rate
customer acquisition cost
```

Acceptance criteria:

- Dashboard supports marketplace/channel segmentation.
- Profitability visible at SKU and marketplace level.
- Cost attribution linked to workflow telemetry.

---

# P2 — Advanced Arbitrage and Commerce Intelligence

## MB-ECOM-P2-001 — Regional scarcity and demand intelligence

Create:

```text
skills/regional-demand-analysis/
skills/geographic-price-gap-analysis/
skills/regional-scarcity-scoring/
skills/local-market-trend-analysis/
```

Capabilities:

```text
regional pricing variance
cross-state arbitrage analysis
supply-demand imbalance detection
regional seasonality analysis
```

Acceptance criteria:

- Integrates with OldFarmTrucks workflows.
- Supports ecommerce and physical inventory use cases.
- Geographic pricing opportunities include logistics impact.

---

## MB-ECOM-P2-002 — AI-assisted negotiation and sourcing support

Create:

```text
skills/vendor-negotiation-support/
skills/bulk-purchase-negotiation-analysis/
skills/supplier-risk-negotiation-support/
skills/offer-strategy-analysis/
```

Governance:

- No autonomous negotiation commitments.
- No autonomous purchasing.
- Outbound communication approval required.

Acceptance criteria:

- Negotiation recommendations include margin/risk impact.
- Communication drafts include governance review markers.

---

## MB-ECOM-P2-003 — Ecommerce finance and tax integration

Create:

```text
skills/marketplace-tax-analysis/
skills/sales-tax-nexus-analysis/
skills/marketplace-fee-reconciliation/
skills/ecommerce-payout-reconciliation/
skills/refund-loss-analysis/
```

Acceptance criteria:

- Marketplace payouts reconcile to accounting entities.
- Tax nexus and jurisdiction reporting include professional-review flags.
- Refund and return leakage is quantified.

---

# P3 — Future Marketplace Ecosystem

## MB-ECOM-P3-001 — Supplier and reseller network graph (Completed 2026-05-12)

Create:

```text
core/commerce-network-graph/
skills/vendor-network-analysis/
skills/supplier-reputation-analysis/
skills/reseller-relationship-mapping/
```

Acceptance criteria:

- Tracks supplier reliability and pricing history.
- Supports fraud/risk correlation.
- Integrates with organizational memory.

---

## MB-ECOM-P3-002 — Autonomous commerce simulation environment (Completed 2026-05-12)

Create:

```text
core/commerce-simulator/
skills/pricing-strategy-simulation/
skills/marketplace-scenario-analysis/
skills/fulfillment-simulation/
```

Acceptance criteria:

- Simulates inventory turnover, pricing changes, fees, logistics delays, and demand shocks.
- Supports dry-run optimization without real marketplace actions.

---

# Immediate Recommended Execution Order

1. Marketplace ontology and canonical commerce entities.
2. Marketplace ingestion and scraping governance.
3. Pricing intelligence engine.
4. Product sourcing and acquisition intelligence.
5. Ecommerce logistics and fulfillment orchestration.
6. Marketplace listing operations.
7. Inventory synchronization and catalog normalization.
8. Ecommerce profitability dashboard.
9. Regional scarcity and arbitrage intelligence.
10. Ecommerce finance/tax reconciliation.

Update (2026-05-11):
- Implemented `core/marketplace-ingestion/` with source adapter contracts and sample adapters for marketplace normalization.
- Implemented `core/scraping-governor/` governance interceptors to fail closed on legal/robots/TOS and throttle violations.
- Added `schemas/marketplace-source.schema.json` for required legal, robots/TOS, throttling, network, and lineage metadata.
- Added `references/marketplace-data-policy.md` and `scripts/marketplaces/validate_source_policy.py` for policy documentation and enforcement.
- Marked MB-ECOM-P0-002 as Completed (2026-05-11).


### 2026-05-11 Update — MB-ECOM-P0-003 completed

- Added `core/pricing-intelligence/` with normalization and profitability modules for marketplace fee, shipping, and tax normalization.
- Added five pricing-intelligence skills for normalization, fee analysis, profitability, dynamic margins, and competitor pricing intelligence.
- Published `reports/marketplace_pricing_report.md` with channel-level and SKU-level examples including net margin and confidence scoring.


### 2026-05-12 Update — Listing Ops + Catalog/Inventory + Analytics Surface (MB-ECOM-P0-006/007/008)

- Implemented listing operations skills in draft-first mode with publish approval gates: `skills/marketplace-listing-generation/`, `skills/product-title-optimization/`, `skills/product-description-generation/`, `skills/listing-seo-optimization/`, `skills/listing-image-analysis/`, `skills/listing-quality-scoring/`, and `skills/listing-compliance-validation/`.
- Implemented catalog/inventory components: `core/catalog-normalization/`, `skills/multi-channel-inventory-sync/`, `skills/catalog-deduplication/`, `skills/sku-relationship-analysis/`, `skills/bundle-product-analysis/`, and `skills/reorder-threshold-analysis/`.
- Added analytics surface: `apps/ecommerce-dashboard/`, `reports/ecommerce_profitability_dashboard.json`, and `reports/ecommerce_operations_report.md`.
- Enforced required metrics in skills/reports/dashboard contracts: gross_margin, net_margin, sell_through, aging_days, return_rate, shipping_fee_ratio, conversion_rate, and cac with marketplace + SKU segmentation.

## MB-ECOM-P0-010 — Regional arbitrage, negotiation support, and finance-tax integration skills

**Status:** Completed (2026-05-12)

Create:

```text
skills/regional-demand-analysis/
skills/geographic-price-gap-analysis/
skills/regional-scarcity-scoring/
skills/local-market-trend-analysis/
skills/vendor-negotiation-support/
skills/bulk-purchase-negotiation-analysis/
skills/supplier-risk-negotiation-support/
skills/offer-strategy-analysis/
skills/marketplace-tax-analysis/
skills/sales-tax-nexus-analysis/
skills/marketplace-fee-reconciliation/
skills/ecommerce-payout-reconciliation/
skills/refund-loss-analysis/
```

Capabilities:

```text
regional demand and scarcity scoring
geographic price-gap detection with logistics impact adjustments
local market trend and velocity analysis
negotiation brief/counteroffer strategy support with explicit no-autonomous-commitment controls
marketplace tax and nexus analysis with professional-review flags
fee/payout/refund reconciliation linked to accounting entities
```

Acceptance criteria:

- All new skills operate in support-only draft mode and block autonomous external commitments.
- All negotiation outputs include explicit no-autonomous-commitment controls and HITL approval requirements.
- Tax/jurisdiction outputs include `professional_review_required: true` and explicit qualified-review messaging.
- Finance reconciliation outputs include linkage fields to accounting entities (`account_id`, `invoice_id`, `payment_id`, `order_id`, `marketplace_payout_id`).
- Opportunity scoring includes logistics-impact-aware components (landed-cost delta, lead-time risk, and fulfillment constraints).


Update (2026-05-12):
- Implemented `core/commerce-network-graph/` with organizational-memory primitive mapping for supplier reliability history, pricing history, and fraud/risk correlation signals.
- Added skills: `vendor-network-analysis`, `supplier-reputation-analysis`, and `reseller-relationship-mapping` with provenance/confidence and review-gate requirements.
- Implemented `core/commerce-simulator/` with explicit dry-run-only controls and scenario coverage for demand shocks, fee changes, logistics delays, and inventory turnover dynamics.
- Added skills: `pricing-strategy-simulation`, `marketplace-scenario-analysis`, and `fulfillment-simulation` with no-side-effects simulation safety constraints.
- Added/update documentation references under `core/commerce-network-graph/references/` and `core/commerce-simulator/references/` for signal semantics, memory integration, and simulation safeguards.
- Marked MB-ECOM-P3-001 and MB-ECOM-P3-002 as Completed (2026-05-12).
