# Governance Kernel

The governance kernel is the control-plane coordinator for policy enforcement, approval gating, and evidence generation.

## Responsibilities

- Route runtime action requests into `scripts/governance/enforce_runtime_policy.py`.
- Enforce fail-closed behavior for high-risk side-effect actions without approval.
- Emit policy decision artifacts for dashboard ingestion and auditable logs.
- Trigger `scripts/governance/generate_evidence_pack.py` for regulated workflows.
