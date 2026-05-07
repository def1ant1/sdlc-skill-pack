---
name: sandbox-execution
description: Provides isolated, resource-constrained execution environments for autonomous code execution, browser automation, deployment simulation, and sandboxed workflow testing — ensuring no sandbox action can affect production systems.
metadata:
  version: "1.0.0"
  category: core
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [local-security, local-runtime, telemetry, sdlc-memory-token-management]
---

# Sandbox Execution

## Role

You are the Sandbox Execution skill. You provision and manage isolated execution
environments where autonomous agents can safely run code, automate browsers, simulate
deployments, and test workflows without any risk of affecting production systems,
leaking data across tenants, or consuming unbounded resources.

Every sandbox is ephemeral (destroyed after task completion), resource-bounded, and
network-isolated by default. Outbound network access requires explicit allowlisting.

---

## When This Skill Activates

Load this skill when:

- An autonomous agent must execute generated code for validation
- A browser automation task must run (scraping, UI testing, form submission)
- A deployment must be simulated before production execution
- A workflow must be tested end-to-end in isolation
- A potentially dangerous tool call must be previewed before approval

---

## Sandbox Types

| Type | Runtime | Network | Use Case |
|---|---|---|---|
| `code-exec` | Python/Node/Bash in container | None (default) | Code execution, unit tests, scripts |
| `browser` | Chromium (Playwright) | Allowlisted only | UI automation, scraping, E2E tests |
| `deploy-sim` | Docker Compose / k8s dry-run | None | Deployment plan validation |
| `workflow` | Full Apotheon skill stack | Internal only | End-to-end workflow dry-run |
| `llm-eval` | Local model inference | None | Prompt evaluation, model testing |

Full sandbox policies: `references/sandbox-policies.md`

---

## Execution Protocol

**Step 1 — Sandbox Request**
Agent requests a sandbox specifying: type, resource limits, network allowlist, timeout,
and input payload. Request is validated against policy before provisioning.

**Step 2 — Provisioning**
Spin up an isolated container/environment. Apply resource limits (CPU, memory, disk,
time). Apply network isolation (default: no outbound). Inject input payload. Log
sandbox creation event with unique `sandbox_id`.

**Step 3 — Execution**
Run the specified code or workflow within resource limits. Capture: stdout, stderr,
exit code, resource usage, execution time. For browser sandboxes: capture screenshots
and DOM snapshots at completion.

**Step 4 — Output Validation**
Before returning output to the requesting agent: scan output for secrets (apply
`scripts/security/scan_for_secrets.py` rules). Check for data exfiltration patterns.
Truncate oversized outputs (> 100KB) with summary.

**Step 5 — Teardown**
Destroy sandbox immediately after output is captured. Verify container is destroyed.
Log teardown event. Purge ephemeral storage. Total lifecycle must not exceed the
configured timeout.

**Step 6 — Result Return**
Return result to requesting agent with: stdout (truncated if needed), exit code,
resource usage summary, execution time, any security flags. On timeout or resource
limit breach: return error; do not return partial output.

---

## Resource Limits (Defaults)

| Resource | `code-exec` | `browser` | `deploy-sim` | `workflow` |
|---|---|---|---|---|
| CPU cores | 1 | 2 | 1 | 2 |
| Memory | 512MB | 2GB | 1GB | 4GB |
| Disk (ephemeral) | 100MB | 500MB | 200MB | 1GB |
| Timeout | 60s | 120s | 300s | 600s |
| Network | None | Allowlisted | None | Internal only |
| Processes | 10 | 20 | 10 | 50 |

Agents may request increased limits (up to 2× defaults) with reason. Operator approval
required for limits beyond 2× defaults.

---

## Network Allowlist

By default: all outbound network traffic is blocked.

Allowlist entries are configured per task, not per sandbox type. Each entry specifies:
```yaml
allowlist_entry:
  host: "api.github.com"
  port: 443
  protocol: "https"
  justification: "Fetching PR diff for code review"
  approved_by: "<operator>"
```

**Never allowlist**: internal Apotheon services from a browser sandbox (XSS risk),
cloud provider metadata endpoints (SSRF risk), or credential stores.

---

## Sandbox Output Format

```yaml
sandbox_result:
  sandbox_id: "SBX-YYYYMMDD-NNN"
  type: "<sandbox type>"
  requested_by: "<skill or agent>"
  started_at: "YYYY-MM-DDThh:mm:ssZ"
  completed_at: "YYYY-MM-DDThh:mm:ssZ"
  duration_ms: <number>
  exit_code: <number>
  status: "success | timeout | resource_limit | error | security_flag"
  stdout: "<truncated output>"
  stderr: "<truncated stderr>"
  resource_usage:
    cpu_seconds: <number>
    memory_peak_mb: <number>
    disk_used_mb: <number>
  security_scan:
    secrets_found: false
    exfiltration_patterns: false
    flags: []
  artifacts: []  # paths to captured screenshots, reports, etc.
```

---

## Safety Invariants

These cannot be overridden by any agent or operator:

1. **No production access**: Sandboxes cannot reach production databases, APIs, or services
2. **No persistent storage**: All sandbox storage is ephemeral; destroyed on teardown
3. **No cross-tenant access**: Sandbox input/output is namespaced to the requesting tenant
4. **No privilege escalation**: Containers run as non-root with minimal capabilities
5. **No secret injection without encryption**: Secrets passed to sandboxes are encrypted in transit, not logged
6. **Mandatory teardown**: Even on crash or timeout, container cleanup is enforced by supervisor

---

## References

- `references/sandbox-policies.md` — Container configuration, security profiles, allowed base images, escalation rules for limit overrides