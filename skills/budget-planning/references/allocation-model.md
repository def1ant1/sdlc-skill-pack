# Budget Allocation Model

## Top-Down Allocation Framework

Budget flows from top-level targets → department envelopes → line items.

```
CEO/Board approved targets
        │
        ▼
Revenue target → Gross Margin → Operating Expense envelope
        │
        ▼
Department allocations (% of total opex)
        │
        ▼
Line-item breakdown within each department
```

---

## Department Allocation Benchmarks

Benchmarks are expressed as % of total operating expense. Adjust based on company stage.

| Department | Seed | Series A | Series B | Growth |
|---|---|---|---|---|
| Engineering | 45–55% | 40–50% | 35–45% | 30–40% |
| Sales & Marketing | 20–30% | 25–35% | 30–40% | 35–45% |
| G&A | 15–25% | 12–20% | 8–15% | 6–10% |
| Product | 5–10% | 5–10% | 5–10% | 5–10% |
| Customer Success | 5–10% | 5–10% | 8–12% | 10–15% |

---

## Headcount Cost Model

### Cost Per FTE by Band

| Band | Role Type | Annual Fully-Loaded Cost (USD) |
|---|---|---|
| Band 1–2 | IC (Junior) | $120K–$160K |
| Band 3–4 | IC (Mid) | $160K–$220K |
| Band 5–6 | IC (Senior) | $220K–$300K |
| Band 7 | Staff / Principal | $300K–$400K |
| Band 8 | Director / VP | $350K–$500K+ |

Fully-loaded = base salary + benefits (30% of base) + equity cost (20% of base for tech roles) + payroll taxes.

Contractor cost: 1.3–1.5× equivalent IC rate, no benefits multiplier.

---

## AI Compute Budget Methodology

AI compute costs are allocated across COGS and OpEx:

| Category | Allocation | GL Code |
|---|---|---|
| Customer-serving LLM calls | COGS | 5110 |
| Internal AI workflows (non-customer) | Engineering OpEx | 6200 |
| LoRA training runs | Research / ML budget | 6200 |
| DGX Spark amortization | Shared (allocated by usage) | 5120 |

**Monthly AI budget formula**:

```
AI_budget = (expected_customer_requests × avg_cost_per_request)
           + (internal_workflow_volume × avg_internal_cost)
           + (training_runs_per_month × avg_training_cost)
           + (dgx_amortization_monthly)

Where dgx_amortization = hardware_cost / 36 months
```

Alert when actual > 115% of budgeted AI compute; escalate > 130%.

---

## Infrastructure Budget Model

Cloud infrastructure budget:

| Component | % of Infra Budget | Scaling Driver |
|---|---|---|
| Compute (app servers) | 40–50% | Active users × sessions/user |
| Database | 20–30% | Data volume + query volume |
| Storage | 10–15% | Data volume growth rate |
| CDN & Network | 5–10% | Traffic volume |
| Monitoring & Security | 5–10% | Flat + per-service |

---

## Contingency Reserve

All department budgets include a contingency reserve:

| Department Size | Reserve |
|---|---|
| < $500K annual | 10% |
| $500K–$2M annual | 8% |
| > $2M annual | 5% |

Contingency requires Level-3 approval to access. Unused contingency returns to central pool at period end.