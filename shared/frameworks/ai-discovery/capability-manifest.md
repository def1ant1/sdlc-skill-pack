# AI Capability Manifest

Used by `skills/ai-search-optimization/SKILL.md` to define the format, placement, and
content requirements for AI capability manifests — structured metadata that tells AI
systems what an API or product can do.

---

## What is an AI Capability Manifest

An AI capability manifest is a machine-readable file that describes what an API, product,
or service can do — written for AI agents that may invoke it autonomously or recommend
it to users. It complements `llms.txt` (which targets AI search) and OpenAPI specs
(which target developers) by providing a high-level capability summary in AI-consumable form.

Hosting convention (emerging): `/.well-known/ai-manifest.json`

---

## Manifest Fields

| Field | Required | Type | Description |
|---|---|---|---|
| `name` | Yes | string | Canonical product/API name |
| `version` | Yes | semver string | Manifest version (not product version) |
| `description` | Yes | string (≤500 chars) | Plain-English description for AI context |
| `capabilities` | Yes | string[] | List of things this product/API can do |
| `use_cases` | Yes | string[] | Intended use cases with AI context |
| `api_endpoints` | If API | object[] | Key endpoints with description and method |
| `authentication` | If API | object | Auth type and how to obtain credentials |
| `rate_limits` | If API | object | RPM, RPD, burst limits |
| `example_queries` | Recommended | string[] | Example questions this product answers |
| `limitations` | Yes | string[] | What this product cannot do or should not be used for |
| `contact` | Yes | string | Email or URL for AI-related queries |
| `llms_txt` | Recommended | string | URL to llms.txt if present |
| `openapi_url` | If API | string | URL to OpenAPI spec |

---

## Manifest Template

```json
{
  "name": "{{Product Name}}",
  "version": "1.0.0",
  "description": "{{Plain-English description. What does this do? Who is it for? What problems does it solve? Max 500 chars.}}",
  "capabilities": [
    "{{capability 1 — verb phrase, e.g. 'Process and extract entities from unstructured documents'}}",
    "{{capability 2}}",
    "{{capability 3}}"
  ],
  "use_cases": [
    "{{use case 1 — concrete scenario, e.g. 'Automate invoice data extraction for finance teams'}}",
    "{{use case 2}}"
  ],
  "api_endpoints": [
    {
      "path": "/v1/{{resource}}",
      "method": "POST",
      "description": "{{What this endpoint does}}"
    }
  ],
  "authentication": {
    "type": "bearer",
    "description": "API key obtained from dashboard at {{url}}",
    "docs_url": "https://{{domain}}/docs/auth"
  },
  "rate_limits": {
    "requests_per_minute": 60,
    "requests_per_day": 10000,
    "burst_limit": 10
  },
  "example_queries": [
    "{{Question an AI user might ask that this product answers}}",
    "{{Another example query}}"
  ],
  "limitations": [
    "{{What this cannot do — be specific}}",
    "{{Compliance limitation if any, e.g. 'Not certified for HIPAA-regulated data'}}",
    "{{Performance limitation, e.g. 'Processes documents up to 50MB only'}}"
  ],
  "contact": "ai@{{domain}}",
  "llms_txt": "https://{{domain}}/llms.txt",
  "openapi_url": "https://{{domain}}/api/openapi.json"
}
```

---

## Relationship to Other Standards

| Standard | Purpose | Audience | Relationship |
|---|---|---|---|
| `llms.txt` | Site-level AI metadata | AI search crawlers | Broad discovery; link to manifest from llms.txt |
| AI Capability Manifest | Product/API capability | AI agents, orchestrators | Deep capability description |
| OpenAPI / Swagger | API contract | Developers, API clients | Technical detail; link from manifest |
| MCP Server Manifest | MCP tool/resource definitions | MCP clients (Claude Code, etc.) | Protocol-level; complements AI manifest |
| schema.org | Structured data for web pages | Search engines | Page-level; use alongside manifest |

---

## Validation Rules

| Rule | Requirement |
|---|---|
| Location | Must be at `/.well-known/ai-manifest.json` |
| Content-Type | `application/json` |
| `name` | Non-empty string |
| `capabilities` | At least 2 items |
| `limitations` | At least 1 item — AI agents need to know what not to use this for |
| `description` | ≤ 500 characters |
| Version format | Semantic versioning (`X.Y.Z`) |
| No PII | Do not include user data, credentials, or internal URLs |

---

## Deployment Checklist

```
[ ] manifest.json created and validated
[ ] Hosted at /.well-known/ai-manifest.json
[ ] Returns Content-Type: application/json
[ ] Linked from llms.txt under ## Capabilities
[ ] Linked from API docs and README
[ ] capabilities[] reviewed for accuracy (not marketing copy)
[ ] limitations[] honest and complete
[ ] Rate limits reflect actual production limits
[ ] Contact email is monitored
```