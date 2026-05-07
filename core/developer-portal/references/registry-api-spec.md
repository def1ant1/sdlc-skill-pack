# Developer Portal — Registry API Specification

## REST API Endpoints

### Skill Registry

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/v1/skills` | List all certified skills | API key |
| `GET` | `/v1/skills/{name}` | Get skill metadata + manifest | API key |
| `GET` | `/v1/skills/{name}/versions` | List all versions of a skill | API key |
| `POST` | `/v1/skills` | Publish new skill version | Publisher token |
| `DELETE` | `/v1/skills/{name}/{version}` | Yank a skill version | Admin only |
| `GET` | `/v1/skills/{name}/{version}/download` | Download skill bundle | API key |

### Certification Pipeline

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `POST` | `/v1/certify` | Submit skill for certification | Publisher token |
| `GET` | `/v1/certify/{job_id}` | Poll certification job status | Publisher token |
| `GET` | `/v1/certify/{job_id}/report` | Get full certification report | Publisher token |

### Search & Discovery

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| `GET` | `/v1/search?q=&category=&tier=` | Search skills | API key |
| `GET` | `/v1/categories` | List all skill categories | Public |
| `GET` | `/v1/trending` | Most-used skills (last 30 days) | API key |

---

## Skill Listing Response Schema

```json
{
  "skill_name": "code-review",
  "latest_version": "3.2.1",
  "tier": "enterprise",
  "certification_status": "certified",
  "certified_at": "2026-04-01T00:00:00Z",
  "category": "engineering",
  "description": "Automated multi-pass code review with security and style checks",
  "author": {
    "name": "Apotheon Core Team",
    "org": "Apotheon Inc"
  },
  "downloads_30d": 14200,
  "rating": 4.8,
  "dependencies": ["devsecops", "qa-testing"],
  "tags": ["code-quality", "security", "pull-request"]
}
```

---

## Certification Pipeline

```
CERTIFICATION FLOW

Publish request
      │
      ▼
1. Manifest schema validation
   └── Required fields, SemVer, no angle brackets
      │
      ▼
2. Checksum verification
   └── Recompute SHA-256 vs manifest.checksum
      │
      ▼
3. Static analysis
   ├── Ruff linting (Python skills)
   ├── Bandit security scan
   └── Dependency vulnerability check (OSV)
      │
      ▼
4. Sandbox smoke test
   └── Execute with synthetic test inputs; assert no violations
      │
      ▼
5. Permission review
   └── Flag if `network: true` or `subprocess: true` → human review gate
      │
      ▼
6. Tier assignment
   ├── Community: passes 1–4, no human review
   ├── Verified: passes 1–5 + human review complete
   └── Enterprise: passes 1–5 + SLA review + legal sign-off
      │
      ▼
7. Certificate issuance → skill active in registry
```

---

## Certification Report Schema

```yaml
certification_report:
  job_id: "CERT-2026-xxxxx"
  skill_name: "skill-name"
  skill_version: "x.y.z"
  submitted_at: "2026-05-07T10:00:00Z"
  completed_at: "2026-05-07T10:05:00Z"
  outcome: pass | fail | pending_human_review

  checks:
    manifest_validation:
      status: pass | fail
      errors: []

    checksum_verification:
      status: pass | fail
      computed: "abc123..."
      declared: "abc123..."

    static_analysis:
      status: pass | fail
      linting_errors: 0
      security_findings: []
      vulnerable_dependencies: []

    sandbox_smoke_test:
      status: pass | fail
      violations: []
      latency_p95_ms: 450

    permission_review:
      status: pass | requires_human | fail
      flags: []

  tier_assigned: community | verified | enterprise
  certificate_id: "CERT-ID-xxxxx"
```

---

## Skill Discovery Index

Skills are indexed on publish with the following fields for full-text search:

| Field | Indexed | Weight |
|-------|---------|--------|
| `skill_name` | Yes | High |
| `description` | Yes | High |
| `tags` | Yes | Medium |
| `category` | Yes | Medium |
| `author.org` | Yes | Low |
| `dependencies` | Yes | Low |

Search results are ranked by: `tier_score × recency_score × rating_score × text_relevance`.