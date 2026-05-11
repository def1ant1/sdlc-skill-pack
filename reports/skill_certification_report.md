# Skill Certification Report

## Repeatable certification criteria
- Manifest exists and parses as JSON.
- Eval/security/context/context-budget/telemetry checks pass.
- No unresolved routing collisions.

## Evidence outputs
- Skill: `demo-skill`
- Timestamp (UTC): `2026-05-11T21:19:34.782651+00:00`
- Status: `rejected`
- Reasons: `eval_failed, security_failed, context_failed, context_budget_failed, telemetry_failed`

```json
{
  "skill": "demo-skill",
  "status": "rejected",
  "reasons": [
    "eval_failed",
    "security_failed",
    "context_failed",
    "context_budget_failed",
    "telemetry_failed"
  ],
  "criteria": {
    "eval": false,
    "security": false,
    "context": false,
    "context_budget": false,
    "telemetry": false
  },
  "evidence": {
    "eval": "reports/skill_benchmark_results.json",
    "security": "reports/security_scan_report.md",
    "context": "reports/context_budget_report.md",
    "telemetry": "reports/ai_telemetry_replay.md"
  },
  "generated_at_utc": "2026-05-11T21:19:34.782651+00:00"
}
```
