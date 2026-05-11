# Marketplace Pricing Report

_Date: 2026-05-11_

## Channel-Level Analysis (Example)

| Channel | Avg Listed Price | Avg Marketplace Fee | Avg Shipping Cost | Avg Net Margin | Avg Confidence |
|---|---:|---:|---:|---:|---:|
| Amazon US | $29.95 | $4.49 | $3.80 | 0.2140 | 0.92 |
| Walmart Marketplace | $28.40 | $3.21 | $4.25 | 0.1875 | 0.88 |
| eBay | $31.10 | $3.58 | $4.90 | 0.2410 | 0.85 |

### Commentary
- Amazon delivers the highest confidence-adjusted contribution due to stable fee predictability.
- eBay has higher nominal margin, but larger shipping variability reduces confidence.
- Walmart margin pressure is primarily driven by shipping cost inflation.

## SKU-Level Analysis (Example)

| SKU | Channel | Net Sales Before Tax | Total Fees + Costs | COGS | Net Profit | Net Margin | Confidence |
|---|---|---:|---:|---:|---:|---:|---:|
| SKU-ALPHA-001 | Amazon US | $27.95 | $8.12 | $11.40 | $8.43 | 0.3016 | 0.94 |
| SKU-ALPHA-001 | Walmart Marketplace | $27.40 | $8.80 | $11.40 | $7.20 | 0.2628 | 0.88 |
| SKU-BETA-019 | eBay | $24.99 | $9.65 | $9.50 | $5.84 | 0.2337 | 0.82 |

## Confidence Scoring Notes
- Baseline confidence starts at **1.00**.
- Apply penalties for missing explicit fee data, default shipping assumptions, and absent tax rates.
- Scores under **0.80** should be reviewed before making automated repricing decisions.

## Recommended Next Actions
1. Improve shipping-cost telemetry for eBay listings.
2. Add fee table snapshots for Amazon promotions to reduce modeled assumptions.
3. Prioritize repricing for low-margin Walmart SKUs where confidence is at least 0.85.
