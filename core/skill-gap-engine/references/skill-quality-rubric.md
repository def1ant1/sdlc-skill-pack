# Skill Quality Rubric

## Overview

The quality rubric scores each SKILL.md file on six dimensions (total 100 points).
A skill must score ≥ 60 to be considered adequate. Skills below 60 are flagged as
WEAK gaps. Skills between 60–74 are BELOW TARGET and should be improved in the
next sprint.

---

## Dimension 1 — Role Clarity (0–20 points)

**What it measures**: Is the skill's purpose clearly defined? Is it distinct from
other skills in the registry?

| Score | Criteria |
|---|---|
| 18–20 | Role section defines a specific, bounded purpose; explicitly contrasts with overlapping skills; a new engineer could understand the skill's domain from the role alone |
| 12–17 | Role is clear but slightly vague; overlaps not explicitly addressed |
| 6–11 | Role section exists but is generic; could apply to multiple skills |
| 0–5 | No role section; role cannot be determined from the content |

**Fail threshold**: < 10

**Examples of strong role clarity**:
> "You are the Compliance Governance skill. While `compliance-automation` handles evidence
> collection for specific frameworks, you handle ongoing governance: policy attestation,
> control health monitoring, and risk register management across all active frameworks."

---

## Dimension 2 — Activation Triggers (0–15 points)

**What it measures**: Are the conditions for loading this skill specific and actionable?

| Score | Criteria |
|---|---|
| 13–15 | 4–6 specific trigger conditions; each is a concrete, distinguishable scenario |
| 8–12 | 3–5 triggers; mostly specific; one or two are vague |
| 4–7 | Fewer than 3 triggers; or triggers are too generic (e.g., "when needed") |
| 0–3 | No trigger section; or triggers are circular ("load when this skill is relevant") |

**Fail threshold**: < 8

---

## Dimension 3 — Execution Protocol Completeness (0–25 points)

**What it measures**: Does the protocol provide a numbered, actionable step-by-step
process that an agent could follow independently?

| Score | Criteria |
|---|---|
| 22–25 | 4–8 numbered steps; each step: what to do, how to do it, what to produce; covers normal, error, and edge cases |
| 15–21 | Steps present and mostly actionable; minor gaps in error handling or output specification |
| 8–14 | Steps exist but are abstract ("analyze and recommend"); missing outputs or conditions |
| 0–7 | No protocol; or protocol is a single paragraph with no structure |

**Fail threshold**: < 15

---

## Dimension 4 — Reference Coverage (0–20 points)

**What it measures**: Are the referenced files sufficient and do they exist?

| Score | Criteria |
|---|---|
| 18–20 | All referenced files exist (or are planned with a clear path); references cover all major decision tables and templates the protocol uses |
| 12–17 | Most references exist; one or two are stubs or missing |
| 6–11 | References listed but most are missing; skill relies on references that don't exist |
| 0–5 | No references section; or protocol mentions templates/tables with no reference to where they are |

**Fail threshold**: < 10

---

## Dimension 5 — Standards Compliance (0–10 points)

**What it measures**: Does the skill conform to the structural and frontmatter standards?

| Score | Criteria |
|---|---|
| 9–10 | Valid YAML frontmatter; all required fields present; description ≤ 1024 chars; no angle brackets; file in correct directory |
| 6–8 | Frontmatter valid; minor issues (extra fields, non-ideal description) |
| 3–5 | Frontmatter present but missing 1–2 required fields |
| 0–2 | Frontmatter missing or unparseable |

**Fail threshold**: < 8 (hard fail for frontmatter invalidity)

---

## Dimension 6 — Dependency Accuracy (0–10 points)

**What it measures**: Are the declared dependencies accurate and free of issues?

| Score | Criteria |
|---|---|
| 9–10 | All listed dependencies exist; none are circular; dependencies are necessary (no phantom deps) |
| 6–8 | All dependencies exist; one phantom dependency (listed but not actually used) |
| 3–5 | One or two dependencies reference non-existent skills; or circular dependency present |
| 0–2 | Dependencies not listed; or majority reference non-existent skills |

**Fail threshold**: < 6

---

## Scoring Summary

| Dimension | Max | Fail Threshold |
|---|---|---|
| Role clarity | 20 | < 10 |
| Activation triggers | 15 | < 8 |
| Execution protocol | 25 | < 15 |
| Reference coverage | 20 | < 10 |
| Standards compliance | 10 | < 8 |
| Dependency accuracy | 10 | < 6 |
| **Total** | **100** | **< 60 overall** |

---

## Score Interpretation

| Score | Classification | Action |
|---|---|---|
| 85–100 | Excellent | No action; monitor |
| 75–84 | Good | Minor improvements welcome; not blocking |
| 60–74 | Below target | Improve in next sprint (P2 backlog item) |
| 40–59 | Weak | Strengthen in current sprint (P1 backlog item) |
| < 40 | Poor | Priority fix; may block workflow execution |