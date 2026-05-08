# Analytics Intelligence — GTM Event Taxonomy

## Naming Convention

All events use `noun_verb` format in snake_case.

```
{noun}_{verb}

Examples:
  page_viewed          trial_started        feature_used
  signup_completed     demo_requested       subscription_upgraded
```

---

## Required Properties (All Events)

| Property | Type | Description |
|----------|------|-------------|
| `user_id` | string | Unique user identifier (UUID) |
| `anonymous_id` | string | Pre-auth identifier (cookie-based) |
| `session_id` | string | Current session identifier |
| `timestamp` | ISO 8601 | Event timestamp (UTC) |
| `platform` | string | web \| mobile_ios \| mobile_android \| api |
| `environment` | string | production \| staging \| development |

---

## GTM Event Catalog

### Acquisition Events

| Event | Trigger | Key Properties | Destination |
|-------|---------|---------------|-------------|
| `page_viewed` | Any page load | `page_url`, `page_title`, `referrer`, `utm_*` | GA4, Mixpanel |
| `cta_clicked` | CTA button click | `cta_text`, `cta_location`, `page_url` | GA4, Mixpanel |
| `signup_started` | Signup form opened | `source`, `plan_tier_selected` | GA4, Mixpanel |
| `signup_completed` | Account created | `plan_tier`, `acquisition_channel`, `trial_end_date` | GA4, Mixpanel, Segment |
| `demo_requested` | Demo form submitted | `company_size`, `industry`, `use_case` | GA4, Segment, CRM |
| `pricing_viewed` | Pricing page loaded | `referrer`, `utm_source` | GA4, Mixpanel |

### Activation Events

| Event | Trigger | Key Properties | Destination |
|-------|---------|---------------|-------------|
| `onboarding_started` | First login after signup | `plan_tier`, `days_since_signup` | Mixpanel |
| `onboarding_step_completed` | Each onboarding step | `step_name`, `step_index`, `total_steps` | Mixpanel |
| `first_value_achieved` | User reaches "aha moment" | `feature_name`, `days_to_activation` | Mixpanel, Segment |
| `workflow_created` | First workflow created | `workflow_type`, `duration_seconds` | Mixpanel |
| `integration_connected` | External tool connected | `integration_name`, `days_since_signup` | Mixpanel |

### Retention Events

| Event | Trigger | Key Properties | Destination |
|-------|---------|---------------|-------------|
| `session_started` | User opens app | `days_since_last_session`, `plan_tier` | Mixpanel |
| `feature_used` | Feature interaction | `feature_name`, `feature_version`, `usage_count_lifetime` | Mixpanel |
| `report_generated` | Report created | `report_type`, `data_range_days` | Mixpanel |
| `export_downloaded` | Data exported | `export_format`, `record_count` | Mixpanel |

### Revenue Events

| Event | Trigger | Key Properties | Destination |
|-------|---------|---------------|-------------|
| `trial_started` | Trial period begins | `plan_tier`, `trial_duration_days`, `acquisition_channel` | GA4, Mixpanel, Segment, ERP |
| `trial_converted` | Trial → paid | `plan_tier`, `mrr_usd`, `trial_duration_days` | GA4, Mixpanel, Segment, ERP |
| `subscription_upgraded` | Plan upgrade | `from_tier`, `to_tier`, `expansion_mrr_usd` | Segment, ERP |
| `subscription_downgraded` | Plan downgrade | `from_tier`, `to_tier`, `contraction_mrr_usd` | Segment, ERP |
| `subscription_cancelled` | Cancellation | `plan_tier`, `churned_mrr_usd`, `reason` | Segment, ERP |
| `payment_failed` | Payment failure | `plan_tier`, `attempt_number`, `failure_reason` | Segment |

---

## Event Routing Rules

| Destination | What Goes There | Auth |
|-------------|----------------|------|
| GA4 | Web events (page_viewed, cta_clicked, signup_completed, trial_started, trial_converted) | Measurement protocol key |
| Mixpanel | All product events, lifecycle events | Project token |
| Segment | Revenue events, identity events, cross-tool routing hub | Write key |
| CRM (Salesforce) | demo_requested, signup_completed (B2B) | Via Segment destination |
| ERP | Revenue events (trial_converted, upgraded, downgraded, cancelled) | Via Segment destination |

---

## Identity Resolution

```
Anonymous browsing:
  anonymous_id (cookie) → page_viewed, cta_clicked, pricing_viewed

After signup:
  identify(user_id, traits: {email, name, plan_tier, company, created_at})
  anonymous_id → user_id association via Segment identify() call

After payment:
  group(company_id, traits: {name, plan, mrr, seats})
```