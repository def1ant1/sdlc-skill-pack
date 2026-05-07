# Canonical Artifact Formats

## Overview

All artifacts exchanged through MCP integrations use these canonical formats.
External connector outputs are normalized to these formats before entering the platform.

---

## Text Artifact

```json
{
  "type": "text",
  "id": "<artifact-id>",
  "source": "<connector or skill>",
  "created_at": "ISO8601",
  "content": "<text content>",
  "format": "plain | markdown | html | code",
  "language": "<programming language if code>",
  "encoding": "utf-8",
  "metadata": {}
}
```

---

## Document Artifact

```json
{
  "type": "document",
  "id": "<artifact-id>",
  "source": "<connector>",
  "created_at": "ISO8601",
  "title": "<document title>",
  "content": "<extracted text>",
  "format": "pdf | docx | markdown | html",
  "url": "<original URL if applicable>",
  "author": "<author if known>",
  "published_at": "ISO8601",
  "page_count": N,
  "word_count": N,
  "metadata": {}
}
```

---

## Data Artifact (Structured)

```json
{
  "type": "data",
  "id": "<artifact-id>",
  "source": "<connector>",
  "created_at": "ISO8601",
  "schema": "<schema name>",
  "records": [
    { "<field>": "<value>", ... }
  ],
  "record_count": N,
  "format": "jsonl | csv | parquet",
  "metadata": {}
}
```

---

## Code Artifact

```json
{
  "type": "code",
  "id": "<artifact-id>",
  "source": "<connector or skill>",
  "created_at": "ISO8601",
  "language": "python | go | typescript | sql | bash",
  "content": "<code text>",
  "filename": "<suggested filename>",
  "description": "<what this code does>",
  "is_runnable": true,
  "dependencies": ["<dep>"],
  "metadata": {}
}
```

---

## Search Result Artifact

```json
{
  "type": "search_results",
  "id": "<artifact-id>",
  "source": "<connector>",
  "created_at": "ISO8601",
  "query": "<original query>",
  "results": [
    {
      "rank": 1,
      "title": "<result title>",
      "url": "<result URL>",
      "snippet": "<relevant excerpt>",
      "score": 0.0,
      "published_at": "ISO8601"
    }
  ],
  "total_results": N,
  "metadata": {}
}
```

---

## Event Artifact

```json
{
  "type": "event",
  "id": "<artifact-id>",
  "source": "<connector or skill>",
  "event_type": "<event.name>",
  "occurred_at": "ISO8601",
  "entity_type": "<entity type>",
  "entity_id": "<entity id>",
  "payload": {},
  "correlation_id": "<correlation id>",
  "metadata": {}
}
```

---

## Normalization Rules

When receiving data from external connectors (CV-001 through CV-011):

1. **Always assign an artifact ID** (UUID4) if not provided by the source
2. **Normalize timestamps** to ISO 8601 UTC
3. **Sanitize content**: remove executable scripts, active content; keep plain text/markdown
4. **Validate schema**: reject artifacts missing required fields; log validation errors
5. **Enforce size limits**: text content ≤ 1MB; data artifacts ≤ 10MB; reject larger with explanation
6. **Strip PII from metadata**: do not propagate external user IDs or email addresses in metadata fields