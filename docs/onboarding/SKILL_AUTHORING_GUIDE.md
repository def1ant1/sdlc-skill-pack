# Skill Authoring Guide

This guide covers everything needed to create, validate, and publish a new
Apotheon skill from scratch.

---

## Skill Types

| Type | Location | Purpose |
|---|---|---|
| **Domain skill** | `skills/<name>/` | Executes a specific SDLC task (code review, deployment, etc.) |
| **Core skill** | `core/<name>/` | Control-plane orchestration, memory, governance |
| **GTM skill** | `skills/<name>/` | Go-to-market and growth operations |

New skills almost always go under `skills/`. Only add to `core/` for infrastructure
that other skills depend on.

---

## Quickstart: Scaffold a New Skill

```bash
python scripts/generators/create_skill.py <skill-name>
```

This creates:
```
skills/<skill-name>/
├── SKILL.md              ← behavioral contract (edit this)
└── references/           ← supporting reference documents
```

Naming rules:
- Lowercase kebab-case only: `my-new-skill` not `MyNewSkill` or `my_new_skill`
- Descriptive and action-oriented: `code-review`, `threat-modeling`, `launch-planning`

---

## SKILL.md Structure

Every `SKILL.md` must open with valid YAML frontmatter followed by the behavioral contract.

### Frontmatter (required)

```yaml
---
name: my-skill-name
description: One-line description of what this skill does (max 1024 chars, no angle brackets)
metadata:
  version: "1.0.0"
  category: engineering          # engineering | security | gtm | analytics | governance
  owner: platform-team
  maturity: alpha                # alpha | beta | stable | deprecated
  dependencies:
    - other-skill-name           # skills this one depends on
---
```

Validation rules enforced by CI:
- `name` must match the directory name exactly
- `name` must be kebab-case
- `description` max 1024 characters
- No `<` or `>` characters anywhere in the frontmatter block

### Behavioral Contract (body)

The body is the system prompt used when the skill runs. Write it as detailed
instructions to the LLM. Structure:

```markdown
# <Skill Name>

## Role
One sentence describing what this skill agent is.

## Inputs
What context packet fields and objective text this skill expects.

## Outputs
What this skill produces (artifacts, decisions, recommendations).

## Execution Protocol
Step-by-step instructions for how the skill should behave:
1. Analyze the objective
2. Apply <domain> principles
3. Produce output in the required format

## Output Format
Specify the exact output format (JSON, YAML, markdown, etc.)

## HITL Gates
List any actions that require human approval before execution.

## Quality Standards
List the standards this skill must meet.
```

---

## Adding Reference Documents

Reference documents live in `skills/<name>/references/` and contain
domain-specific schemas, runbooks, templates, and specifications
that the skill can cite.

Naming: `<topic>-<type>.md` — e.g., `deployment-runbook.md`, `keyword-map.md`

The skill's body should reference these explicitly:
```markdown
## Reference Documents
- `references/deployment-runbook.md` — step-by-step deployment procedures
- `references/sizing-guide.md` — resource sizing recommendations
```

---

## HITL Gates

If your skill can take irreversible or high-blast-radius actions, add HITL gate
declarations to the frontmatter:

```yaml
hitl_gates:
  - trigger: "Production deployment initiated"
    level: 3
    condition: "environment == 'production'"
    rollback_plan_required: true
  - trigger: "External communication to >1000 recipients"
    level: 2
```

Gate levels:
- **Level 1** — Informational; 30-min veto window
- **Level 2** — Soft approval; 4h wait
- **Level 3** — Hard approval; blocks until approved

See `docs/governance/hitl-gate-audit.md` for the full gate specification.

---

## Dependencies

List skills that must execute before this one in the `dependencies` array.
The orchestration planner uses this to build the correct execution order.

Only list **direct** dependencies (not transitive). For example, if `code-review`
depends on `backend`, and `backend` depends on `architecture`, `code-review`
only lists `backend`.

Known aliases (not real skill directories) that can appear as dependencies:
- `gtm-orchestration` — the GTM planner script
- `sdlc-orchestration` — the SDLC planner script
- `connector-hub` — the connector layer

---

## Validation

Run these before opening a PR:

```bash
# Structural validation (kebab-case, SKILL.md presence)
python scripts/validation/validate_skill_structure.py .

# Frontmatter validation (required fields, format)
python scripts/validation/validate_frontmatter.py .

# Dependency gap detection
python scripts/orchestration/detect_skill_gaps.py

# Full test suite
pytest
```

All four must pass. CI blocks merge if any fail.

---

## Maturity Ladder

| Stage | Criteria | CI Required |
|---|---|---|
| `alpha` | Draft, may be incomplete | Structure + frontmatter |
| `beta` | Feature-complete, under review | All validation + tests |
| `stable` | Production-tested, peer-reviewed | Full CI + HITL audit |
| `deprecated` | Superseded; keep for reference | None |

Promote maturity by updating the `metadata.maturity` field and submitting a PR
with the changes documented in `CHANGELOG.md`.

---

## Checklist: Ready to Merge

- [ ] Directory name is kebab-case
- [ ] `SKILL.md` opens with valid YAML frontmatter
- [ ] `name` matches directory name
- [ ] `description` is under 1024 chars and has no angle brackets
- [ ] `metadata.version`, `category`, `owner`, `maturity` are populated
- [ ] Dependencies listed are real skills or known aliases
- [ ] Behavioral contract body is complete (Role → Quality Standards)
- [ ] Reference documents added for any complex schemas/runbooks
- [ ] HITL gates declared for any irreversible actions
- [ ] All validation scripts pass
- [ ] `detect_skill_gaps.py` reports no new missing dependencies