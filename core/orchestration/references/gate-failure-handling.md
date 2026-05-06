# Gate Failure Handling Protocol

Defines exactly what happens when a quality gate returns `FAIL` during an
SDLC workflow. Enforced by `core/orchestration/SKILL.md` Step 4.

See `shared/frameworks/quality-gates/catalog.md` for gate definitions and
`docs/workflows/quality-gate-enforcement.md` for the evaluation procedure.

---

## Failure Categories

Every gate failure falls into one of three categories based on the gate's
`fail_action` value. The handling protocol differs by category.

### Category 1 — Block (`fail_action: block`)

The workflow halts. The next phase does not load until all block-level criteria
pass on re-evaluation.

**Used for:** Missing required artifacts, critical security findings, undefined
auth strategy, no rollback plan, upstream gates still failing.

### Category 2 — Warn (`fail_action: warn`)

The workflow continues. The failure is logged prominently in the memory packet
and surfaced to the user, but does not stop phase advancement.

**Used for:** Low-severity security findings, static analysis not yet run,
non-critical checklist gaps that do not affect downstream correctness.

### Category 3 — Escalate (`fail_action: escalate`)

The workflow halts and the failure is routed to the escalation protocol in
`core/orchestration/references/escalation-rules.md`. Human review is required
before the workflow may continue.

**Used for:** Critical-severity security findings, critical AI risk tier,
regulated data handling issues, second consecutive failure on the same gate
after remediation.

---

## Failure Handling Steps

### Step 1 — Surface All Failures Immediately

When a gate returns `FAIL`, produce a failure report before doing anything else.
Do not summarize, defer, or mention failures in passing. Every failed criterion
must be named explicitly.

**Non-compliant:** "The gate did not fully pass. Some criteria need attention."
**Compliant:** See failure report format below.

### Step 2 — Generate Remediation Tasks

For each failed criterion, produce one concrete remediation task. A remediation
task must state:

- What must be done (specific artifact, decision, or fix)
- Which gate criterion it addresses
- Which phase or skill is responsible for producing it

Remediation tasks are numbered `REM-NNN` and recorded in the memory packet.

### Step 3 — Update the Memory Packet

Record the gate result in `quality_gate_status` with:

- `status: FAIL`
- Per-criterion results including `FAIL` entries with explanatory notes
- The full list of remediation tasks

Set the blocked phase's `phase_status` to `blocked`.
Set `next_action` to the first remediation task.

### Step 4 — Block Advancement

Do not load any skill downstream of the failing gate.
Do not evaluate downstream gates.
State explicitly which phase is blocked and by which gate.

### Step 5 — Await User Acknowledgement

Present the failure report and remediation task list to the user.
Ask the user to confirm when remediation is complete before re-evaluating.
Do not re-evaluate the gate without user confirmation.

### Step 6 — Re-Evaluate After Remediation

When the user confirms remediation:

1. Re-collect the gate's required evidence from the memory packet.
2. Re-evaluate all criteria, including those that previously passed.
3. Append the new result to `quality_gate_status` — retain the prior `FAIL` record.
4. If the gate now passes: clear the `blocked` status, update `next_action`, proceed.
5. If the gate fails again on the same criterion: escalate (see Category 3 above).

---

## Failure Report Format

```md
## Gate Failure: <gate-name>

**Transition:** <Phase A> → <Phase B>
**Status:** FAIL
**Fail Action:** block | warn | escalate

---

### Failed Criteria

**REM-001 — <Criterion text>**
- Why it failed: <one sentence explaining the specific gap>
- Remediation: <concrete action — what to produce, fix, or decide>
- Responsible: <skill name or user>

**REM-002 — <Criterion text>**
- Why it failed: <one sentence>
- Remediation: <concrete action>
- Responsible: <skill name or user>

---

### Warnings (non-blocking)

- <warn-level criterion>: <brief note>

---

### Gate Status After This Evaluation

| Criterion | Result |
|---|---|
| <criterion text> | FAIL |
| <criterion text> | PASS |
| <criterion text> | WARN |

---

### Blocked Phase

**<Next phase name>** is blocked until **<gate-name>** passes.

Complete the remediation tasks above and confirm when ready to re-evaluate.
```

---

## Memory Packet Recording

Gate failures are recorded in the `quality_gate_status` array of the memory
packet. The format is defined in `docs/schemas/memory-packet-schema.md`.

Example of a recorded failure with remediation tasks:

```yaml
quality_gate_status:
  - gate_name: security-review-passed
    transition: "devsecops → qa-automation"
    status: FAIL
    evaluated_at: "2026-05-06T16:10:00Z"
    criteria:
      - text: "No critical-severity findings left unmitigated"
        result: FAIL
        note: "CVE-2025-1234 in auth library rated critical; no patch applied yet"
      - text: "Threat model covers all service entry points"
        result: PASS
      - text: "Prompt injection defense included for AI systems"
        result: FAIL
        note: "Threat model does not include prompt injection attack surface"
      - text: "Secrets management approach defined"
        result: PASS
    remediation_tasks:
      - id: REM-001
        criterion: "No critical-severity findings left unmitigated"
        action: "Upgrade auth library to version >=2.4.1 which patches CVE-2025-1234. Re-run dependency scan. Update threat model with patch evidence."
        responsible: backend-engineering
      - id: REM-002
        criterion: "Prompt injection defense included for AI systems"
        action: "Extend threat model to include prompt injection attack surface. Add input sanitization requirement to the backend engineering specification."
        responsible: devsecops

  - gate_name: security-review-passed
    transition: "devsecops → qa-automation"
    status: PASS
    evaluated_at: "2026-05-06T18:45:00Z"
    criteria:
      - text: "No critical-severity findings left unmitigated"
        result: PASS
      - text: "Threat model covers all service entry points"
        result: PASS
      - text: "Prompt injection defense included for AI systems"
        result: PASS
      - text: "Secrets management approach defined"
        result: PASS
    prior_fail_ref: "Evaluation at 2026-05-06T16:10:00Z"
```

Key rules for recording:

1. Retain all prior evaluation records — never overwrite a `FAIL` with the passing result.
2. Link re-evaluations to prior records with `prior_fail_ref`.
3. Remediation tasks remain in the packet even after the gate passes, as an audit trail.
4. Set `phase_status` of the blocked phase back to `pending` once the gate clears.

---

## Escalation Triggers

A gate failure triggers escalation (Category 3) when any of the following are true:

| Trigger | Example |
|---|---|
| Any security criterion rated `critical` fails | Critical CVE unmitigated; hardcoded secret found |
| AI risk tier is `critical` and an AI governance criterion fails | No human oversight defined for critical-risk AI system |
| The same criterion fails a second time on the same gate after remediation | Remediation confirmed but criterion still fails on re-evaluation |
| The workflow involves regulated data (PII, PHI, financial) and a data handling criterion fails | No data minimization approach for PII reaching the model |
| User requests an explicit waiver on a `fail_action: block` criterion | Must be escalated and logged before waiver is granted |

When escalation is triggered, follow `core/orchestration/references/escalation-rules.md`.

---

## Warn-Only Failures

Gates with `fail_action: warn` on a criterion do not block advancement but
require the failure to be surfaced and logged.

Warn-only failures must:

1. Appear in the failure report under "Warnings (non-blocking)".
2. Be recorded in `quality_gate_status` with `result: WARN`.
3. Be carried forward in the memory packet's `risks` section with `status: open`.
4. Be reviewed at the next applicable gate (they do not expire silently).

Warn-only failures must never be silently dropped from the memory packet.

---

## Failure Prevention

The orchestration control plane should prevent foreseeable gate failures by:

1. **Pre-checking evidence availability** before evaluating a gate. If required
   artifacts are missing, surface this before the skill that was supposed to
   produce them completes — not after.
2. **Flagging pending decisions** (`decisions.pending` in the memory packet) that
   are known to block a gate criterion. Surface these to the user at the start of
   the phase that must resolve them.
3. **Carrying warn-level failures forward** as risks so downstream phases can
   address them proactively before they become block-level failures at a later gate.