# Quality Gate Enforcement

Describes how the orchestration control plane evaluates and enforces quality
gates at every SDLC phase transition.

---

## Gate Catalog

All gate definitions live in `shared/frameworks/quality-gates/catalog.md`.
That file is the source of truth for criteria, evidence requirements, and
remediation guidance. This document covers the enforcement protocol only.

---

## When Gates Are Evaluated

A gate is evaluated **immediately before** the next skill in the chain loads.
The gate for transition A → B is evaluated after skill A produces its outputs
and before skill B begins.

Gates are not evaluated retroactively. If a skill produces outputs mid-phase,
the gate is only evaluated when the skill signals completion.

---

## Evaluation Protocol

```
1. Collect evidence
   - Check memory packet for all artifacts listed in gate's evidence_required.
   - If any evidence is missing: gate status = NOT_EVALUATED.
     Surface missing artifacts to user. Do not proceed.

2. Evaluate criteria
   - Assess each criterion against available evidence.
   - Classify each criterion: PASS | FAIL | WARN.

3. Determine gate status
   - All block-level criteria PASS → gate status = PASS.
   - All block-level criteria PASS, one or more WARN → gate status = PASS_WITH_WARNINGS.
   - Any block-level criterion FAIL → gate status = FAIL.

4. Record result
   - Write gate name, status, and per-criterion results to the memory packet.
   - Timestamp the evaluation.

5. Act on status
   - PASS or PASS_WITH_WARNINGS: load next skill.
   - FAIL: execute the gate failure protocol (below).
   - NOT_EVALUATED: surface missing evidence and pause.
```

---

## Gate Failure Protocol

When a gate returns `FAIL`:

1. **Surface all failures.** List every failed criterion with a one-sentence explanation of why it failed.
2. **Generate remediation tasks.** For each failed criterion, produce a concrete remediation task referencing the gate's remediation guidance in the catalog.
3. **Block advancement.** Do not load the next skill. Set the next phase status to `blocked` in the memory packet.
4. **Do not summarize failures away.** Every failed criterion must be explicitly named. "Some criteria were not met" is non-compliant output.
5. **Await user acknowledgement.** Present remediation tasks and ask the user to confirm when remediation is complete.
6. **Re-evaluate.** When the user confirms remediation, re-evaluate the gate. Append the new result to the memory packet (retain the prior FAIL record).

### Failure Output Format

```md
## Gate Failure: <gate-name>

**Transition:** <Phase A> → <Phase B>
**Status:** FAIL

### Failed Criteria

1. **<criterion text>**
   Why it failed: <brief explanation>
   Remediation: <concrete action>

2. **<criterion text>**
   Why it failed: <brief explanation>
   Remediation: <concrete action>

### Warnings (non-blocking)

- <warn-level criterion and note>

### Next Steps

Complete the remediation tasks above and confirm when ready to re-evaluate.
The following phase is blocked until this gate passes: **<next phase name>**.
```

---

## Gate Waiver Protocol

A gate criterion may be waived only when:

- The user explicitly requests it.
- A documented rationale is provided.
- The waiver is recorded in the memory packet with the user's rationale.

Waivers set the criterion status to `SKIPPED`. The gate may still achieve overall
`PASS` if all non-waived block-level criteria pass.

Waivers are not permitted for `fail_action: escalate` criteria without completing
the escalation review first.

---

## Escalation

Gates with `fail_action: escalate` on a criterion trigger the escalation protocol
in `core/orchestration/references/escalation-rules.md`. This applies to:

- Any security finding rated `critical`
- AI risk classification rated `critical`
- Gate failures on workflows involving regulated data (PII, PHI, financial)
- Second consecutive `FAIL` on the same gate after remediation

---

## Gate State in the Memory Packet

Gate evaluation results are recorded in the `quality_gate_status` field of the
memory packet using this structure:

```yaml
quality_gate_status:
  - gate_name: architecture-approved
    status: PASS
    evaluated_at: "2026-05-06T14:32:00Z"
    criteria:
      - text: "System design document exists"
        result: PASS
      - text: "At least one ADR exists"
        result: PASS
  - gate_name: security-review-passed
    status: FAIL
    evaluated_at: "2026-05-06T16:10:00Z"
    criteria:
      - text: "No critical-severity findings unmitigated"
        result: FAIL
        note: "CVE in auth library not yet remediated"
      - text: "Threat model covers all entry points"
        result: PASS
    remediation_tasks:
      - "Upgrade auth library to patched version; re-run security scan"
```

---

## Relationship to Validation Scripts

`scripts/orchestration/validate_workflow_state.py` reads the memory packet and
enforces gate state programmatically. It:

- Blocks phase transitions when upstream gates are `FAIL` or `NOT_EVALUATED`.
- Reports gate status in machine-readable JSON.
- Is invoked by CI on workflow state files committed to the repository.

For per-gate validation (checking that criteria are evaluable from available
artifacts), see `scripts/validation/validate_quality_gate.py` (P5-003).
