# Scoring Engine

Used by `core/strategic-planning/SKILL.md` to provide scoring rubrics per dimension,
calibration examples, tech debt scoring adjustments, and weight configuration guidance.

---

## Dimension Rubrics

### Revenue Impact (0–10)

Score the direct or near-direct revenue effect of the item.

| Score | Criteria |
|---|---|
| 9–10 | Expected to add > $100K ARR or reduce churn by > 5% in 6 months |
| 7–8 | Expected to add $25K–$100K ARR or enable a specific enterprise deal |
| 5–6 | Expected to increase conversion or expansion — hard to quantify precisely |
| 3–4 | Indirect revenue effect (improves NPS or adoption of a revenue feature) |
| 1–2 | No measurable revenue effect; compliance or hygiene only |
| 0 | Net negative (cost increase, no revenue benefit) |

### Customer Impact (0–10)

Score the breadth and depth of customer benefit.

| Score | Criteria |
|---|---|
| 9–10 | Affects ≥ 50% of active users; critical pain point (blocks workflows) |
| 7–8 | Affects ≥ 20% of active users; significant friction removed |
| 5–6 | Affects a defined segment (10–20% of users); moderate value |
| 3–4 | Affects power users or a small segment; nice-to-have |
| 1–2 | Edge case; requested by < 3 customers |
| 0 | Internal only; no external customer impact |

### Implementation Effort (0–10)

Score the raw effort required. Higher score = more effort. **Inverted in formula.**

| Score | Criteria |
|---|---|
| 9–10 | > 8 weeks of engineering effort; multiple teams required |
| 7–8 | 4–8 weeks; one team, complex integration |
| 5–6 | 2–4 weeks; medium complexity |
| 3–4 | 1–2 weeks; low complexity, clear implementation path |
| 1–2 | < 1 week; configuration change or minor code edit |
| 0 | Trivial; < 1 day; no design required |

### Technical Risk (0–10)

Score the probability and severity of implementation going wrong. **Inverted in formula.**

| Score | Criteria |
|---|---|
| 9–10 | Novel technology; no prior art; high chance of scope change |
| 7–8 | Known approach but significant unknowns; likely to require R&D spike |
| 5–6 | Some uncertainty; well-understood problem space but new to team |
| 3–4 | Low risk; similar work done before; clear rollback path |
| 1–2 | Very low risk; config change or well-tested pattern |
| 0 | Zero risk; read-only or non-production change |

### Strategic Alignment (0–10)

Score against the 5 strategic pillars (see SKILL.md). Average score across applicable pillars.

| Score | Criteria |
|---|---|
| 9–10 | Core to ≥ 2 pillars; flagship capability |
| 7–8 | Strongly aligned to 1 pillar |
| 5–6 | Partially aligned; tangentially related to strategy |
| 3–4 | Neutral; does not advance or detract from strategy |
| 1–2 | Minor distraction from core strategy |
| 0 | Actively contradicts strategic direction |

---

## Calibration Examples

| Item | Rev | Cust | Effort | Risk | Align | Score |
|---|---|---|---|---|---|---|
| Workflow retry on failure | 8 | 9 | 3 | 2 | 9 | **80.5** |
| SSO/SAML for enterprise | 9 | 6 | 6 | 4 | 8 | **71.5** |
| Dark mode UI | 2 | 5 | 2 | 1 | 2 | **53.5** |
| Refactor auth middleware | 1 | 2 | 5 | 8 | 3 | **31.0** |
| Support for 17 more languages | 3 | 4 | 9 | 3 | 4 | **40.5** |

Formula applied:
```
score = (rev×0.30 + cust×0.25 + (10-effort)×0.20 + (10-risk)×0.15 + align×0.10) × 10
```

---

## Technical Debt Scoring

For tech debt items, use a modified formula with doubled risk weight:

```
debt_score = (
  (10 - effort_score)     × 0.25 +   # effort to fix (inverted)
  (10 - risk_score)       × 0.30 +   # risk of not fixing (inverted — high risk = high priority)
  revenue_impact          × 0.25 +   # does fixing it unblock revenue features?
  strategic_alignment     × 0.20
) × 10
```

**Debt severity labels:**

| Debt Score | Label | Action |
|---|---|---|
| 80–100 | Critical Debt | Fix before any new feature work in affected area |
| 60–79 | High Debt | Schedule in current or next sprint |
| 40–59 | Medium Debt | Schedule within 2 quarters |
| 20–39 | Low Debt | Backlog; fix opportunistically |
| 0–19 | Negligible | Accept; document as known debt |

---

## Weight Adjustment Guidelines

Default weights work for most product stages. Adjust in the following scenarios:

| Stage / Situation | Adjustment |
|---|---|
| Pre-revenue (finding PMF) | Increase `customer_impact` to 0.40; reduce `revenue_impact` to 0.15 |
| Revenue-focused (scaling) | Increase `revenue_impact` to 0.40; reduce `strategic_alignment` to 0.05 |
| Enterprise sales motion | Increase `strategic_alignment` to 0.20; increase `technical_risk` to 0.20 |
| Heavy technical debt phase | Use tech debt formula for all items; normal formula for new features |
| Compliance-driven sprint | Add `compliance_requirement` dimension (0–10); weight 0.25 |

Document weight changes in the memory packet under `decisions.accepted`.

---

## Build / Buy / Partner Decision Framework

For any capability evaluation:

| Factor | Build | Buy | Partner |
|---|---|---|---|
| Core differentiator | Yes | No | No |
| Time to market critical | No | Yes | Maybe |
| Vendor lock-in acceptable | — | No | Maybe |
| Long-term cost (3y) | Low (if owned) | High (SaaS) | Medium |
| Control required | High | Low | Medium |
| Market already solved | No | Yes | Yes |

Score each factor: sum of "Yes" counts determines recommendation.
Build if ≥ 3 Build columns match. Buy if ≥ 3 Buy columns match. Otherwise: Partner or hybrid.

---

## Roadmap Capacity Constraint

```
available_capacity_weeks = team_size × sprint_weeks × (1 - overhead_factor)
overhead_factor = 0.20  # 20% for meetings, reviews, incidents
```

Commitment rule: never commit > 80% of available capacity to planned work.
Reserve 20% for unplanned work, bug fixes, and reactive tasks.