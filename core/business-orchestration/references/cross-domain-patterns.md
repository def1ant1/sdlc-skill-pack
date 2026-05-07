# Cross-Domain Workflow Patterns

## Pattern 1 — New Vendor Onboarding

**Trigger**: Spend request for a vendor not in the registry.

**Domains**: Procurement → Legal → Finance → IT

```
Step 1: vendor-procurement    Qualify vendor (business, security, compliance checks)
Step 2: legal-ops             Review/execute DPA if vendor processes company data
Step 3: legal-ops             Review/execute contract or order form
Step 4: hitl-dashboard        Level-2 approval for spend
Step 5: accounting-automation Create vendor record; issue PO
Step 6: local-security        Provision any required system access
Step 7: vendor-procurement    Add to approved vendor registry
```

**Approval gate**: Level-2 at step 4; Level-3 for spend > $25K.

---

## Pattern 2 — New Hire

**Trigger**: Offer letter signed.

**Domains**: HR → Legal → IT → Finance

```
Step 1: workforce-management  Generate onboarding plan; confirm start date
Step 2: legal-ops             Verify employment docs (I-9 equivalent, contracts)
Step 3: local-security        Provision accounts (email, SSO, GitHub, Slack)
Step 4: accounting-automation Add to payroll
Step 5: workflow-engine       Schedule 30/60/90 check-in tasks
Step 6: meeting-intelligence  Schedule first-week 1:1s with manager and buddy
```

**Approval gate**: Level-3 approval for headcount was obtained at requisition stage.

---

## Pattern 3 — Enterprise Customer Deal Close

**Trigger**: Sales opportunity moves to "Closed-Won".

**Domains**: Legal → Finance → Customer Success → Engineering

```
Step 1: legal-ops             Review/execute enterprise agreement and DPA
Step 2: accounting-automation Record new ARR; update billing
Step 3: revenue-operations    Update CRM; log closed-won
Step 4: customer-success      Create account; assign CSM; begin onboarding
Step 5: workflow-engine       Trigger customer onboarding workflow
Step 6: engineering (if req)  Provision customer tenant (tenant-management)
Step 7: meeting-intelligence  Schedule kickoff meeting; capture agenda
```

**Approval gate**: Level-2 for standard enterprise; Level-3 for custom terms or > $100K ACV.

---

## Pattern 4 — Annual Budget Cycle

**Trigger**: September 1 (scheduled).

**Domains**: Finance → Strategy → HR → All Departments

```
Step 1: strategic-planning    Produce strategic priorities and growth targets
Step 2: budget-planning       Distribute top-down targets to department heads
Step 3: workforce-management  Collect headcount plans from each department
Step 4: budget-planning       Collect bottom-up expense submissions
Step 5: budget-planning       Consolidate; resolve conflicts; build scenarios
Step 6: hitl-dashboard        CFO review and approval of consolidated budget
Step 7: executive-reporting   Prepare board budget presentation
Step 8: hitl-dashboard        Board approval
Step 9: budget-planning       Activate approved budget in financial systems
```

**Approval gate**: CFO (Level-3) at step 6; Board at step 8.

---

## Pattern 5 — P0 Incident with Financial Impact

**Trigger**: P0 incident declared with estimated revenue impact > $10K.

**Domains**: SRE → Finance → Legal → Executive

```
Step 1: sre-incident-response Declare P0; assign IC; begin response
Step 2: business-orchestration Parallel: notify finance + legal + exec
Step 3: accounting-automation  Track revenue impact in real-time
Step 4: legal-ops              Assess customer notification obligations
Step 5: sre-incident-response  Resolve incident
Step 6: executive-reporting    Produce impact report for exec/board
Step 7: sre-incident-response  Author post-mortem
Step 8: legal-ops              Send customer notifications (if required)
Step 9: accounting-automation  Record financial impact; update projections
```

---

## Composition Rules

When composing a cross-domain workflow:

1. **Each step is a single skill invocation** — never combine two domain skills in one step
2. **Data contracts are explicit** — each step's inputs must be named outputs from a prior step
3. **Approval gates are domain-specific** — the approval level is the maximum required across all domains in the workflow
4. **Rollback must be defined** for any step that writes to external systems
5. **Audit trail is always last** — the final step in any cross-domain workflow writes to telemetry