# Gap Detection Rules

## Rule Categories

Gap detection runs on three axes: capability coverage, skill quality, and skill
currency. Each rule produces a gap record with type, severity, and recommended action.

---

## Axis 1 — Capability Coverage

### Rule COV-001: Missing Skill for Active Workflow Capability

**Trigger**: A workflow template references a capability ID from the capability ontology
that has no primary skill registered.

**Detection**:
```
for each workflow_template in workflow_engine.templates:
  for each step in workflow_template.steps:
    if step.capability_id not in skill_registry.capability_map:
      raise GAP(type=MISSING, severity=CRITICAL, capability=step.capability_id)
```

**Action**: Scaffold new skill immediately; block workflow execution until resolved.

---

### Rule COV-002: Missing Skill for Planned Capability

**Trigger**: A capability ID appears in the capability ontology but no skill covers it.

**Detection**:
```
for each capability in capability_ontology:
  if capability.id not in skill_registry.capability_map:
    raise GAP(type=MISSING, severity=HIGH, capability=capability.id)
```

**Action**: Create scaffolded skill stub; assign to next sprint.

---

### Rule COV-003: Single Point of Coverage (No Secondary)

**Trigger**: A high-usage capability has only one skill covering it (no secondary/fallback).

**Detection**:
```
for each capability in capability_ontology:
  if capability.workflow_usage_count > 5:
    if capability.secondary_skill is None:
      raise GAP(type=RESILIENCE, severity=MEDIUM, capability=capability.id)
```

**Action**: Identify or create a secondary skill; document fallback behavior.

---

## Axis 2 — Skill Quality

### Rule QUA-001: Skill Below Quality Floor

**Trigger**: A skill scores < 60 on the quality rubric.

**Detection**:
```
for each skill in skill_registry:
  score = evaluate_rubric(skill)
  if score < 60:
    raise GAP(type=WEAK, severity=HIGH if score < 40 else MEDIUM, skill=skill.name)
```

**Action**: Generate improvement plan; assign strengthening task to owning team.

---

### Rule QUA-002: Skill Below Target (Below 75)

**Trigger**: A skill scores 60–74 (adequate but below target).

**Detection**:
```
for each skill in skill_registry:
  score = evaluate_rubric(skill)
  if 60 <= score < 75:
    raise GAP(type=BELOW_TARGET, severity=LOW, skill=skill.name)
```

**Action**: Add to improvement backlog (P2); address in next sprint.

---

### Rule QUA-003: Invalid Frontmatter

**Trigger**: A SKILL.md file fails frontmatter validation.

**Detection**: Run `validate_frontmatter.py`; any file with validation errors.

**Action**: Auto-fix if possible; flag for immediate human review; block in CI.

---

### Rule QUA-004: Missing References Files

**Trigger**: A SKILL.md protocol references a file path (e.g., `references/foo.md`)
that does not exist on disk.

**Detection**:
```
for each skill in skill_registry:
  for each reference_path in skill.referenced_files:
    if not file_exists(reference_path):
      raise GAP(type=MISSING_REFERENCE, severity=MEDIUM, skill=skill.name, path=reference_path)
```

**Action**: Create stub reference file; assign completion to skill owner.

---

## Axis 3 — Skill Currency

### Rule CUR-001: Stale Skill (> 6 months, High Usage)

**Trigger**: A skill has not been updated in > 6 months AND has > 5 active workflow dependencies.

**Detection**:
```
for each skill in skill_registry:
  if skill.last_updated_days > 180 and skill.workflow_dependency_count > 5:
    raise GAP(type=STALE, severity=MEDIUM, skill=skill.name)
```

**Action**: Trigger quarterly review; assign to owning team.

---

### Rule CUR-002: Skill with Alpha Maturity in Critical Workflow

**Trigger**: A skill with maturity=alpha is the primary skill for a capability used in
more than 3 active workflows.

**Detection**:
```
for each skill in skill_registry:
  if skill.maturity == 'alpha' and skill.workflow_dependency_count > 3:
    raise GAP(type=MATURITY, severity=MEDIUM, skill=skill.name)
```

**Action**: Prioritize maturity promotion; conduct additional review and testing.

---

### Rule CUR-003: Deprecated Dependency

**Trigger**: A skill lists a deprecated skill in its dependencies.

**Detection**:
```
for each skill in skill_registry:
  for each dep in skill.dependencies:
    if dep in deprecated_skills:
      raise GAP(type=DEPENDENCY, severity=HIGH, skill=skill.name, dep=dep)
```

**Action**: Update dependency to current replacement; re-test integration.

---

## Gap Record Schema

```yaml
gap:
  id: "GAP-YYYYMMDD-NNN"
  rule: "COV-001"
  type: "MISSING | WEAK | BELOW_TARGET | STALE | MATURITY | RESILIENCE | MISSING_REFERENCE | DEPENDENCY"
  severity: "CRITICAL | HIGH | MEDIUM | LOW"
  skill: "<skill name or null>"
  capability: "<capability ID or null>"
  description: "<description of the gap>"
  detected_at: "ISO8601"
  workflow_impact: "<list of affected workflows>"
  recommended_action: "<what to do>"
  owner: "<team>"
  target_sprint: "<sprint ID>"
  status: "open | in-progress | resolved | accepted"
  resolved_at: "ISO8601"
```

---

## Detection Run Cadence

| Trigger | Axis | Scope |
|---|---|---|
| Every CI build | Standards compliance (QUA-003) | Changed files only |
| Weekly (Friday 06:00 UTC) | All axes | Full registry scan |
| On new workflow template added | Coverage (COV-001, COV-002) | New workflow capabilities |
| On new skill registered | Quality (QUA-001, QUA-002) | New skill only |
| Quarterly | Currency (CUR-001, CUR-002, CUR-003) | Full registry |