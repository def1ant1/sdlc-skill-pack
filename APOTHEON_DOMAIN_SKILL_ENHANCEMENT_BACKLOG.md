# APOTHEON — DOMAIN SKILL ENHANCEMENT BACKLOG

**Status:** DOMAIN EXPANSION PLAN  
**Purpose:** Improve and extend skills for financial management, trading research, arbitrage analysis, tax strategy support, business entity management, legal/regulatory intelligence, economic analysis/reporting, logistics, learning and development, materials management/science, data security, HR management, sales assistance, and knowledge/research management.

---

## 0. Operating Guardrails

These skills must be designed as governed decision-support systems.

They must not autonomously:

- Place trades.
- Transfer money.
- Execute tax filings.
- Create/dissolve entities.
- Submit payroll or HR decisions.
- Send customer-facing communications without policy approval.
- Submit legal filings.
- Interpret law as final legal advice.
- Modify security policy, secrets, IAM, encryption, or access controls without approval.
- Provide legal, tax, investment, employment, engineering safety, or security advice as final professional advice.

Required language in high-risk domains:

```text
This output is decision support only. Review with a qualified professional before acting.
```

Required governance:

- Human approval for external actions.
- Evidence/source traceability.
- Assumption logs.
- Risk scoring.
- Confidence scoring.
- Compliance boundary checks.
- Audit trail events.
- Jurisdiction and effective-date tracking for legal/tax/regulatory outputs.
- Citation to authoritative sources where legal, tax, regulatory, economic, scientific, or security information is used.
- Clear separation of observed data, derived analysis, inference, and recommendation.

---

# 1. Financial Management Skill Pack

## Goal

Create CFO-grade operating support for cash, budgets, accounting workflows, margin, financial controls, and executive visibility.

## New or enhanced skills

```text
skills/financial-management/
skills/cash-management/
skills/cash-flow-forecasting/
skills/budget-planning/
skills/budget-variance-analysis/
skills/fpa-analysis/
skills/financial-scenario-modeling/
skills/revenue-leakage-detection/
skills/working-capital-optimization/
skills/unit-economics-analysis/
skills/month-end-close-support/
skills/reconciliation-automation/
skills/financial-control-monitoring/
skills/expense-policy-compliance/
```

## Capabilities

- Cash runway analysis
- 13-week cash forecast
- Monthly budget vs actuals
- Revenue, COGS, gross margin, operating margin analysis
- Unit economics by product/service/channel
- AR/AP aging analysis
- Expense anomaly detection
- Monthly close checklist
- Financial KPI dashboard
- Scenario modeling and sensitivity analysis

## Required inputs

```text
bank exports
accounting system data
invoices
payments
expenses
budgets
sales pipeline
inventory data
payroll data
vendor contracts
```

## Required outputs

```text
cash forecast
budget variance report
CFO summary
margin analysis
expense anomaly report
runway report
financial control exceptions
recommended actions with approval requirements
```

## Required governance

- Any payment, payroll, bank, accounting-book, or tax-facing action requires human approval.
- Outputs must include assumptions and data-source lineage.
- Any missing or stale financial data must be flagged.

## Acceptance criteria

- All skills have V9 manifests.
- All skills reference canonical finance entities.
- All skills include evals for calculation accuracy, source completeness, and governance compliance.
- Financial reports explicitly separate observed data, calculated data, assumptions, and recommendations.

---

# 2. Trading Research and Portfolio Intelligence Skill Pack

## Goal

Support research, risk analysis, watchlists, portfolio analytics, and strategy backtesting for stocks, crypto, currencies, ETFs, commodities, and other liquid markets.

## New skills

```text
skills/trading-research/
skills/market-data-ingestion/
skills/watchlist-management/
skills/portfolio-risk-analysis/
skills/technical-analysis-support/
skills/fundamental-analysis-support/
skills/crypto-market-analysis/
skills/fx-market-analysis/
skills/correlation-regime-analysis/
skills/position-sizing-analysis/
skills/trade-journal-analysis/
skills/backtesting-support/
skills/market-news-synthesis/
skills/risk-limit-monitoring/
```

## Capabilities

- Watchlist creation
- Market data ingestion and normalization
- Price/volume/volatility summaries
- Fundamental snapshot analysis
- Technical indicator calculation
- Portfolio exposure analysis
- Correlation and regime detection
- Risk/reward scenario analysis
- Backtest preparation and review
- Trade journal review
- Risk-limit monitoring
- News/event synthesis with citations when live data is available

## Prohibited autonomous behavior

- No autonomous trade execution.
- No personalized investment advice as final advice.
- No guaranteed return claims.
- No market manipulation, pump-and-dump, wash trading, insider-trading support, or evasion guidance.

## Required governance

- All trade ideas are labeled as research hypotheses.
- Any order placement integration must be disabled by default and require explicit HITL approval.
- Every output must include risk factors, assumptions, time horizon, and invalidation criteria.

## Required outputs

```text
research brief
risk summary
scenario table
watchlist update
portfolio exposure report
backtest assumptions
trade journal insights
```

## Acceptance criteria

- Skills work in offline/dry-run mode using fixture data.
- Skills can ingest CSV market data locally.
- Backtesting support produces assumptions and limitations, not performance guarantees.
- Trading-related skills reference governance docs for investment-risk boundaries.

---

# 3. Arbitrage and Market Inefficiency Analysis Skill Pack

## Goal

Identify and evaluate potential pricing inefficiencies across markets, geographies, products, platforms, or currencies while enforcing legality, fees, liquidity, timing, and execution-risk checks.

## New skills

```text
skills/arbitrage-analysis/
skills/cross-market-price-comparison/
skills/fee-slippage-modeling/
skills/liquidity-risk-analysis/
skills/execution-risk-analysis/
skills/local-market-arbitrage/
skills/crypto-arbitrage-monitoring/
skills/fx-arbitrage-analysis/
skills/retail-arbitrage-analysis/
skills/vehicle-market-arbitrage/
```

## Capabilities

- Compare prices across marketplaces
- Normalize fees, taxes, shipping, spreads, and slippage
- Rank opportunities by expected net margin
- Identify execution risks and timing risks
- Evaluate local scarcity and geographic price gaps
- Generate acquisition/sale watchlists

## Governance

- Do not bypass marketplace controls.
- Do not scrape or access sources in violation of terms/access controls.
- Do not support market manipulation or prohibited trading conduct.
- Require human review before purchases, listings, trades, or outreach.

## Acceptance criteria

- Every opportunity includes gross spread, estimated costs, net spread, liquidity score, timing risk, confidence score, and legal/policy checks.
- Works with OldFarmTrucks.com market scarcity workflow.
- Supports dry-run fixture data.

---

# 4. Tax Minimization Strategy Support Skill Pack

## Goal

Provide tax planning support, deduction tracking, entity tax considerations, retirement-plan contribution planning support, and estimated-tax workflow support while requiring qualified professional review.

## New skills

```text
skills/tax-strategy-support/
skills/deduction-opportunity-analysis/
skills/entity-tax-comparison-support/
skills/estimated-tax-planning/
skills/retirement-plan-contribution-support/
skills/depreciation-strategy-support/
skills/vehicle-business-use-documentation/
skills/state-tax-consideration-analysis/
skills/tax-document-checklist/
skills/tax-advisor-briefing-pack/
```

## Capabilities

- Identify potential deduction categories
- Prepare tax advisor briefing packs
- Estimate tax payment planning inputs
- Compare entity-tax considerations at a high level
- Track documentation needs
- Support retirement contribution strategy planning
- Support depreciation/Section 179 research workflows where applicable
- Flag professional review requirements

## Hard boundaries

- No final tax advice.
- No tax evasion or concealment guidance.
- No filing instructions that bypass professional review.
- No guarantee of tax outcomes.

## Required outputs

```text
tax planning checklist
advisor briefing pack
potential deduction inventory
estimated-tax input worksheet
entity comparison support memo
retirement contribution planning support memo
documentation gaps
professional review flags
```

## Acceptance criteria

- Every output contains professional-review notice.
- Skills reference legal/tax review policy.
- Outputs separate general rules, user-provided facts, assumptions, and questions for CPA/attorney.

---

# 5. Business Entity Management Skill Pack

## Goal

Manage the operational lifecycle of business entities, ownership structures, registered agents, annual reports, licenses, governance docs, bank accounts, and compliance calendars.

## New skills

```text
skills/business-entity-management/
skills/entity-formation-support/
skills/entity-compliance-calendar/
skills/registered-agent-management/
skills/ownership-structure-mapping/
skills/business-license-tracking/
skills/annual-report-preparation-support/
skills/board-consent-generation-support/
skills/entity-document-vault/
skills/intercompany-relationship-mapping/
```

## Capabilities

- Entity inventory
- Ownership/org chart mapping
- Annual report deadline tracking
- License/permit tracking
- Compliance calendar
- Registered agent and address tracking
- Document checklist management
- Board/member consent draft support
- Entity record audit

## Boundaries

- No legal advice as final advice.
- Formation/filing actions require human/legal review.
- Any secretary-of-state filing or bank action requires approval.

## Required outputs

```text
entity register
compliance calendar
ownership chart
document checklist
filing readiness report
legal-review question list
```

## Acceptance criteria

- Adds canonical entities for BusinessEntity, Owner, RegisteredAgent, Filing, License, EntityDocument, ComplianceDeadline.
- Supports schedule integration for annual reports and renewal deadlines.

---

# 6. Legal Operations and Regulatory Intelligence Skill Pack

## Goal

Support legal operations, legal research, regulatory monitoring, jurisdiction tracking, tax-rate monitoring, contract support, compliance calendars, and professional-review-ready legal/tax/regulatory briefs.

This skill pack is decision support only. It must not replace an attorney, CPA, enrolled agent, compliance officer, or other licensed professional.

## New skills

```text
skills/legal-operations/
skills/legal-research-support/
skills/regulatory-monitoring/
skills/jurisdiction-law-monitoring/
skills/local-law-research/
skills/county-law-research/
skills/state-law-research/
skills/federal-law-research/
skills/tax-rate-monitoring/
skills/sales-tax-rate-monitoring/
skills/property-tax-research/
skills/business-license-research/
skills/permit-requirements-research/
skills/employment-law-monitoring/
skills/consumer-protection-law-monitoring/
skills/vehicle-dealer-law-research/
skills/data-privacy-law-monitoring/
skills/contract-review-support/
skills/clause-risk-analysis/
skills/legal-obligation-tracking/
skills/legal-deadline-monitoring/
skills/legal-change-impact-analysis/
skills/legal-citation-validation/
skills/legal-advisor-briefing-pack/
```

## Capabilities

- Research local, county, state, and federal laws from authoritative sources.
- Monitor law/regulation changes by jurisdiction and topic.
- Search for current tax rates and effective dates.
- Track sales tax, property tax, payroll tax, franchise tax, excise tax, and business license fee references.
- Identify business licensing and permit requirements.
- Track vehicle dealer, title, disclosure, lemon-law, advertising, consumer-protection, and consignment requirements where relevant.
- Track employment law changes for HR workflows.
- Track data privacy and marketing consent rules.
- Extract obligations from contracts, leases, vendor agreements, customer terms, and policies.
- Build legal advisor briefing packs with sources, questions, risk flags, and deadlines.

## Source priority

Legal/regulatory/tax skills must prioritize authoritative sources:

```text
federal agency websites
state department of revenue websites
state secretary of state websites
state department of labor websites
county tax assessor/collector websites
city/county clerk websites
municipal code portals
court/government code repositories
official legislative websites
official administrative code websites
```

Secondary sources may be used only for discovery or context and must be labeled as non-authoritative.

## Required metadata for every legal/tax/regulatory finding

```yaml
finding:
  jurisdiction:
    country:
    state:
    county:
    city:
  authority_level: federal | state | county | municipal | agency | court | secondary
  topic:
  source_title:
  source_url:
  source_publisher:
  publication_date:
  effective_date:
  last_verified_at:
  retrieved_at:
  citation:
  excerpt:
  confidence:
  professional_review_required: true
  change_detected:
  supersedes:
  related_obligations:
```

## Required outputs

```text
legal research memo
jurisdiction requirements matrix
tax-rate table
business license checklist
permit requirement checklist
regulatory change alert
legal obligation register
contract risk summary
advisor briefing pack
professional-review question list
```

## Hard boundaries

- No final legal advice.
- No final tax advice.
- No instructions for evading taxes, licenses, permits, reporting obligations, or legal duties.
- No autonomous legal filings.
- No autonomous government submissions.
- No autonomous contract signature or acceptance.
- No definitive claim that a business is compliant without professional review.

## Acceptance criteria

- Every legal/regulatory/tax output includes jurisdiction, source URL, effective date if available, last-verified timestamp, and professional-review notice.
- Skills distinguish authoritative vs non-authoritative sources.
- Skills flag stale, missing, conflicting, or ambiguous law/tax-rate data.
- Skills produce a legal advisor or CPA briefing pack when uncertainty or action is required.
- Skills integrate with schedule system for periodic monitoring.
- Skills integrate with entity management, tax strategy, HR, sales/customer, and OldFarmTrucks vehicle-dealer workflows.

---

# 7. Economic Analysis and Reporting Skill Pack

## Goal

Create macroeconomic, regional, industry, labor-market, pricing, inflation, interest-rate, and business-cycle intelligence for strategic planning, forecasting, market entry, pricing, and risk management.

## New skills

```text
skills/economic-analysis/
skills/macro-economic-reporting/
skills/regional-economic-analysis/
skills/industry-economic-analysis/
skills/inflation-impact-analysis/
skills/interest-rate-impact-analysis/
skills/labor-market-analysis/
skills/consumer-demand-analysis/
skills/commodity-price-analysis/
skills/business-cycle-monitoring/
skills/economic-indicator-ingestion/
skills/economic-forecast-scenario-support/
skills/local-market-economic-reporting/
skills/economic-risk-dashboard/
```

## Capabilities

- Monitor macro and regional indicators.
- Track inflation, rates, labor, consumer spending, housing, commodities, and credit conditions.
- Analyze impact on pricing, demand, inventory, payroll, financing, and cash flow.
- Produce executive economic outlook reports.
- Support scenario planning and sensitivity analysis.
- Connect economic indicators to company KPIs.

## Source priority

Prefer authoritative and primary data sources, such as:

```text
BLS
BEA
Federal Reserve / FRED
Census Bureau
Treasury
state labor departments
state economic development agencies
county/city economic dashboards
industry associations
commodity exchanges where permitted
```

## Required outputs

```text
economic outlook report
regional market brief
industry trend report
inflation impact memo
interest-rate impact memo
labor-market report
scenario assumptions table
executive risk dashboard
```

## Governance

- Forecasts must be labeled as forecasts, not facts.
- Every economic report must separate observed indicators, assumptions, model outputs, and recommendations.
- Use source timestamps and revision dates where available.

## Acceptance criteria

- Skills include source timestamps and indicator definitions.
- Skills flag stale or revised data.
- Outputs include confidence and scenario ranges.
- Economic assumptions can feed finance, pricing, inventory, trading research, and strategy workflows.

---

# 8. Logistics and Transportation Skill Pack

## Goal

Support transportation planning, freight/route optimization, carrier/vendor selection, delivery scheduling, warehouse movement, fleet operations, shipping cost analysis, and logistics risk management.

## New skills

```text
skills/logistics-management/
skills/route-optimization-support/
skills/freight-cost-analysis/
skills/carrier-selection-support/
skills/shipping-rate-comparison/
skills/delivery-schedule-planning/
skills/warehouse-flow-optimization/
skills/fleet-maintenance-planning/
skills/transport-risk-analysis/
skills/reverse-logistics-management/
skills/last-mile-delivery-analysis/
skills/logistics-exception-management/
skills/vehicle-transport-coordination/
skills/bill-of-lading-review-support/
```

## Capabilities

- Compare carriers, routes, and shipping options.
- Estimate freight, transport, fuel, handling, storage, and delay costs.
- Plan pickup/delivery windows.
- Track exceptions and delays.
- Support inbound/outbound logistics.
- Coordinate vehicle transport for dealership workflows.
- Analyze logistics impact on margin and customer experience.

## Required outputs

```text
route plan
carrier comparison
shipping cost estimate
transport risk report
delivery schedule
logistics exception report
vehicle transport checklist
freight margin impact report
```

## Governance

- No autonomous carrier booking, shipment release, payment, or legal transport document signature without approval.
- Regulated transport, hazardous materials, title/vehicle movement, and interstate commerce issues require professional review where applicable.

## Acceptance criteria

- Skills support dry-run fixture data.
- Outputs include assumptions, costs, timing, risk, and approval requirements.
- Integrates with inventory, procurement, customer onboarding, vendor management, and OldFarmTrucks vehicle transport workflows.

---

# 9. Learning and Development Skill Pack

## Goal

Support employee training, role-based learning paths, skills gap analysis, onboarding curricula, knowledge retention, certification tracking, coaching, and adaptive learning workflows.

## New skills

```text
skills/learning-development/
skills/skills-gap-analysis/
skills/role-based-learning-paths/
skills/onboarding-curriculum-design/
skills/training-content-generation/
skills/learning-assessment-design/
skills/certification-tracking/
skills/coaching-plan-generation/
skills/knowledge-retention-analysis/
skills/adaptive-learning-recommendations/
skills/team-capability-mapping/
skills/learning-roi-analysis/
```

## Capabilities

- Map roles to required skills.
- Identify individual/team skill gaps.
- Create onboarding and training plans.
- Generate learning objectives, assessments, and practice tasks.
- Track certifications and policy acknowledgements.
- Recommend learning content based on role, goals, and performance evidence.
- Measure learning effectiveness and business impact.

## Required outputs

```text
skills matrix
learning path
onboarding curriculum
training module outline
assessment rubric
certification tracker
coaching plan
learning ROI report
```

## Governance

- Learning recommendations must not be used as final HR performance decisions.
- Sensitive/protected attributes must not drive learning-path recommendations.
- Performance-related insights require human review before employment impact.

## Acceptance criteria

- Integrates with HR management, knowledge management, meeting intelligence, and employee record workflows.
- Skills include bias/fairness safeguards.
- Outputs include evidence, objectives, timeline, and review cadence.

---

# 10. Materials Management and Materials Science Skill Pack

## Goal

Support materials inventory, procurement, substitution analysis, supplier/material risk, quality documentation, material compatibility, failure analysis support, and materials-science research for product, manufacturing, construction, repair, and restoration workflows.

## New skills

```text
skills/materials-management/
skills/materials-inventory-control/
skills/bill-of-materials-management/
skills/material-requirements-planning/
skills/material-substitution-analysis/
skills/material-cost-analysis/
skills/supplier-material-risk-analysis/
skills/material-quality-documentation/
skills/material-traceability/
skills/material-compatibility-research/
skills/material-failure-analysis-support/
skills/corrosion-risk-analysis/
skills/coatings-and-finishes-research/
skills/metals-and-alloys-research/
skills/restoration-materials-planning/
```

## Capabilities

- Manage material inventories and BOMs.
- Forecast material requirements.
- Compare substitute materials by cost, availability, performance, and risk.
- Track material certificates, lots, batches, and traceability.
- Support corrosion, coatings, metals/alloys, and restoration-material research.
- Analyze material choice impact on cost, durability, safety, and compliance.

## Required outputs

```text
bill of materials
material inventory report
substitution analysis
supplier/material risk report
traceability record
quality documentation checklist
material compatibility memo
failure analysis support memo
restoration materials plan
```

## Governance

- Materials outputs involving safety-critical, structural, hazardous, regulated, or engineering-certified applications require qualified professional review.
- No final engineering safety certification.
- Hazardous materials handling must reference applicable safety and regulatory requirements.

## Acceptance criteria

- Integrates with inventory, procurement, logistics, product operations, and OldFarmTrucks restoration workflows.
- Outputs include assumptions, source references, material properties, constraints, and review flags.
- Supports citation-backed research for materials science claims.

---

# 11. Data Security and Information Protection Skill Pack

## Goal

Strengthen data security, privacy, access control, secrets management, data classification, retention, DLP, incident response, vendor security review, and secure workflow governance.

## New skills

```text
skills/data-security-management/
skills/data-classification/
skills/data-loss-prevention-analysis/
skills/secrets-management-review/
skills/access-control-review/
skills/iam-policy-analysis/
skills/security-configuration-review/
skills/encryption-policy-management/
skills/data-retention-policy-enforcement/
skills/privacy-impact-assessment/
skills/vendor-security-review/
skills/security-incident-triage/
skills/backup-and-recovery-security/
skills/audit-log-review/
skills/secure-data-sharing-review/
skills/ai-data-security-review/
```

## Capabilities

- Classify data by sensitivity, privacy, and business criticality.
- Review access policies, IAM, secrets, encryption, and retention.
- Identify risky data flows and external sharing.
- Review vendor/security questionnaires.
- Support incident triage and evidence collection.
- Evaluate AI workflow data exposure risks.
- Enforce least privilege and approval gates.

## Required outputs

```text
data classification report
access review report
secrets exposure risk report
data flow risk map
privacy impact assessment
vendor security review
incident triage report
secure sharing recommendation
audit evidence pack
```

## Governance

- No autonomous permission changes, secret rotation, data deletion, encryption changes, or security configuration changes without approval.
- Security incident outputs must preserve evidence and avoid destructive actions unless approved.
- Sensitive findings must be access-controlled.

## Acceptance criteria

- Integrates with privacy runtime, zero-trust runtime, local security, governance, audit ledger, connector hub, and knowledge management.
- Skills produce actionable but approval-gated remediation recommendations.
- Dry-run tests verify no security mutations occur.

---

# 12. HR Management Skill Pack

## Goal

Support recruiting, onboarding, employee records, performance coaching, learning plans, policy compliance, workforce planning, and HR operations with high-impact decision safeguards.

## New skills

```text
skills/hr-management/
skills/workforce-planning/
skills/hiring-pipeline-intelligence/
skills/job-description-generation/
skills/interview-scorecard-analysis/
skills/onboarding-workflow-management/
skills/employee-record-management/
skills/performance-coaching-support/
skills/learning-path-optimization/
skills/compensation-benchmarking-support/
skills/employee-policy-compliance/
skills/burnout-risk-detection/
skills/offboarding-checklist-management/
```

## Capabilities

- Hiring workflow support
- Interview scorecards
- Onboarding plans
- Training plans
- Employee record checklists
- Performance coaching support
- Workforce planning
- Policy acknowledgement tracking
- Offboarding checklist support

## High-impact decision rules

The system must not autonomously make or recommend final decisions for:

- hiring
- firing
- promotion
- demotion
- compensation
- disciplinary action
- protected-class-sensitive decisions

These require human review and bias checks.

## Acceptance criteria

- Skills reference HR high-impact decision policy.
- Outputs include structured evidence and human-review flag.
- Sensitive attributes must not be used for scoring.
- Bias and fairness checks required for hiring/performance workflows.

---

# 13. Sales Assistant and Revenue Enablement Skill Pack

## Goal

Improve lead management, pipeline support, discovery prep, call notes, proposals, follow-up, account planning, objection handling, and sales coaching.

## New skills

```text
skills/sales-assistant/
skills/discovery-call-prep/
skills/sales-call-summary/
skills/follow-up-draft-generation/
skills/proposal-support/
skills/account-planning/
skills/opportunity-risk-analysis/
skills/objection-handling-support/
skills/negotiation-prep/
skills/pipeline-hygiene/
skills/sales-coaching-feedback/
skills/customer-research-briefing/
```

## Capabilities

- Account research briefs
- Discovery question generation
- Call summary and action items
- Follow-up drafts
- Proposal outlines
- Objection handling playbooks
- Deal risk scoring
- Pipeline hygiene recommendations
- Next-best-action suggestions

## Governance

- Customer-facing messages require approval unless explicit policy permits automation.
- Pricing/discount commitments require approval.
- Legal/contractual claims require review.

## Acceptance criteria

- Integrates with CRM entities.
- Supports OldFarmTrucks.com lead/opportunity workflows.
- Emits action items and CRM update recommendations separately from actual CRM mutations.

---

# 14. Knowledge Management and Research Skill Pack

## Goal

Create a robust organizational knowledge and research system that supports document ingestion, source evaluation, literature review, competitive intelligence, decision memory, evidence packs, and retrieval quality.

## New skills

```text
skills/knowledge-management/
skills/research-management/
skills/source-quality-evaluation/
skills/evidence-pack-generation/
skills/document-ingestion/
skills/knowledge-graph-curation/
skills/decision-memory-management/
skills/research-brief-generation/
skills/competitive-intelligence-research/
skills/literature-review/
skills/citation-integrity-checking/
skills/research-gap-analysis/
skills/institutional-knowledge-query/
```

## Capabilities

- Ingest docs into knowledge base
- Evaluate source quality
- Create evidence packs
- Generate research briefs
- Maintain decision records
- Identify research gaps
- Summarize competitive intelligence
- Track claims to citations
- Improve retrieval quality

## Required outputs

```text
research brief
evidence pack
source table
citation map
knowledge graph update proposal
decision record
research gap report
```

## Acceptance criteria

- Every claim in research outputs must be traceable to a source or clearly labeled as inference.
- Supports local document folders.
- Integrates with memory/context manager.
- Includes citation integrity evaluation.

---

# 15. Canonical Entity Expansion

Add or verify schemas for:

```text
Portfolio
Asset
Position
TradeIdea
MarketDataPoint
Watchlist
RiskLimit
ArbitrageOpportunity
TaxStrategy
TaxDocument
Deduction
BusinessEntity
Owner
RegisteredAgent
Filing
License
ComplianceDeadline
LegalMatter
LegalSource
LegalFinding
Jurisdiction
LawMonitor
RegulatoryChange
TaxRate
PermitRequirement
BusinessLicense
Contract
Clause
LegalObligation
LegalDeadline
EconomicIndicator
EconomicReport
ForecastScenario
RegionalMarket
IndustryTrend
CommodityPrice
LogisticsRoute
Carrier
Shipment
FreightQuote
WarehouseLocation
DeliverySchedule
FleetAsset
LearningPath
TrainingModule
Assessment
Certification
SkillProfile
CapabilityMatrix
Material
BillOfMaterials
MaterialLot
MaterialCertificate
MaterialProperty
MaterialSubstitution
SupplierMaterial
DataAsset
DataClassification
DataFlow
AccessPolicy
Secret
SecurityFinding
SecurityIncident
PrivacyImpactAssessment
Employee
Candidate
JobRole
InterviewScorecard
PerformanceReview
LearningPlan
SalesActivity
SalesConversation
Proposal
ResearchSource
EvidencePack
DecisionRecord
KnowledgeArtifact
```

---

# 16. Event Model Expansion

Add or verify events:

```text
finance.cash_forecast_updated
finance.budget_variance_detected
finance.control_exception_detected
portfolio.risk_limit_breached
trade.idea_created
trade.journal_entry_added
arbitrage.opportunity_detected
tax.strategy_review_requested
tax.document_missing
tax.rate_changed
tax.rate_verified
entity.compliance_deadline_due
entity.filing_completed
legal.source_verified
legal.finding_created
legal.regulatory_change_detected
legal.obligation_created
legal.deadline_due
legal.professional_review_requested
permit.requirement_detected
license.renewal_due
economic.indicator_updated
economic.report_generated
economic.scenario_updated
economic.risk_alert_created
logistics.shipment_planned
logistics.carrier_selected_for_review
logistics.exception_detected
logistics.delivery_schedule_updated
logistics.transport_risk_flagged
learning.skill_gap_detected
learning.path_assigned_for_review
learning.assessment_completed
learning.certification_due
materials.bom_updated
materials.shortage_detected
materials.substitution_recommended
materials.quality_document_received
materials.traceability_gap_detected
security.data_classified
security.access_review_required
security.secret_risk_detected
security.incident_triaged
security.privacy_impact_assessment_created
hr.candidate_scored
hr.onboarding_started
hr.policy_acknowledgement_missing
sales.follow_up_drafted
sales.opportunity_risk_changed
knowledge.source_ingested
knowledge.evidence_pack_created
knowledge.decision_recorded
```

---

# 17. Required Governance Documents

Create or update:

```text
docs/governance/investment-research-boundaries.md
docs/governance/trading-risk-policy.md
docs/governance/tax-strategy-boundaries.md
docs/governance/entity-management-legal-boundaries.md
docs/governance/legal-research-boundaries.md
docs/governance/regulatory-monitoring-policy.md
docs/governance/tax-rate-source-policy.md
docs/governance/government-source-verification-policy.md
docs/governance/economic-forecasting-boundaries.md
docs/governance/logistics-external-action-policy.md
docs/governance/learning-development-fairness-policy.md
docs/governance/materials-science-review-boundaries.md
docs/governance/data-security-action-policy.md
docs/governance/incident-response-boundaries.md
docs/governance/hr-high-impact-decision-policy.md
docs/governance/customer-communication-policy.md
docs/governance/research-citation-integrity-policy.md
```

---

# 18. Planner and Schedule Integration

## Planner updates

Update or create planners so these domains can be routed:

```text
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_trading_research_workflow.py
scripts/orchestration/plan_tax_workflow.py
scripts/orchestration/plan_entity_management_workflow.py
scripts/orchestration/plan_legal_workflow.py
scripts/orchestration/plan_regulatory_monitoring_workflow.py
scripts/orchestration/plan_economic_analysis_workflow.py
scripts/orchestration/plan_logistics_workflow.py
scripts/orchestration/plan_learning_development_workflow.py
scripts/orchestration/plan_materials_workflow.py
scripts/orchestration/plan_data_security_workflow.py
scripts/orchestration/plan_hr_workflow.py
scripts/orchestration/plan_sales_workflow.py
scripts/orchestration/plan_research_workflow.py
```

## Schedule examples

Create schedules:

```text
schedules/examples/weekly-cash-forecast.yaml
schedules/examples/monthly-budget-variance-review.yaml
schedules/examples/daily-market-watchlist-review.yaml
schedules/examples/weekly-trade-journal-review.yaml
schedules/examples/monthly-tax-document-check.yaml
schedules/examples/monthly-tax-rate-verification.yaml
schedules/examples/monthly-entity-compliance-review.yaml
schedules/examples/monthly-business-license-review.yaml
schedules/examples/weekly-regulatory-change-monitor.yaml
schedules/examples/monthly-local-law-monitor.yaml
schedules/examples/quarterly-federal-law-review.yaml
schedules/examples/weekly-economic-outlook-report.yaml
schedules/examples/monthly-regional-economic-review.yaml
schedules/examples/weekly-logistics-exception-review.yaml
schedules/examples/monthly-carrier-performance-review.yaml
schedules/examples/monthly-learning-skills-gap-review.yaml
schedules/examples/quarterly-certification-review.yaml
schedules/examples/weekly-materials-shortage-review.yaml
schedules/examples/monthly-material-quality-review.yaml
schedules/examples/weekly-data-security-access-review.yaml
schedules/examples/daily-security-incident-triage-review.yaml
schedules/examples/weekly-hr-onboarding-review.yaml
schedules/examples/daily-sales-follow-up-review.yaml
schedules/examples/weekly-knowledge-curation-review.yaml
```

---

# 19. Example Workflows

Add docs/examples for:

```text
docs/examples/financial-management-workflows.md
docs/examples/trading-research-workflows.md
docs/examples/arbitrage-analysis-workflows.md
docs/examples/tax-strategy-support-workflows.md
docs/examples/business-entity-management-workflows.md
docs/examples/legal-regulatory-intelligence-workflows.md
docs/examples/local-state-federal-law-monitoring-workflows.md
docs/examples/tax-rate-monitoring-workflows.md
docs/examples/economic-analysis-reporting-workflows.md
docs/examples/logistics-management-workflows.md
docs/examples/learning-development-workflows.md
docs/examples/materials-management-science-workflows.md
docs/examples/data-security-workflows.md
docs/examples/hr-management-workflows.md
docs/examples/sales-assistant-workflows.md
docs/examples/knowledge-research-management-workflows.md
```

---

# 20. Test and Evaluation Requirements

Create tests:

```text
tests/domain/test_financial_management_skills.py
tests/domain/test_trading_research_skills.py
tests/domain/test_arbitrage_analysis_skills.py
tests/domain/test_tax_strategy_skills.py
tests/domain/test_entity_management_skills.py
tests/domain/test_legal_regulatory_skills.py
tests/domain/test_tax_rate_monitoring_skills.py
tests/domain/test_economic_analysis_skills.py
tests/domain/test_logistics_skills.py
tests/domain/test_learning_development_skills.py
tests/domain/test_materials_management_skills.py
tests/domain/test_data_security_skills.py
tests/domain/test_hr_management_skills.py
tests/domain/test_sales_assistant_skills.py
tests/domain/test_knowledge_research_skills.py
tests/orchestration/test_domain_planner_expansion.py
tests/governance/test_high_risk_domain_boundaries.py
tests/governance/test_legal_tax_professional_boundaries.py
tests/governance/test_data_security_action_boundaries.py
tests/governance/test_materials_science_review_boundaries.py
```

Required eval dimensions:

- calculation accuracy
- source traceability
- hallucination risk
- governance compliance
- professional-boundary language
- approval routing
- dry-run safety
- schema validity
- jurisdiction correctness
- effective-date handling
- authoritative-source preference
- stale-source detection
- conflicting-source detection
- forecast assumption quality
- logistics cost/timing accuracy
- learning recommendation fairness
- material property citation quality
- security action safety
- privacy and data classification correctness

---

# 21. Recommended Implementation Order

1. Governance boundary docs for trading, tax, legal/regulatory, economics, logistics, L&D, materials science, data security, HR, entity management, research.
2. Canonical entity and event schemas.
3. Data security skills and governance validators.
4. Legal/regulatory/tax-rate monitoring skills.
5. Economic analysis/reporting skills.
6. Financial management skills.
7. Logistics skills.
8. Materials management/science skills.
9. Knowledge/research skills.
10. Learning and development skills.
11. Sales assistant skills.
12. Entity management skills.
13. HR management skills.
14. Tax strategy support skills.
15. Trading research skills.
16. Arbitrage analysis skills.
17. Planner integrations.
18. Schedule examples.
19. Domain examples.
20. Tests and evals.

---

# 22. Release Acceptance Criteria

This enhancement is complete when:

- All new skills pass V9 skill contract validation.
- All high-risk domains reference governance boundary docs.
- Trading/tax/legal/HR/security/materials skills are decision-support only where professional review is required.
- Legal and tax-rate outputs include jurisdiction, source, effective date where available, and last-verified timestamp.
- Economic reports include source timestamps, assumptions, and scenario ranges.
- Logistics outputs include cost, timing, risk, and approval requirements.
- Learning/development outputs include fairness safeguards and human-review boundaries.
- Materials science outputs include source-backed material properties and professional-review flags for safety-critical use.
- Data security outputs never perform access, secret, encryption, deletion, or configuration changes without approval.
- Authoritative government/primary sources are preferred and secondary sources are labeled.
- No autonomous trades, filings, payments, entity actions, HR decisions, legal submissions, government filings, security mutations, logistics bookings, or customer messages occur.
- Domain planners can route representative workflows.
- Example schedules validate.
- Dry-run tests prove no external side effects.
- Example workflow docs exist for each domain.
