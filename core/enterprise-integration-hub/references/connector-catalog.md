# Enterprise Integration Hub — Connector Catalog

## Connector Registry

| Connector ID | System | Type | Auth Method | Rate Limit | Data Classification |
|-------------|--------|------|------------|------------|---------------------|
| `sap-erp` | SAP S/4HANA | ERP | OAuth2 + mTLS | 1000 req/min | CONFIDENTIAL |
| `oracle-erp` | Oracle ERP Cloud | ERP | OAuth2 | 600 req/min | CONFIDENTIAL |
| `salesforce` | Salesforce CRM | CRM | OAuth2 (SFDX) | 1000 req/5min | INTERNAL |
| `hubspot` | HubSpot CRM | CRM | OAuth2 | 100 req/10s | INTERNAL |
| `servicenow` | ServiceNow ITSM | ITSM | OAuth2 | 100 req/min | INTERNAL |
| `jira-sm` | Jira Service Mgmt | ITSM | OAuth2 | 50 req/min | INTERNAL |
| `workday` | Workday HRIS | HRIS | OAuth2 | 60 req/min | RESTRICTED |
| `bamboohr` | BambooHR | HRIS | API Key | 100 req/hr | RESTRICTED |
| `slack` | Slack | Communication | Bot Token | Tier 2 rate limits | INTERNAL |
| `ms-teams` | Microsoft Teams | Communication | OAuth2 | Graph API limits | INTERNAL |
| `gmail` | Google Workspace | Email | OAuth2 | 250 quota units/s | INTERNAL |

---

## Canonical Entity Schema

### Budget Actuals (ERP → Platform)
```yaml
budget_actuals:
  entity_type: budget_actuals
  source_system: sap-erp | oracle-erp
  retrieved_at: "2026-05-07T10:00:00Z"
  entries:
    - cost_center: "CC-ENG-001"
      gl_code: "6000"
      description: "Cloud compute"
      period: "2026-05"
      actual_usd: 142000
      budget_usd: 130000
      variance_usd: 12000
      variance_pct: 0.092
```

### Opportunity (CRM → Platform)
```yaml
opportunity:
  entity_type: opportunity
  source_system: salesforce | hubspot
  retrieved_at: "2026-05-07T10:00:00Z"
  opportunity_id: "OPP-00123456"
  name: "Acme Corp — Enterprise License"
  stage: "Proposal/Price Quote"
  amount_usd: 250000
  close_date: "2026-06-30"
  owner: "alice@corp.com"
  account: "Acme Corp"
  last_activity_date: "2026-05-05"
  days_in_stage: 12
  activity_recency_days: 2
```

### Incident (ITSM → Platform)
```yaml
incident:
  entity_type: incident
  source_system: servicenow | jira-sm
  retrieved_at: "2026-05-07T10:00:00Z"
  incident_id: "INC-0001234"
  title: "vLLM inference engine degraded"
  severity: P1
  status: open | in_progress | resolved | closed
  assignee: "bob@corp.com"
  affected_ci: "inference-fleet/vllm-prod"
  created_at: "2026-05-07T09:00:00Z"
  updated_at: "2026-05-07T09:45:00Z"
  resolution_notes: null
```

---

## Rate Limit Management

```python
class RateLimitManager:
    """
    Token bucket rate limiter per connector.
    Queues requests when bucket is empty rather than dropping.
    """
    def __init__(self, connector_id: str, rate: int, window_seconds: int):
        self.connector_id = connector_id
        self.rate = rate
        self.window_seconds = window_seconds
        self.tokens = rate  # Start full

    def acquire(self, timeout_seconds: float = 30.0) -> bool:
        """
        Acquire a token. Blocks up to timeout_seconds.
        Returns False if timeout exceeded.
        """
        start = time.monotonic()
        while self.tokens <= 0:
            if time.monotonic() - start > timeout_seconds:
                return False
            time.sleep(0.1)
            self._refill()

        self.tokens -= 1
        return True

    def _refill(self):
        # Refill tokens based on elapsed time
        elapsed = time.monotonic() - self.last_refill
        new_tokens = elapsed * (self.rate / self.window_seconds)
        self.tokens = min(self.rate, self.tokens + new_tokens)
        self.last_refill = time.monotonic()
```

---

## Webhook Validation

```python
def validate_webhook_signature(
    payload: bytes,
    signature_header: str,
    secret: bytes,
    algorithm: str = "sha256"
) -> bool:
    """
    Validate HMAC signature on inbound webhook.
    Supports GitHub-style (X-Hub-Signature-256) and Slack-style signing.
    """
    import hmac, hashlib

    expected = hmac.new(
        key=secret,
        msg=payload,
        digestmod=getattr(hashlib, algorithm)
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(
        f"{algorithm}={expected}",
        signature_header
    )
```

---

## Cache TTL Policy by Connector

| Connector | Entity | Cache TTL | Rationale |
|-----------|--------|-----------|-----------|
| sap-erp | budget_actuals | 4 hours | Financial data: near-real-time acceptable |
| salesforce | opportunity | 30 minutes | Pipeline data: frequent changes |
| servicenow | incident | 5 minutes | Incident status changes rapidly |
| workday | employee_roster | 24 hours | HR data: slow-changing |
| slack | channel_metadata | 1 hour | Channels rarely change |

---

## Error Handling

```yaml
connector_error_handling:
  auth_failure:
    action: refresh_token_and_retry
    max_retries: 1
    on_retry_failure: return_error(auth_failed)

  rate_limit:
    action: queue_and_retry_with_backoff
    backoff: exponential
    initial_delay_s: 5
    max_delay_s: 300
    max_retries: 5

  system_unavailable:
    action: return_cached_if_available_else_error
    stale_cache_warning: true

  timeout:
    request_timeout_s: 30
    on_timeout: return_error(system_unavailable)
```