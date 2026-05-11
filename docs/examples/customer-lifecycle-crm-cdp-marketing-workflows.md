# Example Business Use Case — Complete Customer Lifecycle CRM/CDP/Marketing Workflows

**Example business:** OldFarmTrucks.com  
**Business type:** Classic truck dealership, consignment marketplace, sourcing service, and enthusiast content brand  
**Purpose:** Demonstrate full customer lifecycle orchestration across CRM, CDP, marketing automation, sales, customer success, service, analytics, governance, and executive reporting.

---

## 1. Why This Example Exists

This example gives Apotheon AI Company OS a concrete customer-management reference scenario that spans the complete lifecycle:

```text
Anonymous visitor
→ known lead
→ marketing-qualified lead
→ sales-qualified lead
→ opportunity
→ buyer/customer
→ onboarded customer
→ repeat buyer/seller
→ advocate/referral source
→ churn risk / inactive contact
→ win-back candidate
```

The example is intentionally designed to exercise CRM integration, CDP profile unification, journey orchestration, segmentation, lead scoring, campaigns, attribution, customer communication governance, sales forecasting, support/service workflows, retention, expansion, referral loops, privacy/consent controls, and executive reporting.

---

## 2. Customer Lifecycle Model

| Stage | Description | Primary systems | Example OldFarmTrucks signal |
|---|---|---|---|
| Anonymous Visitor | Unknown website or content visitor | Web analytics, CDP | Reads article: Best 1960s Ford farm trucks |
| Known Visitor | Visitor submits email or identifies | CDP, email platform | Downloads buyer checklist |
| Lead | Contact expresses general interest | CRM, CDP | Submits form for classic truck sourcing |
| MQL | Marketing-qualified based on fit/engagement | CRM, marketing automation | Opens 3 emails and views inventory pages |
| SQL | Sales-qualified by intent/budget/timeline | CRM | Requests help finding a 1967 Ford F-100 |
| Opportunity | Active deal or sourcing engagement | CRM, quoting/proposal | Receives vehicle sourcing proposal |
| Customer | Purchases, consigns, or pays finder fee | CRM, accounting | Buys a listed truck or signs consignment |
| Onboarded Customer | Receives post-sale support and education | CRM, service desk | Receives title/transport checklist |
| Repeat/Expansion | Buys/sells again, requests services | CRM, CDP | Requests restoration partner referral |
| Advocate | Refers others or creates testimonial | CRM, marketing | Shares story/photo testimonial |
| At-Risk/Inactive | Engagement drops or deal stalls | CRM, CDP | No response after proposal; abandoned inquiry |
| Win-Back | Re-engagement opportunity | CRM, marketing automation | Responds to new inventory alert |

---

## Canonical Entity + Lifecycle Taxonomy Baseline (MB-P2-002)

All CRM/CDP/marketing/customer-lifecycle workflows in this pack must normalize to: `customer`, `lead`, `opportunity`, `campaign`, and `ticket`.

Required lifecycle taxonomy:

`anonymous -> known_lead -> mql -> sql -> opportunity_open -> opportunity_closed_won|opportunity_closed_lost -> onboarding -> active -> at_risk -> renewed|churned`

Outbound communication enforcement baseline:
- Verify consent before each outbound communication attempt.
- Enforce suppression/unsubscribe status.
- Enforce communication preferences (channel/frequency/quiet-hours).
- Require explicit approval for outbound communication unless active policy explicitly permits lifecycle automation for that segment/channel.

---

## 3. Canonical Customer Data Model

Required canonical entities:

```text
Account
Contact
Customer
Lead
Opportunity
Campaign
Ticket
Product
InventoryItem
Invoice
Payment
Decision
WorkflowRun
ConsentRecord
CommunicationPreference
CustomerEvent
Segment
```

If missing, create backlog suggestions for:

```text
ConsentRecord
CommunicationPreference
CustomerEvent
Segment
VehicleInterestProfile
LifecycleStage
AttributionTouchpoint
```

Unified profile shape:

```yaml
customer_profile:
  profile_id:
  account_id:
  contact_id:
  lifecycle_stage:
  identity_resolution:
    email:
    phone:
    cookie_id:
    crm_id:
    cdp_id:
  consent:
    email_marketing:
    sms_marketing:
    data_processing_basis:
    last_updated:
  preferences:
    truck_makes:
    truck_years:
    condition_interest:
    budget_range:
    geography:
    purchase_timeline:
    buyer_or_seller:
  engagement:
    website_visits:
    content_downloads:
    inventory_views:
    email_opens:
    email_clicks:
    form_submissions:
  sales:
    lead_score:
    fit_score:
    intent_score:
    opportunity_value:
    pipeline_stage:
    next_best_action:
  service:
    tickets_open:
    satisfaction_score:
    post_sale_tasks:
  attribution:
    first_touch:
    last_touch:
    multi_touch_summary:
  risk:
    churn_risk:
    stale_lead_risk:
    communication_risk:
```

---

# 4. Short-Term Lifecycle Workflows

## Workflow 1 — Anonymous Visitor to Known Lead

**Objective:** Convert anonymous OldFarmTrucks.com visitors into known leads using educational content and compliant lead capture.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Convert anonymous OldFarmTrucks.com visitors into known leads using buyer guides and inventory alerts" \
  --dry-run --json
```

**Skill chain:**

1. `analytics-intelligence` — identify high-intent pages and anonymous behavior patterns
2. `content-marketing` — define lead magnets and calls to action
3. `seo-intelligence` — map organic entry pages to buyer intent
4. `cdp-profile-unification` — create anonymous-to-known identity resolution rules
5. `marketing-attribution` — define first-touch attribution logic
6. `customer-journey-analysis` — define conversion path
7. `customer-communication-policy` — verify consent and messaging boundaries
8. `executive-reporting` — summarize visitor-to-lead funnel

**Required outputs:** lead magnet list, landing page recommendations, anonymous event taxonomy, form fields, consent language, identity stitching rules, attribution rules, KPI dashboard.

**Governance:** no marketing messages without consent; track consent source/timestamp; avoid dark patterns; respect privacy and retention policy.

---

## Workflow 2 — Lead Scoring and MQL Qualification

**Objective:** Score known leads and identify marketing-qualified leads based on fit, intent, engagement, and buying timeline.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Score OldFarmTrucks.com leads and identify which are ready for sales follow-up" \
  --dry-run --json
```

**Skill chain:**

1. `crm-integration` — read lead/contact records and CRM stage
2. `cdp-profile-unification` — merge web/email/CRM behavior
3. `lead-scoring` — compute fit, intent, engagement, urgency, and value scores
4. `persona-modeling` — classify buyer/seller/restorer/collector segment
5. `customer-journey-analysis` — identify lifecycle stage
6. `sales-pipeline-forecasting` — estimate near-term opportunity potential
7. `approval-queue-management` — route high-value leads for owner review
8. `executive-reporting` — summarize MQL volume and quality

**Required outputs:** lead score, fit score, intent score, segment/persona, MQL/SQL recommendation, next action, evidence, confidence, human-review queue.

**Metrics:** MQL-to-SQL conversion, SQL-to-opportunity conversion, false-positive MQL rate, time-to-first-response, pipeline value created.

---

## Workflow 3 — Personalized Nurture Campaign

**Objective:** Create personalized nurture campaigns for different customer segments.

**Planner command:**

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Create nurture campaigns for OldFarmTrucks.com leads by segment and purchase timeline" \
  --dry-run --json
```

**Segments:** classic truck buyer, project truck buyer, restored truck buyer, seller/consignor, restoration enthusiast, parts seeker, high-budget collector, local farm/ranch nostalgia buyer.

**Skill chain:**

1. `cdp-profile-unification`
2. `persona-modeling`
3. `content-strategy`
4. `campaign-optimization`
5. `marketing-attribution`
6. `customer-communication-policy`
7. `brand-sentiment-analysis`
8. `approval-queue-management`

**Required outputs:** segment definitions, campaign map, sequence drafts, suppression rules, frequency caps, consent requirements, KPI targets, approval checklist.

**Governance:** marketing communications require consent; campaign copy requires review before activation; legal/title/condition claims must be verified.

---

## Workflow 4 — Sales Follow-Up and Opportunity Creation

**Objective:** Turn qualified leads into CRM opportunities with a clear next best action.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Convert qualified OldFarmTrucks.com leads into opportunities and draft sales follow-up for review" \
  --dry-run --json
```

**Skill chain:**

1. `crm-integration`
2. `opportunity-risk-analysis`
3. `proposal-automation`
4. `pricing-optimization`
5. `customer-communication-policy`
6. `approval-queue-management`
7. `sales-pipeline-forecasting`
8. `executive-reporting`

**Required outputs:** opportunity draft, deal qualification summary, buyer/seller needs summary, next-best action, draft follow-up, forecast value, risk flags, approval request.

---

## Workflow 5 — Customer Onboarding After Purchase or Consignment

**Objective:** Create post-sale and post-consignment onboarding workflows.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Create onboarding workflows for buyers and sellers after an OldFarmTrucks.com transaction" \
  --dry-run --json
```

**Buyer onboarding:** purchase confirmation, payment/title checklist, transport checklist, insurance/registration reminders, vehicle care guide, post-delivery check-in, testimonial/referral request.

**Seller/consignor onboarding:** consignment agreement checklist, vehicle documentation checklist, photo/intake checklist, listing approval workflow, pricing agreement, status cadence, sale completion checklist.

**Skill chain:** `crm-integration`, `customer-journey-analysis`, `support-ticket-intelligence`, `legal-ops`, `customer-communication-policy`, `approval-queue-management`, `voice-of-customer-analysis`, `executive-reporting`.

**Required outputs:** buyer checklist, seller checklist, communication templates, document checklist, support templates, feedback request, owner approval checklist.

---

## Workflow 6 — Service, Support, and Escalation

**Objective:** Handle support requests, title questions, transport issues, or vehicle condition disputes.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Triage and route OldFarmTrucks.com customer support requests" \
  --dry-run --json
```

**Skill chain:**

1. `support-ticket-intelligence`
2. `sla-risk-detection`
3. `customer-health-scoring`
4. `legal-ops`
5. `customer-communication-policy`
6. `approval-queue-management`
7. `voice-of-customer-analysis`
8. `executive-reporting`

**Required outputs:** classification, priority, suggested response, escalation recommendation, legal/review flag, health update, root-cause category, follow-up tasks.

**Governance:** legal/title/dispute issues require human review; resolution offers require approval; do not admit liability or make binding commitments autonomously.

---

# 5. Long-Term Lifecycle Workflows

## Workflow 7 — Customer 360 and CDP Unification Program

**Objective:** Build a unified Customer 360 view across website behavior, CRM data, email engagement, sales activity, support requests, and purchase history.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Build a Customer 360 and CDP unification workflow for OldFarmTrucks.com" \
  --dry-run --json
```

**Skill chain:** `cdp-profile-unification`, `entity-resolution`, `golden-record-management`, `data-quality-scoring`, `crm-integration`, `marketing-attribution`, `customer-health-scoring`, `privacy-runtime`, `executive-reporting`.

**Required outputs:** Customer 360 schema, identity resolution rules, golden record policy, data quality dashboard, consent/preference model, source-of-record map, duplicate customer report, lifecycle-stage dashboard.

**Metrics:** duplicate profile rate, matched identity confidence, missing consent rate, unknown lifecycle-stage rate, CRM/CDP sync error rate.

---

## Workflow 8 — Lifecycle Marketing Automation Program

**Objective:** Create lifecycle campaigns across awareness, lead nurture, sales, onboarding, retention, referral, and win-back.

**Planner command:**

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Build lifecycle marketing automation for OldFarmTrucks.com" \
  --dry-run --json
```

**Campaign tracks:** awareness education, buyer checklist, seller/consignment education, inventory alerts, abandoned inquiry, proposal follow-up, post-purchase onboarding, referral/testimonial request, inactive lead win-back.

**Skill chain:** `content-strategy`, `campaign-optimization`, `persona-modeling`, `customer-journey-analysis`, `marketing-attribution`, `brand-sentiment-analysis`, `customer-communication-policy`, `approval-queue-management`, `workflow-ab-testing`, `executive-reporting`.

**Required outputs:** lifecycle campaign map, segment message matrix, trigger rules, suppression rules, frequency caps, A/B test plan, consent checks, KPI dashboard, approval workflow.

**Metrics:** lead-to-MQL, MQL-to-SQL, email engagement, inventory alert conversion, proposal follow-up conversion, purchase conversion, referral rate, unsubscribe/complaint rate.

---

## Workflow 9 — Customer Health, Retention, and Expansion

**Objective:** Track customer health and identify repeat purchase, referral, restoration/vendor referral, consignment, and win-back opportunities.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Create a customer health and retention workflow for OldFarmTrucks.com" \
  --dry-run --json
```

**Skill chain:** `customer-health-scoring`, `churn-risk-detection`, `account-expansion-intelligence`, `voice-of-customer-analysis`, `support-ticket-intelligence`, `customer-journey-analysis`, `proposal-automation`, `approval-queue-management`, `executive-reporting`.

**Required outputs:** health score, churn/inactivity risk, expansion/referral list, repeat-buyer candidates, seller/consignment candidates, retention playbook, draft outreach for review, retention dashboard.

**Governance:** outreach requires approval unless policy allows automated lifecycle messaging; use consent/preferences before marketing or SMS; avoid sensitive inferences unrelated to truck buying/selling.

---

## Workflow 10 — Marketing Attribution and Revenue Intelligence

**Objective:** Connect marketing touchpoints to pipeline, revenue, repeat transactions, and referral outcomes.

**Planner command:**

```bash
python scripts/orchestration/plan_business_workflow.py \
  "Build marketing attribution and revenue intelligence for OldFarmTrucks.com" \
  --dry-run --json
```

**Skill chain:** `analytics-intelligence`, `marketing-attribution`, `crm-integration`, `cdp-profile-unification`, `sales-pipeline-forecasting`, `revenue-optimization`, `fpa-analysis`, `executive-reporting`.

**Required outputs:** attribution model recommendation, channel report, campaign-to-pipeline dashboard, campaign-to-revenue dashboard, CAC estimate, LTV estimate, payback period estimate, revenue forecast assumptions.

**Metrics:** cost per lead, cost per MQL, cost per opportunity, cost per sold vehicle/transaction, lead source quality, pipeline velocity, revenue by channel, LTV/CAC.

---

## Workflow 11 — Win-Back and Re-Engagement Program

**Objective:** Identify inactive leads/customers and create compliant re-engagement campaigns.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Build a win-back workflow for inactive OldFarmTrucks.com leads and past customers" \
  --dry-run --json
```

**Skill chain:** `cdp-profile-unification`, `churn-risk-detection`, `customer-segmentation`, `campaign-optimization`, `content-marketing`, `customer-communication-policy`, `marketing-attribution`, `workflow-ab-testing`, `executive-reporting`.

**Required outputs:** inactive segments, suppression list, consent eligibility list, win-back message strategy, draft sequence, approval request, performance dashboard.

**Governance:** honor unsubscribes and suppression lists; do not contact customers without valid consent/legal basis; include opt-out where required.

---

## Workflow 12 — Advocacy, Referral, and Testimonial Engine

**Objective:** Turn satisfied customers into referrals, reviews, testimonials, and community content.

**Planner command:**

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Build a referral and testimonial workflow for OldFarmTrucks.com customers" \
  --dry-run --json
```

**Skill chain:** `customer-health-scoring`, `voice-of-customer-analysis`, `brand-sentiment-analysis`, `content-marketing`, `customer-communication-policy`, `approval-queue-management`, `marketing-attribution`, `executive-reporting`.

**Required outputs:** advocate candidate list, referral timing rules, testimonial templates, photo/story permission checklist, review request policy, community content plan, referral dashboard.

**Governance:** obtain permission before using names, photos, vehicle images, testimonials, or stories; do not alter testimonial meaning; track source permissions and usage rights.

---

# 6. Customer Lifecycle Event Taxonomy

```text
visitor.page_viewed
visitor.content_downloaded
visitor.form_submitted
lead.created
lead.enriched
lead.scored
lead.mql_created
lead.sql_created
opportunity.created
opportunity.stage_changed
proposal.sent_for_approval
proposal.approved
proposal.sent
customer.created
customer.purchase_completed
customer.onboarding_started
customer.onboarding_completed
ticket.created
ticket.escalated
customer.health_changed
campaign.enrolled
campaign.email_opened
campaign.email_clicked
campaign.unsubscribed
customer.referral_created
customer.testimonial_permission_granted
customer.winback_eligible
customer.reactivated
consent.updated
communication.suppressed
```

---

# 7. Example Workflow Plan JSON Shape

```json
{
  "workflow_id": "oldfarmtrucks-customer-lifecycle-001",
  "business": "OldFarmTrucks.com",
  "objective": "Build lifecycle marketing automation across awareness, nurture, sales, onboarding, retention, referral, and win-back",
  "mode": "dry_run",
  "risk_level": "high",
  "requires_human_approval": true,
  "canonical_entities": [
    "Lead",
    "Contact",
    "Customer",
    "Opportunity",
    "Campaign",
    "Ticket",
    "ConsentRecord",
    "CommunicationPreference",
    "CustomerEvent",
    "Segment"
  ],
  "systems": ["CRM", "CDP", "marketing automation", "web analytics", "service desk", "accounting"],
  "steps": [
    {
      "order": 1,
      "skill": "cdp-profile-unification",
      "purpose": "Unify website, email, CRM, support, and purchase data into Customer 360 profiles.",
      "inputs": ["web events", "CRM contacts", "email engagement", "support tickets", "purchase history"],
      "outputs": ["unified profiles", "identity confidence", "duplicate report", "consent map"],
      "governance": {
        "hitl_required": false,
        "policy_refs": ["docs/governance/professional-advice-boundaries.md"]
      }
    },
    {
      "order": 2,
      "skill": "campaign-optimization",
      "purpose": "Design lifecycle campaigns with segment rules, triggers, suppression rules, and KPIs.",
      "inputs": ["segments", "lifecycle stages", "content map", "consent rules"],
      "outputs": ["campaign map", "message matrix", "A/B test plan", "approval queue"],
      "governance": {
        "hitl_required": true,
        "policy_refs": ["docs/governance/customer-communication-policy.md"]
      }
    }
  ],
  "success_metrics": [
    "visitor-to-lead conversion",
    "lead-to-MQL conversion",
    "MQL-to-SQL conversion",
    "opportunity creation rate",
    "purchase conversion",
    "onboarding completion",
    "repeat/referral rate",
    "win-back reactivation"
  ]
}
```

---

# 8. Required Planner Test Cases

```text
1. Convert anonymous OldFarmTrucks.com visitors into known leads using buyer guides and inventory alerts.
2. Score OldFarmTrucks.com leads and identify which are ready for sales follow-up.
3. Create nurture campaigns for OldFarmTrucks.com leads by segment and purchase timeline.
4. Convert qualified OldFarmTrucks.com leads into opportunities and draft sales follow-up for review.
5. Create onboarding workflows for buyers and sellers after an OldFarmTrucks.com transaction.
6. Triage and route OldFarmTrucks.com customer support requests.
7. Build a Customer 360 and CDP unification workflow for OldFarmTrucks.com.
8. Build lifecycle marketing automation for OldFarmTrucks.com.
9. Create a customer health and retention workflow for OldFarmTrucks.com.
10. Build marketing attribution and revenue intelligence for OldFarmTrucks.com.
11. Build a win-back workflow for inactive OldFarmTrucks.com leads and past customers.
12. Build a referral and testimonial workflow for OldFarmTrucks.com customers.
```

---

# 9. Gaps Revealed by This Customer Lifecycle Example

1. Add or verify `cdp-profile-unification` skill.
2. Add or verify `customer-segmentation` skill.
3. Add or verify `customer-communication-policy` governance document and skill references.
4. Add canonical entities for `ConsentRecord`, `CommunicationPreference`, `CustomerEvent`, `Segment`, `LifecycleStage`, and `AttributionTouchpoint`.
5. Add customer lifecycle event schemas listed above.
6. Ensure CRM/CDP/marketing skills reference privacy and consent policies.
7. Ensure outbound customer communications route through approval or explicit policy exception.
8. Ensure customer lifecycle workflows are included in release smoke tests.
9. Ensure marketing attribution connects to revenue, not just traffic or engagement.
10. Ensure CDP identity resolution emits confidence and data lineage.
11. Ensure suppression lists and unsubscribe states are respected.
12. Ensure testimonial/referral workflows capture permission and usage rights.

---

# 10. Recommended Release Smoke Test Additions

```bash
python scripts/orchestration/plan_customer_workflow.py \
  "Build lifecycle marketing automation for OldFarmTrucks.com" \
  --dry-run --json

python scripts/orchestration/plan_customer_workflow.py \
  "Build a Customer 360 and CDP unification workflow for OldFarmTrucks.com" \
  --dry-run --json

python scripts/orchestration/plan_customer_workflow.py \
  "Create a customer health and retention workflow for OldFarmTrucks.com" \
  --dry-run --json

python scripts/orchestration/plan_business_workflow.py \
  "Build marketing attribution and revenue intelligence for OldFarmTrucks.com" \
  --dry-run --json
```

---

# 11. Business Value of Complete Lifecycle Coverage

| Lifecycle area | Business value |
|---|---|
| Anonymous visitor conversion | Turns content traffic into owned audience |
| CDP unification | Creates trustworthy Customer 360 profiles |
| Lead scoring | Prioritizes owner/sales attention |
| Nurture campaigns | Moves long-cycle buyers toward action |
| Opportunity creation | Connects marketing to revenue |
| Onboarding | Reduces post-sale confusion and support burden |
| Support escalation | Protects reputation and customer trust |
| Retention/expansion | Increases repeat transactions and referrals |
| Win-back | Recovers stale pipeline and inactive customers |
| Advocacy | Builds social proof and organic growth |
| Attribution | Shows which marketing investments produce revenue |
| Governance | Prevents unsafe customer communication and privacy mistakes |


## Executable fixture set

Use the executable fixtures in `workflows/fixtures/oldfarmtrucks/` for dry-run regression checks of canonical planner outputs and governance policy references:

- `launch-readiness.yaml`
- `market-scans.yaml`
- `weekly-ops-reviews.json`
- `customer-lifecycle.yaml`
- `customer-360.json`

