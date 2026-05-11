# APOTHEON AI COMPANY OS — RC1 RELEASE FINALIZATION BACKLOG

**Target tag:** `v0.9.0-rc1`  
**Promotion target:** `v1.0.0` only after all P0 gates are green  
**Status:** RELEASE-CLOSEOUT PLAN  
**Owner:** Apotheon.ai  
**Purpose:** Track the remaining release-critical work needed to finalize the project for an RC1 release and define the exact gates required before promotion to v1.0.0.

---

## 0. Current Reanalysis Summary

Repository search found the V9 validation foundation already exists, including skill contract validation, backlog truth validation, context budget checks, inventory generation, dependency graph generation, overlap detection, skill eval validation, telemetry validation, CI workflow integration, and pre-merge checks.

The remaining release-critical gap is now the final release layer:

1. One aggregated readiness gate.
2. Deterministic release packaging.
3. Version/changelog/release-note discipline.
4. Dry-run release smoke tests.
5. Business workflow planner coverage.
6. Governance boundary documentation.
7. Continuous documentation freshness and anti-duplication enforcement.

Search did not find closeout artifacts named:

```text
scripts/validate_release_readiness.py
scripts/package_release.py
scripts/smoke_test_release.py
scripts/orchestration/plan_business_workflow.py
VERSION
CHANGELOG.md
RELEASE_NOTES.md
docs/governance/professional-advice-boundaries.md
docs/governance/data-scraping-policy.md
docs/governance/external-action-policy.md
```

Therefore this backlog treats them as open until proven otherwise by repo filesystem validation.

---

## 1. Release Policy

### RC1 release posture

The next release should be tagged:

```text
v0.9.0-rc1
```

This is appropriate because the platform is feature-rich and CI-heavy, but final release-readiness aggregation, packaging, versioning, smoke tests, business workflow routing, and governance boundary docs are still being finalized.

### v1.0.0 promotion rule

Do not tag `v1.0.0` until:

- All P0 RC1 tasks below are complete.
- `python scripts/validate_release_readiness.py --release-version v1.0.0` passes.
- All generated release reports are committed and stable.
- Release smoke tests pass from a clean checkout.
- Release package checksum is generated and verified.
- README/version/changelog/release notes are internally consistent.
- No stale top-level backlog or task files contradict the generated release reports.

---

# P0-A — Single Release Readiness Gate Aggregator

## Task A1 — Create validate_release_readiness gate and machine-readable readiness outputs

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
scripts/validate_release_readiness.py
reports/release_readiness.md
reports/release_readiness.json
schemas/release-readiness.schema.json
```

## Requirements

`validate_release_readiness.py` must aggregate and execute, or consume outputs from, all release-critical checks:

```bash
python scripts/validation/validate_skill_structure.py .
python scripts/validation/validate_frontmatter.py .
python scripts/orchestration/detect_skill_gaps.py .
python scripts/validate_backlog_truth.py
python scripts/validate_skill_contracts.py
python scripts/check_context_budget.py
python scripts/generate_skill_inventory.py
python scripts/generate_dependency_graph.py
python scripts/detect_skill_overlap.py
python scripts/validate_skill_evals.py
python scripts/validate_telemetry_events.py
python scripts/docs/validate_doc_uniqueness.py
python scripts/docs/check_backlog_changelog_sync.py
python scripts/docs/enforce_doc_freshness.py
python scripts/security/scan_for_secrets.py --path . --exit-on-finding
pytest --tb=short -q
```

It must also verify:

- `VERSION` exists and matches the requested release version.
- `CHANGELOG.md` contains the requested release version.
- `RELEASE_NOTES.md` exists or is generated for the requested release version.
- `reports/` files are current and would not change after regeneration.
- `README.md` release/version/count claims are either generated or match report outputs.
- No top-level backlog/task file says release-critical work is missing while readiness claims pass.
- Required release package files exist if `--require-package` is passed.

## Output schema

`reports/release_readiness.json` must include:

```json
{
  "release_version": "v0.9.0-rc1",
  "commit_sha": "...",
  "generated_at": "...",
  "overall_status": "pass|fail|warning",
  "p0_failures": [],
  "p1_warnings": [],
  "checks": [
    {
      "name": "validate_skill_contracts",
      "status": "pass|fail|warning|skipped",
      "command": "python scripts/validate_skill_contracts.py",
      "duration_ms": 0,
      "summary": "..."
    }
  ],
  "release_blockers": [],
  "promotion_recommendation": "rc_only|v1_ready"
}
```

## Acceptance Criteria

- Running `python scripts/validate_release_readiness.py --release-version v0.9.0-rc1` produces both markdown and JSON reports.
- The command exits nonzero on any P0 release blocker.
- JSON validates against `schemas/release-readiness.schema.json`.
- CI invokes this script after existing V9 gates.
- `scripts/run_premerge_checks.py` either invokes this script or clearly delegates to it as the final gate.

---

# P0-B — Release Artifact Packaging

## Task B1 — Add deterministic release packaging with checksum and exclusion rules

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
scripts/package_release.py
docs/release/release-packaging.md
dist/.gitkeep
```

## Requirements

Create a deterministic release artifact:

```text
dist/apotheon-skill-pack-v0.9.0-rc1.zip
dist/apotheon-skill-pack-v0.9.0-rc1.sha256
dist/apotheon-skill-pack-v0.9.0-rc1.manifest.json
```

Included paths:

```text
core/
skills/
agents/
shared/
schemas/
references/
docs/
scripts/
tests/
reports/
README.md
VERSION
CHANGELOG.md
RELEASE_NOTES.md
pyproject.toml
```

Excluded paths:

```text
.git/
.github/
__pycache__/
.pytest_cache/
.ruff_cache/
.mypy_cache/
.env
.env.*
*.pem
*.key
*.crt
*.p12
*.sqlite
*.db
node_modules/
dist/*.zip
dist/*.sha256
local artifacts
secret or credential files
```

## Determinism requirements

- Files sorted lexicographically.
- Stable ZIP timestamps or normalized metadata.
- Stable compression settings.
- Manifest includes path, byte size, and SHA-256 per file.
- Re-running package command without code changes produces identical checksum.

## Acceptance Criteria

- `python scripts/package_release.py --version v0.9.0-rc1` creates zip, checksum, and manifest.
- `python scripts/package_release.py --version v0.9.0-rc1 --verify` verifies checksum and manifest.
- Secret scan runs before packaging.
- Package generation is integrated into release CI or release workflow.

---

# P0-C — Versioning, Changelog, and Release Notes Discipline

## Task C1 — Standardize release versioning, notes, and cross-file consistency checks

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
VERSION
CHANGELOG.md
RELEASE_NOTES.md
docs/release/release-process.md
scripts/validate_version_consistency.py
scripts/generate_release_notes.py
```

## Requirements

- `VERSION` contains exactly one semantic version or prerelease version, e.g. `v0.9.0-rc1`.
- `CHANGELOG.md` follows Keep a Changelog style.
- `RELEASE_NOTES.md` summarizes the release, known limitations, validation status, and upgrade/use instructions.
- README references the same version.
- Release readiness report references the same version.
- Packaging script uses the same version unless explicitly overridden.

## Acceptance Criteria

- `python scripts/validate_version_consistency.py --release-version v0.9.0-rc1` passes.
- The script fails if README, VERSION, CHANGELOG, RELEASE_NOTES, package manifest, or release readiness report disagree.
- `python scripts/generate_release_notes.py --version v0.9.0-rc1` can regenerate release notes deterministically from changelog and reports.
- CI includes version consistency validation.

---

# P0-D — Release Smoke Tests

## Task D1 — Add dry-run release smoke tests for planning/runtime/report integrity

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
scripts/smoke_test_release.py
tests/release/test_release_smoke.py
reports/release_smoke_test_report.md
reports/release_smoke_test_report.json
```

## Required smoke tests

Run from a clean checkout without external paid API calls by default:

1. Validate all schemas load.
2. Validate skill inventory loads.
3. Validate dependency graph loads.
4. Plan one SDLC workflow in dry-run mode.
5. Plan one GTM workflow in dry-run mode.
6. Plan one business workflow in dry-run mode.
7. Build a context packet for a representative skill.
8. Execute a local workflow dry run without calling external LLMs.
9. Verify generated reports exist and are parseable.
10. Verify package manifest, if present, is parseable.

## Acceptance Criteria

- `python scripts/smoke_test_release.py --dry-run` passes without requiring Anthropic/OpenAI/Slack/Salesforce/etc. credentials.
- Pytest release smoke tests call the same logic.
- Smoke report is generated in markdown and JSON.
- Release readiness aggregator includes smoke test status.

---

# P0-E — Business Workflow Planner Coverage

## Task E1 — Add business workflow planners for enterprise domain routing

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
scripts/orchestration/plan_business_workflow.py
scripts/orchestration/plan_finance_workflow.py
scripts/orchestration/plan_customer_workflow.py
scripts/orchestration/plan_inventory_workflow.py
tests/orchestration/test_plan_business_workflow.py
tests/orchestration/test_plan_finance_workflow.py
tests/orchestration/test_plan_customer_workflow.py
tests/orchestration/test_plan_inventory_workflow.py
docs/onboarding/BUSINESS_WORKFLOW_PLANNER_GUIDE.md
```

## Planner requirements

Each planner must:

- Accept a natural-language objective.
- Return deterministic JSON workflow plans.
- Use existing skill registry/inventory rather than hardcoded nonexistent skills.
- Include required HITL/governance metadata for risky actions.
- Support `--dry-run`.
- Support `--json`.
- Fail clearly when required skills are missing.

## Minimum routing coverage

`plan_business_workflow.py` must route objectives across:

- Finance/accounting
- Budgeting/forecasting
- Procurement/vendor
- Customer success/support
- Sales/revenue
- Marketing/GTM
- Inventory/product
- HR/people
- Legal/compliance
- Executive reporting

## Acceptance Criteria

- Each planner has tests for at least 5 representative objectives.
- Smoke test invokes business planner successfully.
- README quick start includes a business workflow example.
- Planner output conforms to existing workflow execution format.

---

# P0-F — Safety and Compliance Boundary Docs

## Task F1 — Publish governance boundary documents for professional advice and external actions

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
docs/governance/professional-advice-boundaries.md
docs/governance/data-scraping-policy.md
docs/governance/external-action-policy.md
docs/governance/financial-controls.md
docs/governance/hr-high-impact-decision-policy.md
docs/governance/customer-communication-policy.md
docs/governance/legal-tax-review-policy.md
```

## Required content

### Professional advice boundaries

Must state that finance, accounting, legal, tax, HR, medical, and compliance outputs are decision support only and require qualified human review where appropriate.

### Data scraping policy

Must cover:

- robots.txt
- terms of service
- rate limits
- no access control bypass
- source attribution
- timestamping
- observed vs inferred data separation
- privacy and PII handling

### External action policy

Must cover:

- email/customer communications
- CRM updates
- payment actions
- purchase orders
- payroll/HR changes
- deployment/security changes
- deletion/destructive actions
- approval thresholds

### Financial controls

Must cover:

- segregation of duties
- approval thresholds
- audit trail requirements
- payment authorization
- vendor changes
- journal entries
- month-end close controls

### HR high-impact decision policy

Must cover:

- no autonomous hiring/firing/promotion/compensation decisions
- bias review
- human review
- evidence and explanation requirements

## Acceptance Criteria

- Each policy is linked from README and relevant skill references.
- `validate_skill_contracts.py` or a governance validator verifies high-risk skills reference applicable policies.
- Release readiness aggregator fails if required governance docs are missing.

---

# P0-G — Continuous Documentation Freshness and No Duplication

## Task G1 — Enforce always-current backlog/changelog/docs with anti-duplication and freshness checks

**Priority:** P0  
**Status:** Open  
**Primary deliverables:**

```text
scripts/docs/validate_doc_uniqueness.py
scripts/docs/check_backlog_changelog_sync.py
scripts/docs/enforce_doc_freshness.py
scripts/docs/validate_readme_claims.py
reports/doc_freshness_report.md
reports/doc_freshness_report.json
.docs-freshness.yaml
```

Note: Some doc governance scripts may already exist. Codex must inspect current implementations and enhance rather than duplicate.

## Requirements

- Detect duplicate backlog files with overlapping active scope.
- Detect stale task files that contradict generated reports.
- Ensure `CHANGELOG.md` references completed release work.
- Ensure README claims match generated inventory/readiness reports.
- Ensure top-level docs identify current source of truth.
- Archive stale planning docs under `docs/archive/` or mark clearly as historical.
- Require regenerated docs/reports to be committed.

## Acceptance Criteria

- `python scripts/docs/validate_doc_uniqueness.py` passes.
- `python scripts/docs/check_backlog_changelog_sync.py` passes.
- `python scripts/docs/enforce_doc_freshness.py` passes.
- `python scripts/docs/validate_readme_claims.py` passes.
- Release readiness aggregator includes doc freshness status.
- `V9_OPEN_WORK_TASKS.md` is regenerated, reconciled, archived, or replaced so it no longer contradicts release readiness.

---

# 2. CI Integration Required

Update `.github/workflows/validate.yml` so release-closeout gates are explicit:

```bash
python scripts/validate_version_consistency.py --release-version $(cat VERSION)
python scripts/smoke_test_release.py --dry-run
python scripts/validate_release_readiness.py --release-version $(cat VERSION)
```

On release events, also run:

```bash
python scripts/package_release.py --version $(cat VERSION)
python scripts/package_release.py --version $(cat VERSION) --verify
```

Upload artifacts:

```text
reports/
dist/*.zip
dist/*.sha256
dist/*.manifest.json
```

---

# 3. Required README Updates

Update README after implementation:

- Add current version badge/text from `VERSION`.
- Add release readiness command.
- Add package command.
- Add business workflow planner quick start.
- Link governance boundary docs.
- Replace static counts with generated report references, or ensure counts are validated by `validate_readme_claims.py`.

---

# 4. Required Release Reports

Before tagging `v0.9.0-rc1`, generate and commit:

```text
reports/release_readiness.md
reports/release_readiness.json
reports/release_smoke_test_report.md
reports/release_smoke_test_report.json
reports/doc_freshness_report.md
reports/doc_freshness_report.json
reports/skill_inventory.md
reports/skill_inventory.json
reports/skill_dependency_graph.json
reports/orchestration_map.md
reports/routing_collision_report.md
```

---

# 5. RC1 Completion Checklist

```text
[ ] A1 release readiness aggregator implemented and passing
[ ] B1 deterministic package generation implemented and verified
[ ] C1 version/changelog/release notes consistency implemented and passing
[ ] D1 release smoke tests implemented and passing
[ ] E1 business workflow planners implemented and tested
[ ] F1 governance boundary docs published and linked
[ ] G1 doc freshness/no-duplication gates implemented and passing
[ ] CI updated with RC1 gates
[ ] README updated with release, package, business planner, and governance links
[ ] reports/ regenerated and committed
[ ] dist/ artifact generated and checksum verified for release event
[ ] tag `v0.9.0-rc1` only after all above pass
```

---

# 6. v1.0.0 Promotion Checklist

```text
[ ] `python scripts/validate_release_readiness.py --release-version v1.0.0` passes
[ ] No P0 failures in release readiness JSON
[ ] No stale active backlog/task docs
[ ] All P0 business workflow planner tests pass
[ ] All required governance boundary docs linked from high-risk skills
[ ] Release package checksum is deterministic across two builds
[ ] README claims match generated reports
[ ] HITL coverage for critical/high-risk skills meets configured threshold
[ ] RC1 feedback addressed or explicitly waived
[ ] CHANGELOG contains v1.0.0 entry
[ ] RELEASE_NOTES.md regenerated for v1.0.0
```
