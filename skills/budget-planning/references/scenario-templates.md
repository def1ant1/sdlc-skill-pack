# Scenario Templates

## Three-Scenario Framework

Every budget plan and reforecast includes three scenarios:

| Scenario | Percentile | Description |
|---|---|---|
| Base (most likely) | 50th | Current trajectory + known catalysts; planning commitment |
| Upside | 80th | Strong execution + favorable market; target to exceed |
| Downside | 20th | Headwinds materialize; minimum viable plan |

The base case is the operating commitment. The downside defines the contingency trigger point.

---

## Scenario Modeling Template

```
SCENARIO MODEL — [Period]
=========================
Prepared: YYYY-MM-DD
Model version: x.y

ASSUMPTIONS SUMMARY
-------------------
                    BASE        UPSIDE      DOWNSIDE
Revenue growth      +25%        +40%        +10%
Churn rate          8%          5%          15%
New customer adds   N           N×1.3       N×0.7
Headcount           N FTE       N+5 FTE     N-3 FTE
AI compute cost     $X/mo       $X×1.2/mo   $X×0.8/mo

FINANCIAL PROJECTIONS
---------------------
                    BASE        UPSIDE      DOWNSIDE
MRR (end of period) $X          $X          $X
ARR                 $X          $X          $X
Gross margin        X%          X%          X%
Total opex          $X          $X          $X
EBITDA              ($X)        $X          ($X)
Burn rate           $X/mo       $X/mo       $X/mo
Runway              X months    X months    X months

KEY DECISION POINTS
-------------------
1. At $X MRR: unlock headcount tranche 2 (base and upside only)
2. At X months runway: reduce discretionary spend by 20% (downside trigger)
3. At X% churn: initiate customer success emergency plan
```

---

## Sensitivity Analysis

Identify the 3–5 variables that most affect the outcome:

| Variable | Base Value | -20% | +20% | P&L Impact |
|---|---|---|---|---|
| New ARR per month | $X | -$Y to EBITDA | +$Y to EBITDA | High |
| Churn rate | X% | +$Y to ARR | -$Y to ARR | High |
| Engineering headcount | N FTE | -$Y opex | +$Y opex | Medium |
| AI compute cost | $X/mo | -$Y COGS | +$Y COGS | Low-Medium |
| Marketing spend | $X/mo | -$Y ARR | +$Y ARR | Low |

---

## Downside Trigger Playbook

When actuals track downside scenario for 2 consecutive months:

| Runway Remaining | Action |
|---|---|
| > 18 months | Monitor; accelerate pipeline |
| 12–18 months | Reduce discretionary (travel, tools, contractors) |
| 9–12 months | Hiring freeze (non-revenue-generating roles) |
| 6–9 months | Bridge fundraise initiated; deeper cuts evaluated |
| < 6 months | Emergency plan: Level-3 approval for all spend > $1K |

---

## Upside Investment Gates

When actuals track upside for 2 consecutive months, unlock:

| MRR Milestone | Investment Unlocked |
|---|---|
| $X | Headcount tranche 2 (per headcount plan) |
| $Y | Additional marketing budget ($X/mo) |
| $Z | Infrastructure scaling investment |
| $W | New product/feature initiative budget |

Upside gates require CFO sign-off before investment is released.