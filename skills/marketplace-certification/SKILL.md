---
name: marketplace-certification
description: Certifies skills for marketplace release with strict prerequisite and
  governance gates.
metadata:
  version: 0.1.0
  category: governance
  owner: Apotheon.ai
  maturity: beta
use_when:
- Request clearly matches this skill's domain capabilities.
do_not_use_when:
- Request is outside this skill's domain or lacks required context.
---

# Marketplace Certification

## Certification Prerequisites

A candidate skill is certifiable only when all prerequisites pass:

1. Valid `manifest.v9.json` and schema-compliant skill metadata.
2. Evaluation suite passes the configured threshold.
3. Security, context, and telemetry checks pass.
4. No unresolved routing collisions remain in reports.

## Governance Hooks

Autonomous optimization recommendations **must not** mutate production state without
an explicit policy-defined approval decision and audit trail entry.

## Execution Steps

1. Load candidate skill path and manifest.
2. Execute prerequisite checks.
3. Record all failures with machine-readable reasons.
4. If all checks pass, emit certifiable status and governance conditions.
5. If mutation is requested, enforce policy approval gate before production change.
