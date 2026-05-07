# Technical Debt Patterns

## Debt Classification

Technical debt is classified by type and priority. All debt items are tracked as
backlog tickets with estimated remediation cost.

| Type | Description | Priority Driver |
|---|---|---|
| Reliability debt | Code that causes or risks production incidents | Incident history |
| Security debt | Vulnerabilities or insecure patterns | CVE severity |
| Complexity debt | Code too complex to safely maintain | CC score |
| Test debt | Insufficient coverage on critical paths | Coverage gap × criticality |
| Documentation debt | Missing or stale docs/comments/ADRs | Usage frequency |
| Architecture debt | Violations of layering, coupling, or design principles | Change frequency |
| Dependency debt | Outdated or risky dependencies | Risk score |

---

## Detection Patterns

### Pattern: God Object / God Function

**Signal**: A class > 500 LOC or a function > 100 LOC handling unrelated concerns.

**Detection**: File LOC scan + function LOC scan.

**Risk**: High change frequency, all bugs traced here, hard to test in isolation.

**Remediation**: Extract single-responsibility classes; apply SRP.

---

### Pattern: Primitive Obsession

**Signal**: Business concepts represented as primitive types (strings, ints) instead
of domain objects.

**Detection**: Functions accepting many primitive parameters for the same concept.

**Risk**: Easy to pass arguments in wrong order; no validation at type boundary.

**Remediation**: Create value objects (e.g., `AccountID`, `EmailAddress`).

---

### Pattern: Shotgun Surgery

**Signal**: A single change requires modifications to N > 5 different files.

**Detection**: Track PR diffs for change locality. Flag when a single feature touches
> 7 files outside a refactoring PR.

**Risk**: Changes are fragile; high risk of missed updates causing bugs.

**Remediation**: Consolidate related code; reduce coupling between modules.

---

### Pattern: Feature Envy

**Signal**: A method accesses data from another class more than its own class.

**Detection**: Static analysis tools (e.g., ArchUnit, SonarQube).

**Risk**: Wrong responsibility placement; changes to the envied class ripple everywhere.

**Remediation**: Move the method to the class it envies, or introduce a service.

---

### Pattern: Copy-Paste Duplication

**Signal**: Similar code blocks (> 10 lines, > 80% identical) appearing in multiple places.

**Detection**: Code duplication tools (e.g., `jscpd`, `sonar-duplication`).

**Risk**: Bug fixed in one copy but not others; divergence over time.

**Remediation**: Extract shared function or module; apply DRY.

---

### Pattern: Stringly Typed API

**Signal**: Functions using strings where a type-safe enum or constant would prevent bugs.

**Detection**: Functions with string parameters for categorical values; no compile-time validation.

**Risk**: Typos cause runtime failures; no IDE assistance.

**Remediation**: Replace with enums, typed constants, or sum types.

---

## Debt Prioritization Formula

```
debt_priority_score = (impact × likelihood × change_frequency) / remediation_cost

Where:
  impact:           1–5 (production risk if debt causes failure)
  likelihood:       1–5 (probability of this debt causing a bug in next 3 months)
  change_frequency: 1–5 (how often this code is modified)
  remediation_cost: 1–5 (effort to fix; 1 = trivial, 5 = large refactor)

Score > 10: P1 — fix in current sprint
Score 5–10: P2 — fix in next sprint
Score < 5:  P3 — backlog
```

---

## Technical Debt Ledger Format

```yaml
debt_item:
  id: "TD-YYYYMMDD-NNN"
  type: "reliability | security | complexity | test | documentation | architecture | dependency"
  title: "<description of the debt>"
  file: "<file path>"
  location: "<function or class name>"
  pattern: "<debt pattern name>"
  impact: 1–5
  likelihood: 1–5
  change_frequency: 1–5
  remediation_cost: 1–5
  priority_score: X.X
  priority: "P1 | P2 | P3"
  owner: "<team>"
  created_at: "YYYY-MM-DD"
  target_sprint: "<sprint id>"
  resolved_at: "YYYY-MM-DD"
  status: "open | in-progress | resolved | accepted"
```