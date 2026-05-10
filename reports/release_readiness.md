# Release Readiness

- Generated at (UTC): **2026-05-10T20:43:18.219148+00:00**
- Ready for release: **NO**

## Criteria
- ❌ `p0_failures_must_equal_zero`
- ❌ `critical_hitl_100`
- ❌ `high_risk_hitl_gte_95`
- ❌ `p0_maturity_gte_4`
- ❌ `no_unresolved_p0_p1_routing_collisions`
- ❌ `no_unresolved_p0_p1_routing_cycles`

## Checks
- ❌ **Contracts** (`/root/.pyenv/versions/3.12.13/bin/python scripts/validate_skill_contracts.py`)
- ❌ **Context budget** (`/root/.pyenv/versions/3.12.13/bin/python scripts/check_context_budget.py`)
- ✅ **Eval and telemetry coverage** (`/root/.pyenv/versions/3.12.13/bin/python scripts/validate_skill_evals.py`)
- ❌ **HITL coverage** (`/root/.pyenv/versions/3.12.13/bin/python scripts/validate_hitl_coverage.py`)
- ✅ **Backlog staleness** (`/root/.pyenv/versions/3.12.13/bin/python scripts/check_work_tasks_snapshot_freshness.py`)
- ❌ **Report freshness** (`/root/.pyenv/versions/3.12.13/bin/python scripts/docs/enforce_doc_freshness.py`)
- ❌ **Secret scan** (`/root/.pyenv/versions/3.12.13/bin/python scripts/security/scan_for_secrets.py`)
- ❌ **Policy coverage** (`/root/.pyenv/versions/3.12.13/bin/python scripts/validate_backlog_truth.py`)
- ✅ **Maturity thresholds** (`/root/.pyenv/versions/3.12.13/bin/python scripts/grade_skill_maturity.py`)
- ✅ **README claim verification** (`/root/.pyenv/versions/3.12.13/bin/python scripts/docs/validate_readme_claims.py`)
- ✅ **Routing collisions/cycles** (`/root/.pyenv/versions/3.12.13/bin/python scripts/detect_skill_overlap.py`)

## Failure Reasons
- P0 gate failures present: context_budget, contracts, hitl, policy_coverage, report_freshness, secret_scan
- critical HITL coverage must be 100% (actual: 0.0)
- high-risk HITL coverage must be >=95% (actual: 0.0)
- P0 maturity min level must be >=4 (actual: None)
- unresolved routing collisions: 20456
- unresolved routing cycles: 17
