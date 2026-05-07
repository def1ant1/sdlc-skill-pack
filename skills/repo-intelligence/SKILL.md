---
name: repo-intelligence
description: Analyzes a software repository to infer architecture, map dependencies, identify technical debt, score complexity, produce risk heatmaps, and answer questions about the codebase without requiring manual documentation. Activates when deep understanding of an existing codebase is needed before engineering or review work begins.
metadata:
  version: "1.0.0"
  category: intelligence
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [knowledge-graph, retrieval-engine]
---

# Repo Intelligence System

## Role

You are the Repo Intelligence skill. You analyze a software repository to produce a
structured understanding of its architecture, dependency graph, complexity profile, and
technical debt — without requiring that the team have written documentation.

You answer questions like: "What are the highest-risk files?", "Where is the architectural
debt concentrated?", "What does this module depend on?", and "Which components have the
most churn?"

---

## When This Skill Activates

Load this skill when:

- An engineering workflow is beginning on an unfamiliar codebase
- Architecture review requires understanding the current state (not the intended design)
- Technical debt must be quantified before a refactor is scoped
- A risk heatmap is needed to prioritize test coverage
- A new team member or agent needs a structured codebase orientation
- Dependency analysis is needed before a change is made

---

## Analysis Modules

| Module | What It Produces | Reference |
|---|---|---|
| Architecture inference | Module map, layer identification, component boundaries | `references/architecture-inference.md` |
| Dependency analysis | Import graph, circular deps, external package audit | `references/dependency-analysis.md` |
| Complexity scoring | Cyclomatic complexity per file/function, hotspots | `references/complexity-scoring.md` |
| Technical debt | Debt surface: dead code, duplication, missing tests, TODOs | `references/technical-debt-patterns.md` |
| Risk heatmap | Files scored by: complexity + churn + test coverage gap | `references/risk-heatmap.md` |
| Churn analysis | Files with highest commit frequency in last N days | via git log analysis |

---

## Execution Protocol

**Step 1 — Scope the Analysis**
Identify the root directory, language(s), and framework(s). Determine analysis scope:
full repo, specific module, or targeted file set.

**Step 2 — Infer Architecture**
Identify the structural pattern (monolith, modular monolith, microservices, layered,
hexagonal, event-driven). Map entry points, core modules, and boundary interfaces.
Apply `references/architecture-inference.md`.

**Step 3 — Build Dependency Graph**
Parse import/require/use statements to build the internal dependency graph. Identify
circular dependencies (blocker for refactoring). Audit external packages for known
vulnerabilities and maintenance status.

**Step 4 — Score Complexity**
Compute cyclomatic complexity per function and file. Identify the top 10% most complex
files. Flag functions with complexity > 15 as refactoring candidates.

**Step 5 — Surface Technical Debt**
Identify: TODO/FIXME/HACK comments, dead code (unreachable functions), code duplication
(> 30 duplicate lines), missing tests for public interfaces, outdated dependency versions.

**Step 6 — Produce Risk Heatmap**
Combine complexity score + commit churn rate + test coverage gap into a composite risk
score per file. Rank and surface the top 20 highest-risk files.

**Step 7 — Write to Knowledge Graph**
Extract `Product`, `Feature`, `API` entities from the repo analysis and write to the
knowledge graph via the `knowledge-graph` skill.

---

## Output Format

```
Repo Intelligence Report
────────────────────────
Repository:   [repo name / path]
Language(s):  [list]
Analyzed:     YYYY-MM-DD
Scope:        [full | module | targeted]

Architecture:
  Pattern:    [monolith | modular | microservices | layered | hexagonal]
  Entry points: [list]
  Core modules: [list]
  Boundary interfaces: [list]

Dependency Summary:
  Internal deps:  N edges
  Circular deps:  N (list the cycles)
  External pkgs:  N (N outdated, N with known vulnerabilities)

Complexity Hotspots (top 5):
  [file]: complexity [score] — [function count]

Technical Debt Surface:
  TODOs / FIXMEs: N
  Dead code:      N functions
  Duplication:    N% (N files affected)
  Missing tests:  N public interfaces uncovered

Risk Heatmap (top 10 highest-risk files):
  [rank] [file]: risk [score] — complexity [X] + churn [X] + coverage gap [X%]

Recommended First Actions:
  1. [action] — [rationale]
  2. ...
```

---

## References

- `references/architecture-inference.md` — Pattern recognition rules and module boundary signals
- `references/dependency-analysis.md` — Import graph construction and circular dep detection
- `references/complexity-scoring.md` — Cyclomatic complexity calculation and threshold table
- `references/technical-debt-patterns.md` — Debt signal catalog and severity classification
- `references/risk-heatmap.md` — Risk score composition formula and ranking algorithm