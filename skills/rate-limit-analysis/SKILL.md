---
name: rate-limit-analysis
description: Analyzes connector quota pressure, throttling, and scheduler degradation posture.
version: 1.0.0
---

# Rate Limit Analysis

## Inputs
- Connector policy JSON documents conforming to `schemas/rate-limit-policy.schema.json`.
- Scheduler run metadata with connector IDs.

## Outputs
- Quota pressure classification per connector.
- Recommendations for cached or read-only degradation.
