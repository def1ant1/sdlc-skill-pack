# Example Business Use Case — OldFarmTrucks.com

**Business:** OldFarmTrucks.com  
**Concept:** Classic truck dealership specializing in vintage farm trucks, barn finds, restored pickups, project trucks, parts sourcing, consignment, and enthusiast content.  
**Domain owner:** Apotheon.ai  
**Purpose:** Demonstrate how Apotheon AI Company OS should orchestrate short-term and long-term business workflows across marketing, sales, inventory, finance, customer operations, vendor/procurement, data analysis, governance, and executive reporting.

---

## 1. Business Scenario

OldFarmTrucks.com is an unused domain that could become a niche classic truck dealership and marketplace. The business starts lean: a small inventory of classic trucks, a website, lead capture, local-market scraping, valuation intelligence, supplier/vendor research, and content-driven demand generation.

The core business hypothesis:

> Classic farm trucks and vintage pickups are emotionally valuable, search-friendly, content-rich assets. A focused dealership can combine local sourcing, transparent vehicle storytelling, scarcity/pricing intelligence, and trusted buyer education to create a defensible niche brand.

---

## 2. Operating Model

### Primary revenue streams

1. Owned inventory sales
2. Consignment sales
3. Finder fees for sourced trucks
4. Restoration/vendor referral fees
5. Parts sourcing and affiliate/referral revenue
6. Premium buyer reports
7. Content monetization over time

### Core entities

The workflow should use canonical enterprise entities where available:

- `Lead`
- `Customer`
- `Vehicle` or `Product`
- `InventoryItem`
- `Vendor`
- `PurchaseOrder`
- `Invoice`
- `Payment`
- `Campaign`
- `Opportunity`
- `Ticket`
- `Decision`
- `WorkflowRun`

If `Vehicle` does not yet exist as a canonical entity, map it initially to `Product` + `InventoryItem` and create a backlog suggestion for `VehicleAsset`.

---

## 3. Short-Term Workflow Examples

Short-term workflows are tactical workflows that can run daily, weekly, or per transaction. They should be executable as dry-run plans using the business workflow planner.

---

# Short-Term Workflow A — Launch Readiness Sprint

## Objective

Prepare OldFarmTrucks.com for a minimum viable launch within 30 days.

## Trigger

```text
User: Plan the launch of OldFarmTrucks.com as a classic truck dealership with lead capture, inventory pages, pricing intelligence, and basic sales operations.
```

## Expected planner

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Launch OldFarmTrucks.com as a classic truck dealership in 30 days" \
  --dry-run --json
```

## Skill chain

1. `strategic-planning` — define launch goals, ICP, positioning, and constraints
2. `content-marketing` — create homepage, inventory, blog, and buyer-guide content plan
3. `seo-engineering` — define local/classic-truck SEO architecture
4. `product-analytics` — define funnel events and KPIs
5. `crm-integration` — define lead capture and opportunity stages
6. `business-orchestration` — assemble launch workflow and owners
7. `budget-planning` — estimate launch budget and operating runway
8. `legal-ops` — identify dealership/legal/compliance questions for human review
9. `executive-reporting` — produce launch-readiness dashboard

## Required outputs

- Launch checklist
- Website sitemap
- ICP and buyer personas
- Initial lead funnel
- CRM stage definitions
- Inventory page template
- Budget estimate
- Risk register
- 30-day launch plan

## HITL requirements

Human review required before:

- Publishing legal claims
- Advertising vehicles for sale
- Using scraped market data in customer-facing claims
- Sending customer emails
- Making dealership/licensing representations

---

# Short-Term Workflow B — Local Market Scarcity and Pricing Scan

## Objective

Identify undervalued classic farm trucks within a target region and estimate scarcity/pricing opportunity.

## Trigger

```text
User: Scan local market data for classic farm trucks within 300 miles and identify scarcity, pricing, and acquisition opportunities.
```

## Expected planner

```bash
python scripts/orchestration/plan_inventory_workflow.py \
  "Find classic farm truck acquisition opportunities within 300 miles" \
  --dry-run --json
```

## Skill chain

1. `local-market-data-collection` — collect listings from allowed/public sources
2. `market-data-quality-scoring` — score freshness, completeness, source reliability
3. `competitor-price-scraping` — collect competitor/listing prices where permitted
4. `scarcity-analysis` — estimate supply scarcity by make/model/year/condition/location
5. `market-pricing-intelligence` — compare asking prices to observed comps
6. `arbitrage-opportunity-detection` — rank acquisition candidates
7. `inventory-forecasting` — estimate holding period and sales velocity
8. `financial-scenario-modeling` — estimate gross margin scenarios
9. `executive-reporting` — summarize buy/no-buy recommendations

## Required outputs

- Candidate truck acquisition list
- Source URLs and timestamps
- Asking price distribution
- Scarcity score
- Estimated acquisition cost
- Estimated sale price range
- Gross margin estimate
- Confidence score
- Data quality score
- Human-review queue

## Governance requirements

- Respect robots.txt, site terms, and rate limits
- No login bypass or access-control circumvention
- Store observed data separately from inferred valuation
- Flag low-confidence listings
- Require human approval before contacting sellers or making offers

---

# Short-Term Workflow C — Inbound Lead Qualification and Follow-Up

## Objective

Qualify inbound buyer leads and draft appropriate follow-up responses.

## Trigger

```text
User: Qualify new leads for OldFarmTrucks.com and draft follow-up messages for review.
```

## Expected planner

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Qualify inbound classic truck buyer leads and draft follow-up" \
  --dry-run --json
```

## Skill chain

1. `crm-integration` — ingest lead/contact/opportunity records
2. `lead-scoring` — score buyer intent, budget, urgency, fit, and location
3. `customer-journey-analysis` — identify buyer stage
4. `proposal-automation` — prepare vehicle options or sourcing proposal
5. `customer-communication-policy` — check outbound communication rules
6. `approval-queue-management` — route drafts for human approval
7. `sales-pipeline-forecasting` — update expected pipeline value
8. `executive-reporting` — summarize lead quality and next actions

## Required outputs

- Lead score
- Buyer profile
- Recommended next action
- Draft email/SMS for human review
- Pipeline stage recommendation
- Follow-up reminder recommendation
- Risk flags

## HITL requirements

- Never send customer-facing communication without approval unless policy explicitly allows it
- Do not make financing/legal claims
- Flag high-value buyers for owner review

---

# Short-Term Workflow D — Vehicle Intake and Listing Preparation

## Objective

Turn a newly acquired or consigned classic truck into a complete inventory listing.

## Trigger

```text
User: Prepare a new listing for a 1967 Ford F-100 farm truck with photos, condition notes, and estimated pricing.
```

## Expected planner

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Prepare a complete listing for a 1967 Ford F-100 farm truck" \
  --dry-run --json
```

## Skill chain

1. `inventory-forecasting` — create inventory item record
2. `product-lifecycle-intelligence` — classify asset as project/restored/driver/parts
3. `market-pricing-intelligence` — estimate price range from comps
4. `content-marketing` — draft listing copy and story
5. `seo-engineering` — optimize title/meta/structured data
6. `brand-sentiment-analysis` — check messaging trust and clarity
7. `legal-ops` — flag title/disclosure requirements for human review
8. `customer-communication-policy` — verify claims and disclaimers
9. `executive-reporting` — summarize listing readiness

## Required outputs

- Inventory record
- Condition summary
- Disclosure checklist
- Listing title
- Listing description
- SEO metadata
- Suggested price range
- Photo checklist
- Human approval checklist

---

# Short-Term Workflow E — Weekly Operating Review

## Objective

Produce a weekly owner/operator report for OldFarmTrucks.com.

## Trigger

```text
User: Create this week's operating review for OldFarmTrucks.com.
```

## Expected planner

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Create weekly operating review for OldFarmTrucks.com" \
  --dry-run --json
```

## Skill chain

1. `analytics-intelligence` — collect web, lead, and campaign data
2. `sales-pipeline-forecasting` — summarize pipeline movement
3. `inventory-forecasting` — summarize inventory status and aging
4. `budget-variance-analysis` — compare actuals vs budget
5. `customer-health-scoring` — summarize buyer/customer health
6. `marketing-attribution` — summarize channel performance
7. `decision-intelligence` — identify key decisions needed
8. `executive-reporting` — produce weekly operating review

## Required outputs

- KPI dashboard
- Traffic/leads/conversion summary
- Inventory aging report
- Pipeline forecast
- Budget variance
- Marketing channel performance
- Risks/blockers
- Decisions needed
- Next-week priorities

---

## 4. Long-Term Workflow Examples

Long-term workflows are strategic, multi-week or multi-quarter workflows that use persistent memory, periodic reporting, and adaptive planning.

---

# Long-Term Workflow A — 12-Month Dealership Buildout

## Objective

Build OldFarmTrucks.com from unused domain into a revenue-generating classic truck dealership over 12 months.

## Trigger

```text
User: Build a 12-month plan to turn OldFarmTrucks.com into a profitable classic truck dealership.
```

## Expected planner

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Build a 12-month plan to make OldFarmTrucks.com a profitable classic truck dealership" \
  --dry-run --json
```

## Strategic phases

### Phase 1 — Foundation, 0–30 days

- Brand positioning
- Website launch
- CRM setup
- Analytics setup
- Basic legal/compliance review
- Initial sourcing criteria
- Initial content plan

### Phase 2 — Market validation, 31–90 days

- Publish buyer guides
- Build lead capture
- Test paid/local acquisition
- Source first vehicles
- Build pricing intelligence database
- Validate buyer demand by segment

### Phase 3 — Operating system buildout, 91–180 days

- Formalize acquisition pipeline
- Vendor/restoration partner network
- Inventory aging dashboard
- Weekly operating review cadence
- Sales follow-up automation
- Consignment process

### Phase 4 — Scale and optimization, 181–365 days

- Expand geographic sourcing radius
- Launch newsletter/community
- Add parts/referral monetization
- Create premium buyer reports
- Build repeatable acquisition playbook
- Optimize pricing and sales velocity

## Skill chain

1. `strategic-planning`
2. `market-pricing-intelligence`
3. `content-strategy`
4. `seo-intelligence`
5. `crm-integration`
6. `sales-pipeline-forecasting`
7. `inventory-forecasting`
8. `vendor-scorecarding`
9. `budget-planning`
10. `cash-flow-forecasting`
11. `decision-intelligence`
12. `executive-reporting`
13. `lessons-learned-extraction`
14. `workflow-optimization-loop`

## Required outputs

- 12-month roadmap
- KPI tree
- budget and runway estimate
- channel strategy
- sourcing strategy
- inventory strategy
- vendor strategy
- governance/risk plan
- monthly operating cadence
- quarterly strategic review template

## Long-term memory requirements

Persist:

- Market observations
- Acquisition decisions
- Pricing assumptions
- Buyer objections
- Vehicle sale outcomes
- Vendor performance
- Campaign performance
- Lessons learned

---

# Long-Term Workflow B — Pricing Intelligence and Valuation Model

## Objective

Build a continuously improving classic truck valuation model for acquisition and sales pricing.

## Trigger

```text
User: Build a pricing intelligence workflow for classic farm trucks and vintage pickups.
```

## Cadence

- Daily: collect fresh market listings
- Weekly: update comps and scarcity scores
- Monthly: review model assumptions
- Quarterly: evaluate pricing accuracy against actual sale outcomes

## Skill chain

1. `local-market-data-collection`
2. `market-data-quality-scoring`
3. `competitor-price-scraping`
4. `scarcity-analysis`
5. `market-pricing-intelligence`
6. `financial-scenario-modeling`
7. `causal-analysis`
8. `workflow-ab-testing`
9. `lessons-learned-extraction`
10. `executive-reporting`

## Required outputs

- Make/model/year pricing bands
- Condition-adjusted comp model
- Regional scarcity map
- Acquisition target list
- Price confidence score
- Expected sale velocity
- Gross margin forecast
- Valuation accuracy report

## Evaluation metrics

- Pricing error vs final sale price
- Time-to-sale prediction accuracy
- Gross margin forecast error
- Data freshness
- Source reliability
- Acquisition recommendation hit rate

---

# Long-Term Workflow C — Content and Community Growth Engine

## Objective

Use content, SEO, email, and community building to make OldFarmTrucks.com a trusted destination for classic farm truck buyers and sellers.

## Trigger

```text
User: Create a long-term content and community growth workflow for OldFarmTrucks.com.
```

## Cadence

- Weekly: publish content
- Weekly: review search performance
- Monthly: update content calendar
- Monthly: analyze buyer/seller questions
- Quarterly: update brand positioning and ICP assumptions

## Skill chain

1. `content-strategy`
2. `content-marketing`
3. `seo-intelligence`
4. `ai-search-optimization`
5. `brand-sentiment-analysis`
6. `persona-modeling`
7. `marketing-attribution`
8. `customer-journey-analysis`
9. `voice-of-customer-analysis`
10. `executive-reporting`

## Content pillars

1. Buyer education
2. Seller education
3. Truck histories and restoration stories
4. Market pricing analysis
5. Farm truck buying checklists
6. Maintenance and parts sourcing
7. Regional barn-find stories
8. Ownership lifestyle and nostalgia

## Required outputs

- Editorial calendar
- SEO keyword map
- AI-search optimization checklist
- Newsletter plan
- Social content plan
- Buyer/seller FAQ
- Content performance dashboard
- Community growth metrics

---

# Long-Term Workflow D — Inventory Acquisition and Vendor Network

## Objective

Build a repeatable sourcing network for classic trucks, restoration partners, inspection vendors, title services, transport, and parts suppliers.

## Trigger

```text
User: Build a vendor and acquisition network for OldFarmTrucks.com.
```

## Cadence

- Weekly: review acquisition leads
- Monthly: update vendor scorecards
- Quarterly: renegotiate/refine vendor network

## Skill chain

1. `supplier-risk-intelligence`
2. `vendor-scorecarding`
3. `vendor-risk-analysis`
4. `procurement-automation`
5. `contract-renewal-intelligence`
6. `purchase-approval-routing`
7. `inventory-forecasting`
8. `sku-margin-analysis`
9. `business-policy-engine`
10. `executive-reporting`

## Vendor categories

- Vehicle scouts
- Mechanics
- Restoration shops
- Detailers
- Transport providers
- Title/registration specialists
- Parts suppliers
- Photographers/videographers
- Auction contacts
- Storage/warehouse partners

## Required outputs

- Vendor database
- Vendor scorecards
- Risk ratings
- Preferred partner list
- Approval thresholds
- Contract/terms checklist
- Cost benchmarks
- Vendor performance dashboard

---

# Long-Term Workflow E — Dealership Governance and Financial Control System

## Objective

Create an operating control system for payments, vehicle acquisitions, listings, customer communications, legal review, and financial performance.

## Trigger

```text
User: Design governance and financial controls for OldFarmTrucks.com operations.
```

## Skill chain

1. `business-policy-engine`
2. `business-approval-gateway`
3. `business-audit-ledger`
4. `financial-control-monitoring`
5. `expense-policy-compliance`
6. `accounting-operations`
7. `budget-variance-analysis`
8. `legal-ops`
9. `compliance-governance`
10. `executive-reporting`

## Required controls

- Vehicle purchase approval threshold
- Seller contact approval rules
- Customer communication approval rules
- Listing publication approval
- Payment authorization
- Vendor onboarding review
- Legal/title document review
- Data scraping policy compliance
- Financial audit trail
- Monthly close checklist

## Required outputs

- Business policy matrix
- Approval workflow map
- Audit event model
- Monthly financial control checklist
- Risk register
- Evidence pack template
- Executive control dashboard

---

## 5. Example Workflow Plan JSON Shape

All business workflow planners should output a deterministic plan compatible with the workflow runtime.

```json
{
  "workflow_id": "oldfarmtrucks-launch-readiness-001",
  "business": "OldFarmTrucks.com",
  "objective": "Launch OldFarmTrucks.com as a classic truck dealership in 30 days",
  "mode": "dry_run",
  "risk_level": "medium",
  "requires_human_approval": true,
  "canonical_entities": ["Lead", "Customer", "Product", "InventoryItem", "Vendor", "Campaign", "Opportunity", "Decision"],
  "steps": [
    {
      "order": 1,
      "skill": "strategic-planning",
      "purpose": "Define launch strategy, ICP, positioning, constraints, and 30-day outcome targets.",
      "inputs": ["business concept", "domain", "target market", "constraints"],
      "outputs": ["launch strategy", "ICP", "positioning", "success metrics"],
      "governance": {
        "hitl_required": false,
        "policy_refs": []
      }
    },
    {
      "order": 2,
      "skill": "local-market-data-collection",
      "purpose": "Collect permitted public market data for classic truck supply and pricing.",
      "inputs": ["target geography", "vehicle criteria", "approved data sources"],
      "outputs": ["market observations", "source URLs", "data quality score"],
      "governance": {
        "hitl_required": true,
        "policy_refs": ["docs/governance/data-scraping-policy.md"]
      }
    }
  ],
  "success_metrics": [
    "site launched",
    "lead capture active",
    "first inventory listings published",
    "market pricing report generated",
    "weekly operating review cadence established"
  ],
  "reports": [
    "launch_readiness_report.md",
    "market_pricing_report.md",
    "weekly_operating_review.md"
  ]
}
```

---

## 6. Required Planner Test Cases

These examples should become tests for business workflow planner coverage.

```text
1. Launch OldFarmTrucks.com as a classic truck dealership in 30 days.
2. Find acquisition opportunities for classic farm trucks within 300 miles.
3. Qualify inbound buyer leads and draft follow-up messages for review.
4. Prepare a listing for a 1967 Ford F-100 farm truck.
5. Create this week's operating review for OldFarmTrucks.com.
6. Build a 12-month plan to make OldFarmTrucks.com profitable.
7. Build a pricing intelligence workflow for classic farm trucks.
8. Create a long-term content and community growth workflow.
9. Build a vendor and acquisition network.
10. Design governance and financial controls for dealership operations.
```

---

## 7. Gaps Revealed by This Example

This example should drive concrete project improvements:

1. Add `VehicleAsset` or `Vehicle` as a canonical entity.
2. Ensure business planners can route dealership workflows across marketing, sales, inventory, finance, legal, and governance.
3. Ensure market scraping workflows are governed by data scraping policy.
4. Ensure customer communication workflows require approval.
5. Ensure finance/payment/procurement actions require approval.
6. Ensure long-term workflows persist memory and lessons learned.
7. Ensure weekly/monthly/quarterly recurring workflow patterns are represented in planner outputs.
8. Ensure release smoke tests include one OldFarmTrucks.com short-term workflow and one long-term workflow.

---

## 8. Recommended Release Smoke Test Additions

Add these to `scripts/smoke_test_release.py` once the business workflow planners exist:

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Launch OldFarmTrucks.com as a classic truck dealership in 30 days" \
  --dry-run --json

python scripts/orchestration/plan_business_workflow.py \
  "Build a 12-month plan to make OldFarmTrucks.com profitable" \
  --dry-run --json

python scripts/orchestration/plan_inventory_workflow.py \
  "Find acquisition opportunities for classic farm trucks within 300 miles" \
  --dry-run --json

python scripts/orchestration/plan_customer_workflow.py \
  "Qualify inbound classic truck buyer leads and draft follow-up" \
  --dry-run --json
```

---

## 9. Business Value of the Example

OldFarmTrucks.com is a good release validation example because it exercises nearly every enterprise domain:

| Domain | Example Need |
|---|---|
| Strategy | 12-month dealership buildout |
| Marketing | SEO, content, community, AI search |
| Sales | Lead qualification, pipeline, proposals |
| Customer | Follow-up, buyer journey, satisfaction |
| Inventory | Vehicle intake, pricing, aging, sourcing |
| Finance | budget, cash flow, margin, controls |
| Vendor | restoration, transport, parts, scouts |
| Legal/Governance | title, disclosures, approvals, policies |
| Data | local market scraping, pricing intelligence |
| Reporting | weekly operating review, executive dashboards |
| Learning | pricing model improvement, lessons learned |

This makes it a strong canonical example for release testing and onboarding.
