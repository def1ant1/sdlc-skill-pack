---
name: hr-case-management-support
description: Support workflow for hr case management support with mandatory human approval gates.
use_when:
  - Use when task intent directly matches this skill's domain and required outputs.
do_not_use_when:
  - Do not use when a specialized neighboring skill owns the request domain more precisely.
---

## Disclaimer

This skill is decision support only and does not provide legal, tax, payroll, or employment determinations.

## Integration

- Consumes canonical entities and survivorship outputs from `core/master-data-management`.
- Emits auditable recommendations requiring human reviewers before execution.
