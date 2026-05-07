# Isolation Model

Used by `core/tenant-management/SKILL.md` to specify isolation boundary enforcement,
audit check procedures, and violation response protocol.

---

## Isolation Enforcement Architecture

```
Request → Tenant Context Resolver
            │
            ├── Extract: org_id + workspace_id from auth token
            ├── Validate: token signature, tenant status = active
            └── Inject: tenant context into all downstream calls
                        │
                        ├── Memory: namespace prefix enforced
                        ├── Vector store: metadata filter injected
                        ├── Knowledge graph: subgraph filter applied
                        ├── Connector vault: key scoped to tenant
                        ├── Telemetry: tenant_id tag required
                        └── Deployment: target list filtered
```

Every layer enforces isolation independently. Failure of one layer must not expose
another tenant's data (defense in depth).

---

## Memory Namespace Isolation

**Key prefix format:**
```
apotheon:{org_id}:{workspace_id}:{key_type}:{key_name}
```

**Examples:**
```
apotheon:a1b2c3:w4d5e6:memory_packet:current
apotheon:a1b2c3:w4d5e6:decision:arch-2026-001
apotheon:a1b2c3:w4d5e6:artifact:design_doc_v2
```

**Enforcement rules:**
1. All reads: prepend tenant prefix before key lookup; never accept bare keys from API
2. All writes: prepend tenant prefix; reject if caller's tenant does not match key prefix
3. Key enumeration: filter by prefix; never return keys from other tenants
4. Backup/restore: backup files are tenant-namespaced and encrypted per tenant

---

## Vector Store Isolation

Every embedding document must include:
```json
{
  "metadata": {
    "org_id": "<uuid>",
    "workspace_id": "<uuid>",
    "tenant_key": "<org_id>:<workspace_id>"
  }
}
```

All queries must include a metadata filter:
```json
{
  "filter": {
    "tenant_key": {"$eq": "<org_id>:<workspace_id>"}
  }
}
```

**Never** execute a vector query without the tenant filter. If filter is missing: reject
the query, log `MISSING_TENANT_FILTER`, alert.

---

## Knowledge Graph Isolation

All graph nodes carry a mandatory property:
```
node.tenant_key = "<org_id>:<workspace_id>"
```

All traversal queries include a `WHERE n.tenant_key = $tenant_key` clause.
Cross-tenant relationship creation is blocked at the graph write layer.

**Cypher template:**
```cypher
MATCH (n)
WHERE n.tenant_key = $tenant_key
AND <additional filters>
RETURN n
```

---

## Connector Credential Isolation

Credentials stored in vault under:
```
credentials/{org_id}/{workspace_id}/{connector_name}
```

Access pattern:
1. Caller provides `org_id`, `workspace_id`, `connector_name`
2. Vault constructs key; returns credential only if tenant context matches auth token
3. Credentials are never logged, cached in memory packets, or returned in API responses
4. Credential rotation: per tenant; rotation of one tenant never affects others

---

## Automated Daily Isolation Audit

Run nightly at 01:00 UTC:

```
Check 1: Memory key scan — verify no keys exist without valid org_id:workspace_id prefix
Check 2: Vector store audit — sample 100 documents; verify tenant_key metadata present on all
Check 3: Graph node audit — verify all nodes have tenant_key property
Check 4: Credential vault audit — verify all entries have valid org_id/workspace_id path
Check 5: Telemetry event audit — verify all events from last 24h have tenant_id tag
Check 6: Cross-tenant relation check — graph query for any relationship crossing tenant_key values
```

Output: isolation audit report. Any failure → severity Critical alert → halt new provisioning
until resolved.

---

## Isolation Violation Response Protocol

On detection of any isolation violation:

1. **Immediate**: Block all requests from the affected tenant(s)
2. **Within 5 min**: Alert operator with: violation type, affected tenants, data scope
3. **Within 30 min**: Forensic log pull — determine what data was exposed
4. **Within 1h**: Assess whether breach constitutes a notifiable incident (GDPR Art.33, HIPAA)
5. **Within 24h**: Root cause analysis; remediation applied; isolation restored
6. **Within 72h**: Incident report to affected tenant(s); regulatory notification if required

**Violation severity classification:**

| Violation | Severity | Action |
|---|---|---|
| Missing tenant filter on query | High | Block, log, alert, fix |
| Read of another tenant's data | Critical | Block, alert, forensics, notify |
| Write to another tenant's namespace | Critical | Block, alert, forensics, notify, regulatory assessment |
| Credential exposure across tenants | Critical | Revoke all credentials, rotate, forensics, notify |

---

## Tenant Deprovision Checklist

```
[ ] Level-3 approval obtained (two operators)
[ ] 30-day hold period completed
[ ] Tenant notified of data deletion date
[ ] Data export provided to tenant (if requested)
[ ] Memory namespace purged (all keys deleted)
[ ] Vector embeddings deleted (collection or metadata-filtered delete)
[ ] Knowledge graph subgraph deleted (all tenant_key nodes)
[ ] Connector credentials revoked and vault entries deleted
[ ] Telemetry data purged (beyond retention minimum)
[ ] Billing records archived (legal minimum: 7 years)
[ ] Deletion certificate generated and stored
```