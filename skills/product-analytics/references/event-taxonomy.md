# Event Taxonomy

Used by `skills/product-analytics/SKILL.md` to define event naming schemas,
required properties, and the standard event category catalog.

---

## Naming Convention

```
<noun>_<verb>
```

- Lowercase snake_case only
- Noun: the object being acted on (e.g. `workflow`, `export`, `user`, `team`)
- Verb: past tense action (e.g. `created`, `deleted`, `viewed`, `completed`)
- Examples: `workflow_created`, `export_downloaded`, `team_invited`, `session_started`

**Anti-patterns:**
- `clicked_button` — too generic; name what was clicked
- `WorkflowCreated` — PascalCase not allowed
- `workflow-created` — hyphens not allowed
- `create_workflow` — verbs must be past tense

---

## Required Properties (All Events)

```yaml
properties:
  user_id:         string   # internal UUID; never PII email
  anonymous_id:    string   # pre-login identifier; links to user_id on signup
  session_id:      string   # UUID; new on each browser/app session
  timestamp:       string   # ISO 8601 UTC (e.g. 2026-05-06T14:23:00Z)
  platform:        string   # web | mobile | api | cli
  plan_tier:       string   # free | starter | pro | enterprise
  app_version:     string   # semver (e.g. 1.4.2)
  event_version:   integer  # schema version for this event (increment on breaking change)
```

---

## Event Categories

### Identity Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `user_signed_up` | Account created | `signup_method` (email/google/github), `referral_source` |
| `user_logged_in` | Successful login | `auth_method` |
| `user_logged_out` | Explicit logout | — |
| `user_profile_updated` | Profile field changed | `fields_changed[]` |
| `password_reset_completed` | Password reset | — |

### Onboarding Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `onboarding_started` | Onboarding flow entered | `track_name` |
| `onboarding_step_completed` | Each step finished | `step_name`, `step_index`, `time_on_step_seconds` |
| `onboarding_completed` | All steps done | `total_duration_seconds`, `track_name` |
| `onboarding_skipped` | User skipped flow | `skip_step`, `step_index` |
| `first_value_reached` | User hits first meaningful output | `feature_name`, `ttfv_seconds` |

### Workflow / Core Feature Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `workflow_created` | New workflow started | `workflow_type`, `template_used` |
| `workflow_executed` | Workflow run triggered | `workflow_id`, `input_type`, `model_used` |
| `workflow_completed` | Workflow finished successfully | `workflow_id`, `duration_ms`, `output_tokens` |
| `workflow_failed` | Workflow error | `workflow_id`, `error_code`, `error_message` |
| `workflow_deleted` | Workflow removed | `workflow_id` |

### Collaboration Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `team_member_invited` | Invitation sent | `invitee_role`, `invite_method` |
| `team_member_joined` | Invitation accepted | `invitee_role` |
| `workspace_created` | New workspace | `workspace_type` |
| `asset_shared` | Content shared | `asset_type`, `share_scope` |

### Integration Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `integration_connected` | OAuth/API key saved | `integration_name`, `integration_type` |
| `integration_disconnected` | Integration removed | `integration_name` |
| `webhook_triggered` | Outbound webhook fired | `webhook_id`, `destination` |

### Revenue Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `subscription_started` | First payment captured | `plan`, `billing_period`, `revenue_amount_usd` |
| `subscription_upgraded` | Plan upgraded | `from_plan`, `to_plan`, `revenue_delta_usd` |
| `subscription_downgraded` | Plan downgraded | `from_plan`, `to_plan`, `revenue_delta_usd` |
| `subscription_cancelled` | Cancellation confirmed | `plan`, `reason`, `months_active` |
| `payment_failed` | Charge declined | `failure_reason`, `retry_count` |

### Engagement Events

| Event | Trigger | Additional Properties |
|---|---|---|
| `feature_discovered` | User opens feature for first time | `feature_name` |
| `feature_used` | Feature action completed | `feature_name`, `feature_version` |
| `help_article_viewed` | KB article opened | `article_id`, `search_query` |
| `nps_survey_submitted` | NPS response recorded | `score`, `verbatim` (anonymized) |
| `feedback_submitted` | In-app feedback form sent | `feedback_type`, `rating` |

---

## Event Schema Validation Rules

1. `user_id` must be a UUID v4 — never an email or username
2. `timestamp` must be UTC ISO 8601 — reject local time
3. `plan_tier` must match the enum: `free | starter | pro | enterprise`
4. Revenue events require `subscription_id` (UUID); missing = schema validation failure
5. `event_version` increments only on breaking property changes (new required property, renamed property, type change)
6. Additive-only changes (new optional property) do NOT require version increment

---

## Instrumentation Checklist

For each new event:

```
[ ] Event name follows noun_verb convention
[ ] All required properties present
[ ] Category-specific properties added
[ ] event_version set to 1 (new event)
[ ] Event registered in tracking plan
[ ] Unit test added: valid payload passes schema; missing required field fails
[ ] Engineering review approved before shipping
[ ] Analytics review approved before using in dashboards
```