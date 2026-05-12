# Network Graph + Organizational Memory Primitives

## Reliability history signals
- Delivery SLA adherence rate by trailing 30/90/180-day windows.
- Defect/return incidence normalized by SKU family.
- Fill-rate volatility and cancellation drift over time.

## Pricing history signals
- Unit landed-cost trend curves by vendor/SKU cohort.
- Discount stability and promotion dependency patterns.
- Price-volatility and spread-to-market benchmark deltas.

## Fraud/risk correlation signals
- Shared-attribute overlap graph (tax IDs, addresses, bank rails, operator identity overlaps).
- Abnormal sequence detection (rapid entity pivots, synchronized listing edits, anomalous refund clusters).
- Counterparty exposure score propagation over multi-hop graph paths.

## Memory primitive mapping
- `memory.fact`: immutable business facts and lineage.
- `memory.timeseries`: longitudinal reliability/pricing vectors.
- `memory.signal`: model-ready risk and fraud indicators.
- `memory.hypothesis`: explainable investigations pending human review.

## Governance
- All risk signals must include feature provenance and confidence.
- Correlation does not imply causation; escalations require analyst approval checkpoints.
- Retention windows should follow enterprise policy and legal requirements.
