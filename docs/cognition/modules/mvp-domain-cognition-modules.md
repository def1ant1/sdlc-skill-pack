# MVP Domain Cognition Modules

This reference defines cognition modules for priority MVP domains:
- sales
- finance/accounting
- legal/tax
- security
- HR
- knowledge/research
- GTM
- SDLC
- operations

Each module includes principles, heuristics, frameworks, evaluators, anti-pattern detectors, examples, policy boundaries, and memory hooks.

---

## 1) Sales
- **Principles:** customer value first; pipeline truth over optimism; next-best action clarity.
- **Heuristics:** trust commit stage only with validated MEDDICC evidence; aging deals > 1.5x median require risk tagging.
- **Frameworks:** ICP -> qualification -> stage hygiene -> forecast categories -> close plan.
- **Evaluators:** forecast error (MAPE), stage-conversion consistency, cycle-time drift, slipped-commit rate.
- **Anti-pattern detectors:** sandbagging, stage inflation, activity without advancement, single-threaded champions.
- **Examples:** weekly forecast call rubric; rescue plan for 90+ day stalled enterprise deal.
- **Policy boundaries:** no deceptive claims, no unauthorized discounting/contract commitments, human approval for pricing exceptions.
- **Memory hooks:** `buyer_commit_signals`, `deal_risks`, `mutual_action_plan_state`, `forecast_assumptions`.

## 2) Finance/Accounting
- **Principles:** accuracy, auditability, timeliness, segregation of duties.
- **Heuristics:** unexplained variance > 10% or journal outliers > 2 sigma trigger review.
- **Frameworks:** record -> reconcile -> close -> report -> controls evidence.
- **Evaluators:** close-cycle SLA, unreconciled balance count, exception aging, control-test pass rate.
- **Anti-pattern detectors:** unsupported JEs, duplicate invoices, stale accruals, reconciliation bypasses.
- **Examples:** month-end close checklist with blocker triage.
- **Policy boundaries:** no final accounting judgments/tax filings without licensed human sign-off.
- **Memory hooks:** `close_blockers`, `recon_exceptions`, `control_evidence_refs`, `policy_interpretation_questions`.

## 3) Legal/Tax
- **Principles:** obligation clarity, jurisdiction awareness, conservative interpretation, traceable rationale.
- **Heuristics:** any non-standard clause or uncertain nexus => escalate to counsel/tax professional.
- **Frameworks:** intake -> clause/obligation extraction -> risk scoring -> escalation path -> approval log.
- **Evaluators:** obligation completeness, clause deviation severity, response SLA, escalation correctness.
- **Anti-pattern detectors:** unauthorized legal advice, hidden obligations, missing renewal/termination triggers.
- **Examples:** NDA variance triage and tax registration trigger map.
- **Policy boundaries:** support-only; no legal conclusions or tax advice as final determinations.
- **Memory hooks:** `obligation_registry_links`, `clause_deviations`, `counsel_escalations`, `filing_deadlines`.

## 4) Security
- **Principles:** least privilege, defense in depth, secure-by-default, rapid containment.
- **Heuristics:** critical vuln or exposed secret => block and contain first, then root-cause.
- **Frameworks:** identify -> protect -> detect -> respond -> recover.
- **Evaluators:** MTTD/MTTR, critical-open-vuln count, patch latency, control coverage.
- **Anti-pattern detectors:** severity downgrading, blanket suppressions, unowned risk acceptances.
- **Examples:** release security gate decision tree.
- **Policy boundaries:** no bypass of critical gates without explicit high-level approval.
- **Memory hooks:** `incident_timeline`, `accepted_risks_with_expiry`, `control_gaps`, `postmortem_actions`.

## 5) HR
- **Principles:** fairness, consistency, confidentiality, policy compliance.
- **Heuristics:** adverse employee-impact decisions always require human review + bias check.
- **Frameworks:** request intake -> policy lookup -> impact assessment -> review/approval -> communication plan.
- **Evaluators:** policy-consistency score, turnaround SLA, adverse-impact indicators, exception frequency.
- **Anti-pattern detectors:** inconsistent policy application, missing documentation, confidentiality leakage.
- **Examples:** performance-improvement workflow with manager/HR/legal checkpoints.
- **Policy boundaries:** no autonomous hire/fire/pay/equity decisions.
- **Memory hooks:** `case_facts`, `policy_refs_used`, `required_reviews`, `follow_up_dates`.

## 6) Knowledge/Research
- **Principles:** source quality, reproducibility, uncertainty transparency, citation integrity.
- **Heuristics:** claims without primary evidence are tentative; conflicting sources require synthesis note.
- **Frameworks:** question framing -> evidence retrieval -> validation -> synthesis -> confidence grading.
- **Evaluators:** citation coverage, contradiction rate, evidence freshness, confidence calibration.
- **Anti-pattern detectors:** cherry-picking, stale source bias, overconfident conclusions.
- **Examples:** literature synthesis with evidence-grade matrix.
- **Policy boundaries:** do not fabricate sources; mark assumptions and unknowns.
- **Memory hooks:** `evidence_map`, `confidence_scores`, `open_questions`, `source_quality_notes`.

## 7) GTM
- **Principles:** segment focus, message-market fit, measurable funnel outcomes.
- **Heuristics:** low-converting channels get test budget caps until hypotheses validate.
- **Frameworks:** segmentation -> positioning -> channel plan -> campaign execution -> experiment loop.
- **Evaluators:** CAC payback, conversion by stage, win-rate by segment, experiment velocity.
- **Anti-pattern detectors:** vanity metrics, channel sprawl, inconsistent messaging.
- **Examples:** launch plan with pre/during/post milestones.
- **Policy boundaries:** truthful claims only; approval required for public statements and offers.
- **Memory hooks:** `segment_hypotheses`, `message_tests`, `campaign_results`, `next_experiments`.

## 8) SDLC
- **Principles:** correctness, maintainability, security, operability.
- **Heuristics:** risky changes need tests + rollback; complexity above threshold needs design review.
- **Frameworks:** plan -> implement -> verify -> release -> observe -> improve.
- **Evaluators:** defect escape rate, test coverage on changed logic, deployment success rate, rollback frequency.
- **Anti-pattern detectors:** no-tests merges, flaky gate masking, unclear ownership, silent failures.
- **Examples:** PR readiness rubric and incident-driven hardening loop.
- **Policy boundaries:** production-impacting changes require change control and approval policy compliance.
- **Memory hooks:** `adr_links`, `test_evidence`, `release_risks`, `post_release_findings`.

## 9) Operations
- **Principles:** reliability, throughput, standardization, continuous improvement.
- **Heuristics:** recurring incidents > 2 in 30 days trigger root-cause and SOP update.
- **Frameworks:** intake -> prioritization -> execution -> monitoring -> retrospective.
- **Evaluators:** SLA attainment, backlog aging, rework rate, throughput variance.
- **Anti-pattern detectors:** heroics over process, queue starvation, undocumented workarounds.
- **Examples:** weekly operating review with exception ledger.
- **Policy boundaries:** high-impact operational changes require owner approval and audit trail entries.
- **Memory hooks:** `runbook_updates`, `recurring_failures`, `owner_commitments`, `next_review_checkpoint`.
