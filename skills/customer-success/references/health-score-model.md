# Health Score Model

Used by `skills/customer-success/SKILL.md` to compute customer health scores,
define segment thresholds, and trigger intervention workflows.

---

## Health Score Formula

```
health_score = (
  (login_frequency_score × 0.25) +
  (feature_adoption_score × 0.30) +
  (support_sentiment_score × 0.20) +
  (nps_score_normalized × 0.15) +
  (billing_health_score × 0.10)
) × 100
```

All component scores are normalized to 0.0–1.0 before weighting.

---

## Component Definitions

### Login Frequency Score

| Logins (last 30 days) | Score |
|---|---|
| ≥ 20 | 1.0 |
| 10–19 | 0.8 |
| 5–9 | 0.6 |
| 2–4 | 0.3 |
| 0–1 | 0.0 |

### Feature Adoption Score

```
feature_adoption_score = features_used_last_30d / total_available_features
```

Cap at 1.0. Apply tier adjustment: enterprise customers scored against enterprise feature set.

### Support Sentiment Score

```
support_sentiment_score = (
  1.0 - (open_p0_tickets × 0.5 + open_p1_tickets × 0.2 + open_p2_tickets × 0.05)
)
```

Floor at 0.0. A single open P0 ticket caps the support sentiment score at 0.5.

### NPS Score Normalized

```
nps_score_normalized = (latest_nps_response + 10) / 20
```

Maps NPS range (−10 to +10 individual score, i.e. raw 0–10 individual) to 0.0–1.0.
If no NPS response in last 90 days: use 0.5 (neutral).

### Billing Health Score

| Condition | Score |
|---|---|
| No overdue invoices | 1.0 |
| 1–7 days overdue | 0.7 |
| 8–30 days overdue | 0.3 |
| > 30 days overdue | 0.0 |
| Failed payment pending retry | 0.5 |

---

## Segment Thresholds

| Segment | Score Range | Color | Action |
|---|---|---|---|
| Healthy | 70–100 | Green | Routine check-ins; expansion opportunity |
| Developing | 50–69 | Yellow | Proactive outreach; offer enablement |
| At-Risk | 30–49 | Orange | CS manager assigned; intervention plan |
| Critical | 0–29 | Red | Executive escalation; same-day outreach |

---

## Score Modifiers

Apply after computing base score:

| Condition | Modifier |
|---|---|
| Customer is in first 30 days (onboarding) | +10 points (grace period) |
| Open P0 ticket | −20 points (hard penalty) |
| Upcoming renewal within 30 days | Flag for review regardless of score |
| NRR > 120% (expanding) | +5 points |
| Churned a previous account | −10 points |

---

## Health Score Update Cadence

- **Computed**: Daily (batch job at 02:00 UTC)
- **CRM write**: Daily (after computation)
- **Alert trigger**: Immediate on any segment downgrade (Healthy→Developing, Developing→At-Risk, At-Risk→Critical)
- **Weekly summary**: Every Monday 08:00 UTC to CS team

---

## Intervention Workflows

| From Segment | To Segment | Automated Action | Human Action |
|---|---|---|---|
| Healthy | Developing | Send enablement email | CS notified |
| Developing | At-Risk | Schedule check-in call | CS manager assigned within 24h |
| At-Risk | Critical | Executive alert sent | VP CS outreach same day |
| Any | Any (renewal < 30d) | Renewal prep deck generated | AE assigned |