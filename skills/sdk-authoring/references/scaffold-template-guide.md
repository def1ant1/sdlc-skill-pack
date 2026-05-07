# SDK Authoring — Scaffold Template Guide

## Scaffold Generator Usage

```bash
# Generate a new skill scaffold
python scripts/generators/create_skill.py <skill-name> \
  --category <category> \
  --description "<one-line description>" \
  --tier community
```

---

## Generated Directory Layout

```
skills/<skill-name>/
├── SKILL.md                  # Behavioral contract (frontmatter + instructions)
├── manifest.yaml             # SDK manifest (permissions, quotas, checksum)
├── skill.py                  # Entrypoint handler
├── tests/
│   └── test_skill.py         # Pytest unit tests
└── references/
    └── <reference-doc>.md    # Domain reference material
```

---

## SKILL.md Frontmatter Template

```yaml
---
name: <skill-name>
description: <one-line description, max 1024 chars, no angle brackets>
metadata:
  version: "0.1.0"
  category: <category>
  owner: <team-or-agent>
  maturity: alpha
  dependencies: []
---
```

---

## manifest.yaml Template

```yaml
sdk_manifest:
  manifest_version: "1.0"
  skill_name: <skill-name>
  skill_version: "0.1.0"
  runtime_api_version: "2026-05"

  entrypoint:
    handler: "skill.main:handle"
    timeout_seconds: 30
    memory_limit_mb: 512

  permissions:
    network: false
    filesystem: none
    subprocess: false
    secrets: []

  resource_quotas:
    max_tokens_per_call: 8192
    max_calls_per_minute: 60
    max_concurrent_executions: 4
    max_storage_mb: 100

  dependencies:
    skills: []
    external_apis: []
    models: []

  checksum:
    algorithm: sha256
    value: ""   # Filled in by `scripts/publish/compute_checksum.py`

  author:
    name: ""
    org: ""
    contact: ""

  certification:
    status: pending
    certified_at: null
    certified_by: null
    tier: community
```

---

## skill.py Entrypoint Template

```python
"""
<Skill Name> — SDK Skill Entrypoint

This module implements the skill handler called by the SDK Runtime.
"""
from __future__ import annotations
from typing import Any


def handle(request: dict[str, Any]) -> dict[str, Any]:
    """
    Main entrypoint. Called by SDK Runtime for each invocation.

    Args:
        request: Validated input dict. Keys defined in SKILL.md input schema.

    Returns:
        Output dict. Keys defined in SKILL.md output schema.
    """
    objective = request.get("objective", "")

    # TODO: implement skill logic here

    return {
        "status": "success",
        "result": f"Processed: {objective}",
    }
```

---

## test_skill.py Template

```python
"""Tests for <skill-name>."""
import pytest
from skill.main import handle


def test_handle_basic():
    response = handle({"objective": "test input"})
    assert response["status"] == "success"
    assert "result" in response


def test_handle_empty_objective():
    response = handle({"objective": ""})
    assert response["status"] == "success"


def test_handle_missing_objective():
    response = handle({})
    assert response["status"] == "success"
```

---

## Skill Maturity Ladder

| Maturity | Criteria | Tier Eligible |
|----------|---------|--------------|
| `alpha` | Scaffold only; minimal tests | Community |
| `beta` | Functional; >80% test coverage; no critical linting errors | Community |
| `stable` | Production-tested; full reference docs; peer-reviewed | Verified |
| `enterprise` | SLA guarantees; legal review; audit log integration | Enterprise |

---

## Common Authoring Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| Angle brackets (`<>`) in frontmatter | CI fails `validate_frontmatter.py` | Use plain text placeholders |
| Non-kebab-case skill name | CI fails `validate_skill_structure.py` | Rename directory and `name` field |
| Missing `checksum.value` before publish | Certification gate fails | Run `compute_checksum.py` |
| `network: true` without justification | Human review required | Add `external_apis` list in manifest |
| Handler not at declared entrypoint path | Sandbox spawn fails | Match `handler` in manifest to actual module path |

---

## Publishing Checklist

```
□ SKILL.md frontmatter validates (name, description, no angle brackets)
□ manifest.yaml checksum computed and filled
□ All tests pass (pytest)
□ Ruff linting clean (0 errors)
□ References directory has at least one .md document
□ Maturity updated from alpha to at minimum beta
□ Author fields populated in manifest
□ `create_skill.py` was used to scaffold (not hand-written from scratch)
```