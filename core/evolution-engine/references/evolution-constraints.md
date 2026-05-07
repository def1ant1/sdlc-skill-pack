# Evolution Constraints

## Overview

The `evolution-engine` may only make changes that fall within the boundaries defined here.
These constraints protect the integrity of the OS while enabling meaningful self-improvement.

---

## Scope Boundaries

### Autonomous (Level 0 — No Approval Required)

The evolution-engine may apply these changes without operator review:

- Add or update content in existing `references/` markdown files
- Fix broken references listed in a skill's References section (file does not exist)
- Update `description` field in frontmatter if it is a stub (contains "TODO")
- Increment `metadata.version` patch version after a validated improvement
- Add documentation to an existing SKILL.md's Output Format section if empty
- Create a new `references/` subdirectory for an existing skill

### Operator Review Required (Level 2)

The following require operator approval via hitl-dashboard before execution:

- Create a new skill (new directory + SKILL.md) in `skills/` or `core/`
- Modify the Execution Protocol section of any existing SKILL.md
- Change `metadata.dependencies` in any SKILL.md
- Change `metadata.category` or `metadata.maturity` in any SKILL.md
- Modify shared standards, policies, or ontologies in `shared/`
- Create or modify any Python script in `scripts/`

### Always Requires Human Decision (Level 4)

- Delete any existing SKILL.md, reference file, or script
- Change `metadata.name` in any SKILL.md (breaks references)
- Modify `scripts/validation/` validation logic
- Modify CI pipeline configuration (`.github/workflows/`)
- Modify constitutional rules in `alignment-engine/references/`

---

## Rollback Criteria

Every evolution-engine change must be reversible. A change is rolled back if:

| Condition | Rollback Trigger |
|---|---|
| Validation fails post-change | Automatic rollback within 60 seconds |
| Gap detector reports new gaps introduced | Automatic rollback |
| Frontmatter parse error introduced | Automatic rollback |
| Operator rejects change within 24h | Manual rollback via hitl-dashboard |
| Quality metric decreases >5% in 7 days | Recommended rollback (operator decision) |

All changes are written as git commits on a `experimental/evolution-YYYYMMDD-NNN` branch.
No changes are merged to `develop` or `main` without the applicable approval level.

---

## Approval Routing

```
Evolution proposal generated
│
├── Level 0 (auto-apply)
│   ├── Apply change immediately
│   ├── Run validate_skill_structure.py + validate_frontmatter.py
│   ├── If validation passes: commit to experimental branch
│   └── If validation fails: roll back + log failure
│
└── Level 2 (operator review)
    ├── Submit proposal to hitl-dashboard
    ├── Proposal includes: proposed change, rationale, expected quality delta, rollback plan
    ├── Operator decides: approve / reject / modify scope
    └── On approval: apply + validate + commit to experimental branch
```

---

## Evolution Proposal Format

```yaml
evolution_proposal:
  id: "EVO-YYYYMMDD-NNN"
  generated_by: evolution-engine
  generated_at: "ISO8601"
  opportunity_rank: N
  opportunity_source: "skill-gap-engine"
  gap_id: "GAP-YYYYMMDD-NNN"
  gap_severity: "P0 | P1 | P2 | P3"

  proposed_change:
    type: "new_skill | skill_improvement | reference_addition | stub_completion"
    target_path: "skills/example/SKILL.md"
    description: "<what change is proposed>"
    rationale: "<why this improves the platform>"

  approval_level: 0 | 2 | 4
  expected_quality_delta: +X.X  # points on 0-100 rubric

  rollback_plan:
    reversible: true
    rollback_method: "git revert <commit-sha>"
    rollback_time_estimate: "< 30 seconds"

  status: "proposed | approved | rejected | applied | rolled_back"
  operator_decision: "approved | rejected | modified"
  applied_at: "ISO8601"
  validation_result: "passed | failed"
```