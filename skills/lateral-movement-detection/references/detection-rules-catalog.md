# Lateral Movement Detection — Detection Rules Catalog

## Detection Rule Schema

```yaml
detection_rule:
  rule_id: "LMD-RULE-2026-xxxxx"
  rule_name: "Credential stuffing from new IP range"
  rule_version: "1.0.0"
  mitre_technique: "T1110.004"   # MITRE ATT&CK technique ID
  mitre_tactic: credential_access

  severity: critical | high | medium | low
  confidence: high | medium | low

  data_sources:
    - auth_logs
    - network_flow_logs
    - agent_activity_logs

  detection_logic:
    type: threshold | statistical | ml_model | rule_chain
    description: |
      Alert if a single source IP generates ≥ 5 failed authentication
      attempts across ≥ 3 distinct user accounts within a 10-minute window.

  false_positive_rate: low
  tuning_notes: "Exclude known penetration testing IP ranges"

  response:
    automated:
      - block_source_ip_for_minutes: 60
      - invalidate_active_sessions_for_accounts: true
    escalation:
      - notify: security-architect-agent
      - severity_if_sustained_attack: critical
      - create_incident: true
```

---

## Detection Rules Catalog

### Rule LMD-001: Credential Stuffing

```yaml
rule_id: LMD-001
rule_name: Credential Stuffing — Multi-Account Failed Auth
mitre_technique: T1110.004
severity: high

logic:
  query: |
    count(distinct account_id) WHERE event=auth_failure AND
    source_ip = X AND time_window = 10min >= 3
    AND count(auth_failure) >= 5

threshold:
  auth_failures: 5
  distinct_accounts: 3
  window_minutes: 10
```

### Rule LMD-002: Impossible Travel

```yaml
rule_id: LMD-002
rule_name: Impossible Travel — Authentication from Geographically Distant IPs
mitre_technique: T1078
severity: high

logic:
  query: |
    For each principal_id: if two auth_success events occur within 1 hour
    from locations where travel distance / time implies speed > 900 km/h
  threshold:
    implied_speed_kmh: 900
    window_minutes: 60
```

### Rule LMD-003: Agent Privilege Escalation Attempt

```yaml
rule_id: LMD-003
rule_name: Agent Requesting Permissions Beyond Declared Scope
mitre_technique: T1078.004
severity: critical

logic:
  query: |
    Agent action request where:
    - requested_permission NOT IN skill_manifest.permissions
    - AND policy_evaluation = DENY
    - AND frequency >= 3 within 5 minutes (may be probing)

response:
  automated:
    - suspend_agent_session: true
    - alert: security-architect-agent
  escalation:
    - create_incident: true
    - severity: critical
```

### Rule LMD-004: Unusual Data Exfiltration Volume

```yaml
rule_id: LMD-004
rule_name: Anomalous Outbound Data Volume
mitre_technique: T1041
severity: high

logic:
  method: statistical_baseline
  query: |
    For each principal_id: if outbound_bytes in rolling_1h >
    mean(outbound_bytes, last_30d) + 5 * stddev(outbound_bytes, last_30d)
    AND destination NOT IN approved_external_apis

alert_on_sustained: true   # Only alert if anomaly persists > 5 min
```

### Rule LMD-005: Service Account Used Interactively

```yaml
rule_id: LMD-005
rule_name: Service Account Interactive Login
mitre_technique: T1078.002
severity: medium

logic:
  query: |
    auth_success WHERE
    principal_type = service_account AND
    auth_method IN [interactive_login, password_auth] AND
    NOT auth_method = api_key

# Service accounts should only auth via mTLS or API key, never interactively
```

### Rule LMD-006: Lateral Movement via Internal API Calls

```yaml
rule_id: LMD-006
rule_name: Agent Calling Unrelated Internal APIs
mitre_technique: T1021
severity: medium

logic:
  query: |
    Agent skill_name=X makes API call to service Y where
    Y NOT IN skill_manifest[X].dependencies AND
    Y NOT IN allowed_discovery_endpoints AND
    call_count > 3

response:
  automated:
    - rate_limit_agent: true
    - flag_for_review: true
```

---

## Threat Intel Feed Integration

```yaml
threat_intel:
  feeds:
    - name: "MISP Community Feed"
      url: "https://misp.example.com/feeds/1"
      format: MISP
      refresh_hours: 4
      ioc_types: [ip, domain, hash, url]

    - name: "Feodo Tracker"
      url: "https://feodotracker.abuse.ch/downloads/ipblocklist.csv"
      format: csv
      refresh_hours: 1
      ioc_types: [ip]

  enrichment:
    # Enrich auth events with threat intel before rule evaluation
    ip_reputation_check: true
    known_tor_exit_nodes: true
    known_vpn_providers: true    # Flag but do not auto-block
```

---

## Alert Severity → Response Matrix

| Severity | Auto-Block | Create Incident | Notify | HITL Required |
|----------|-----------|----------------|--------|--------------|
| Critical | Yes (immediate) | Yes (P1) | security-architect-agent + on-call | Yes |
| High | Yes (5-min cooldown) | Yes (P2) | security-architect-agent | Yes |
| Medium | Rate-limit only | Yes (P3) | security-architect-agent | No |
| Low | No | No | Log only | No |

---

## Detection Coverage Matrix

| MITRE Tactic | Rules Coverage |
|-------------|---------------|
| Reconnaissance | LMD-006 |
| Initial Access | LMD-001, LMD-002 |
| Persistence | LMD-005 |
| Privilege Escalation | LMD-003 |
| Defense Evasion | LMD-005 |
| Credential Access | LMD-001, LMD-002 |
| Discovery | LMD-006 |
| Lateral Movement | LMD-006 |
| Exfiltration | LMD-004 |