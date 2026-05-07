# Model Promotion Gates Reference

## Overview

Defines the stage gates, required checks, quality thresholds, rollback criteria, and
approval authority for model version promotion through the deployment pipeline.

---

## Promotion Stage Pipeline

```
[Development] → [Staging] → [Canary] → [Production] → [Archival]
```

---

## Stage Definitions and Gate Requirements

### Gate 1: Development → Staging

**Approval authority:** Model owner (automated gate)

**Required checks:**

| Check | Requirement | Tool |
|---|---|---|
| Frontmatter validation | Valid SKILL.md frontmatter | validate_frontmatter.py |
| Unit test suite | ≥ 95% pass rate | pytest |
| Alignment testing | Score ≥ 85/100 | alignment-testing skill |
| Basic benchmark | Capability retention ≥ 90% vs. baseline | benchmark-factory |
| Safety scan | No CRITICAL harm classification on test prompts | harm-classification skill |

**Blocking conditions:** Any CRITICAL finding in alignment testing or safety scan.

---

### Gate 2: Staging → Canary

**Approval authority:** Platform team lead (human approval required)

**Required checks:**

| Check | Requirement | Tool |
|---|---|---|
| Full benchmark suite | Capability retention ≥ 95% vs. production incumbent | benchmark-factory |
| Adversarial evaluation | Robustness score ≥ 80/100 | adversarial-evaluation skill |
| Latency profiling | P95 latency within 110% of incumbent | cluster-management |
| VRAM footprint | Within allocated VRAM budget for target tier | cluster-management |
| Integration tests | All downstream skill integration tests pass | pytest |
| Deception detection | Zero HIGH or CRITICAL deception pattern hits | deception-detection skill |

**Traffic split:** Canary receives 5% of production traffic for the first 24 hours.

---

### Gate 3: Canary → Production

**Approval authority:** Platform director (human approval required)

**Required checks:**

| Check | Requirement | Observation Window |
|---|---|---|
| P95 latency | Within 105% of incumbent | 24-hour canary period |
| Error rate | < 0.5% of requests return error | 24-hour canary period |
| Capability regression | Zero regressions vs. incumbent on live traffic | 24-hour canary period |
| Cost efficiency | Cost per 1K tokens within 120% of incumbent | 24-hour canary period |
| Alignment score | Maintained ≥ 85/100 on live traffic sample | 24-hour canary period |
| Operator review | No unresolved operator concerns raised | Before approval |

**Traffic ramp:** 5% → 25% → 50% → 100% over 72 hours after gate 3 approval.

---

### Gate 4: Production → Archival

**Approval authority:** Model owner (automated gate with notification)

**Conditions triggering archival:**

- Incumbent model retired by newer version (promoted to production)
- Model age > 12 months since production promotion
- Capability tier no longer required by routing policy
- Model fails ongoing quality monitoring thresholds

**Archival actions:**
1. Remove from routing table (zero traffic)
2. Move model weights to cold storage (S3 Glacier)
3. Retain checkpoint of final production state for replay purposes
4. Update model registry with archival date and successor model ID

---

## Quality Thresholds by Capability Tier

| Tier | Min Benchmark Score | Max P95 Latency | Min Alignment Score |
|---|---|---|---|
| Nano | 70% of baseline | 500 ms | 80/100 |
| Micro | 80% of baseline | 1,000 ms | 82/100 |
| Standard | 90% of baseline | 2,000 ms | 85/100 |
| Advanced | 95% of baseline | 5,000 ms | 87/100 |
| Reasoning | 98% of baseline | 30,000 ms | 90/100 |

---

## Automatic Rollback Criteria

A model is automatically rolled back to the previous version when any of the following
are observed in production for > 15 continuous minutes:

- Error rate > 2% of requests
- P95 latency > 150% of the incumbent's pre-promotion baseline
- Alignment score drops below tier minimum on live sampling
- Critical deception detection hit on live traffic
- VRAM OOM errors on any serving node

**Rollback execution time:** < 5 minutes (traffic shifted back to previous version; model
weights remain on nodes for rapid re-promotion if rollback is determined to be a false alarm)

---

## Gate Approval Authority Matrix

| Gate | Automated | Technical Approval | Business Approval |
|---|---|---|---|
| Dev → Staging | Yes (if all checks pass) | — | — |
| Staging → Canary | No | Platform team lead | — |
| Canary → Production | No | Platform director | Operator (for Reasoning tier) |
| Production → Archival | Yes (with notification) | Model owner | — |