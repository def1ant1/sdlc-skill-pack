# Sandbox Policies

Used by `core/sandbox-execution/SKILL.md` to define container configuration,
security profiles, allowed base images, and limit override escalation rules.

---

## Container Configuration

All sandboxes use OCI-compliant containers (Docker or containerd).

### Base Security Profile

```yaml
security_profile:
  run_as_user: 65534        # nobody user
  run_as_group: 65534
  read_only_root_filesystem: true
  allow_privilege_escalation: false
  drop_capabilities:        # drop all Linux capabilities
    - ALL
  add_capabilities: []      # none added by default
  seccomp_profile: "runtime/default"
  apparmor_profile: "runtime/default"
  no_new_privileges: true
```

### Network Policy

```yaml
network_policy:
  mode: "none"              # default: no network
  dns: null                 # no DNS resolution
  outbound_rules: []        # filled from allowlist only
  inbound_rules: []         # no inbound connections permitted
  loopback_only: false      # loopback not enabled by default
```

For `browser` sandboxes only: loopback enabled for Playwright→Chromium IPC.

---

## Allowed Base Images

Only the following base images may be used. Using an unlisted image is blocked.

| Image | Tag | Sandbox Types | Notes |
|---|---|---|---|
| `python` | `3.12-slim` | code-exec | Standard Python execution |
| `node` | `20-slim` | code-exec | JavaScript/TypeScript execution |
| `bash` | `5-alpine` | code-exec | Shell script execution |
| `mcr.microsoft.com/playwright` | `v1.44.0-noble` | browser | Playwright + Chromium |
| `alpine` | `3.19` | deploy-sim, code-exec | Minimal Linux |
| `apotheon/workflow-runner` | `latest` | workflow | Internal Apotheon image |

To add a new approved image: submit a security review request with:
- Image source and publisher
- CVE scan results (no Critical/High CVEs)
- Justification for new image
- Operator approval (Level-3)

---

## Resource Limit Override Rules

| Override Level | Up To | Approval Required |
|---|---|---|
| 1× default | Default values | No approval |
| 2× default | 2× any default limit | Agent may self-approve with reason logged |
| 3× default | 3× any default limit | Operator approval (Level-2) |
| > 3× default | Unlimited | Operator approval (Level-3) + justification |

Overrides apply to a single sandbox instance. Persistent override policies require
Level-3 approval and are documented in the memory packet.

---

## Deployment Simulation (deploy-sim) Policy

The `deploy-sim` sandbox type runs deployment plans in dry-run mode:

- `kubectl apply --dry-run=server` for Kubernetes
- `terraform plan` (no apply) for infrastructure
- `docker-compose config` for validation
- Custom: any tool with `--dry-run` or `--plan` flag

**Prohibited in deploy-sim**: any command without an explicit dry-run mode.
If a tool cannot dry-run: the simulation must use a mock target, not a real endpoint.

**Simulate-before-deploy requirement**: All Level-3 deployments must have a
`deploy-sim` result attached to the approval request. Simulation failure = deployment
blocked until fixed.

---

## Browser Sandbox Policy

Permitted:
- Navigating to allowlisted domains
- Form interactions on allowlisted domains
- Screenshot capture
- DOM inspection and data extraction
- JavaScript execution on loaded pages

Prohibited:
- Downloading executable files
- Accessing browser credential stores
- Navigating to internal/private IP ranges (10.x, 172.16.x, 192.168.x)
- Accessing `file://` URLs
- Installing browser extensions

---

## Audit and Logging

Every sandbox lifecycle event is logged with `telemetry.record_event`:

```yaml
events:
  - sandbox_created:    {sandbox_id, type, tenant_id, resource_limits}
  - sandbox_started:    {sandbox_id, start_time}
  - sandbox_completed:  {sandbox_id, exit_code, duration_ms, resource_usage}
  - sandbox_timeout:    {sandbox_id, timeout_ms}
  - sandbox_error:      {sandbox_id, error_type, error_message}
  - sandbox_destroyed:  {sandbox_id, destroyed_at}
  - security_flag:      {sandbox_id, flag_type, details}
```

Logs retained per tenant telemetry retention policy.

---

## Escalation: Sandbox Security Incident

If a sandbox:
- Attempts network access beyond allowlist
- Tries to escalate privileges
- Exhibits fork bomb or resource exhaustion behavior
- Generates output containing secrets or PII

Actions:
1. Kill sandbox immediately (SIGKILL)
2. Log `SANDBOX_SECURITY_INCIDENT` with severity Critical
3. Alert operator
4. Quarantine: block same agent from creating new sandboxes until reviewed
5. Preserve logs for forensic review (do not purge)