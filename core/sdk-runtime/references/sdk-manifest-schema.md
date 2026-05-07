# SDK Runtime — SDK Manifest Schema & Sandbox Lifecycle

## SDK Manifest Schema

```yaml
sdk_manifest:
  manifest_version: "1.0"
  skill_name: kebab-case-name          # Must match directory name
  skill_version: "x.y.z"              # SemVer
  runtime_api_version: "2026-05"      # Runtime API compatibility target

  entrypoint:
    handler: "skill.main:handle"      # module:function
    timeout_seconds: 30
    memory_limit_mb: 512

  permissions:
    network: false                    # Outbound HTTP allowed?
    filesystem: read_only             # none | read_only | read_write (scoped)
    subprocess: false
    secrets: []                       # Named secrets the skill may access

  resource_quotas:
    max_tokens_per_call: 8192
    max_calls_per_minute: 60
    max_concurrent_executions: 4
    max_storage_mb: 100

  dependencies:
    skills: []                        # Other skills this skill invokes
    external_apis: []                 # Declared external endpoints
    models: []                        # Model IDs required

  checksum:
    algorithm: sha256
    value: "abc123..."               # SHA-256 of the skill bundle at publish time

  author:
    name: "Author Name"
    org: "Organization"
    contact: "email@example.com"

  certification:
    status: pending | certified | revoked
    certified_at: null
    certified_by: null
    tier: community | verified | enterprise
```

---

## Sandbox Lifecycle

```
SKILL INVOCATION FLOW

1. Request arrives at SDK Runtime
        │
        ▼
2. Manifest lookup (skill registry)
        │
        ▼
3. Checksum verification
   ├── PASS → continue
   └── FAIL → reject; log INTEGRITY_VIOLATION
        │
        ▼
4. Permission gate (request vs. manifest)
   ├── PASS → continue
   └── FAIL → reject; log PERMISSION_DENIED
        │
        ▼
5. Quota check (rate + concurrency)
   ├── WITHIN QUOTA → continue
   └── EXCEEDED → return 429; log QUOTA_EXCEEDED
        │
        ▼
6. Sandbox spawn (isolated Python env)
        │
        ▼
7. Inject approved secrets (vault fetch)
        │
        ▼
8. Execute handler (timeout watchdog active)
   ├── SUCCESS → collect output
   └── TIMEOUT → SIGKILL; log TIMEOUT
        │
        ▼
9. Output validation (schema check)
        │
        ▼
10. Emit telemetry; return result
```

---

## Permission Taxonomy

| Permission | Values | Default | Notes |
|-----------|--------|---------|-------|
| `network` | `true` / `false` | `false` | Any outbound HTTP/HTTPS |
| `filesystem` | `none` \| `read_only` \| `read_write` | `none` | Scoped to `/var/skill-data/<skill-name>/` |
| `subprocess` | `true` / `false` | `false` | Shell execution |
| `secrets` | list of secret names | `[]` | Must be pre-approved in registry |
| `inter_skill_calls` | list of skill names | `[]` | Skills this skill may invoke |

---

## Resource Quota Defaults by Tier

| Tier | Tokens/Call | Calls/Min | Concurrent | Storage |
|------|------------|-----------|------------|---------|
| Community | 4,096 | 10 | 1 | 10 MB |
| Verified | 8,192 | 60 | 4 | 100 MB |
| Enterprise | 32,768 | 300 | 16 | 1 GB |

---

## Checksum Verification Protocol

```python
import hashlib
import json
from pathlib import Path

def verify_skill_bundle(bundle_path: str, manifest_checksum: str) -> bool:
    """
    Compute SHA-256 of all skill files (sorted for determinism)
    and compare against manifest-declared checksum.
    """
    h = hashlib.sha256()
    bundle = Path(bundle_path)

    for fpath in sorted(bundle.rglob("*")):
        if fpath.is_file() and fpath.name != "manifest.yaml":
            h.update(fpath.read_bytes())

    computed = h.hexdigest()
    return computed == manifest_checksum
```

---

## Sandbox Violation Event Schema

```yaml
violation_event:
  event_id: "VIOL-2026-xxxxx"
  skill_name: "skill-name"
  skill_version: "x.y.z"
  violation_type: INTEGRITY_VIOLATION | PERMISSION_DENIED | QUOTA_EXCEEDED | TIMEOUT | SCHEMA_VIOLATION
  severity: critical | high | medium | low
  timestamp: "2026-05-07T10:00:00Z"
  invocation_id: "INV-2026-xxxxx"
  detail: "Description of what was attempted or exceeded"
  action_taken: rejected | terminated | throttled
  escalated_to: null | "security-architect-agent"
```