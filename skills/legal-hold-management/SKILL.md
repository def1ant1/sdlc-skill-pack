---
name: legal-hold-management
description: Manages the full legal hold lifecycle from placement through release — suspending data retention policies, preserving relevant data, tracking custodians, and coordinating release with legal counsel.
metadata:
  version: "1.0.0"
  category: privacy
  owner: legal
  maturity: alpha
  dependencies: [privacy-runtime, data-fabric, governance, telemetry]
---

## Role

Legal hold lifecycle orchestrator for the enterprise privacy and legal operations runtime.
Manages the complete chain of custody from hold placement through collection, preservation,
and release — ensuring all potentially relevant data is preserved in an unaltered state
and all retention policy exemptions are properly documented for defensibility.

## Activation Triggers

- Legal counsel issues a litigation hold notice requiring data preservation
- Regulatory investigation triggers a preservation obligation
- Active hold expiration review scheduled by the governance calendar
- Legal counsel requests hold release following matter resolution

## Execution Protocol

1. **Place hold**: Register the hold with a unique hold-id; record the matter name, scope
   definition (data types, date range, custodians), placing counsel identity, and hold date.

2. **Identify custodians**: Enumerate all data custodians (individuals and systems) whose
   data falls within the hold scope; notify them of preservation obligations.

3. **Suspend retention policies**: Override normal data retention and deletion schedules
   for all data within scope; apply a hold exemption flag in the data fabric to prevent
   automated deletion.

4. **Collect and preserve**: For high-risk data (volatile or frequently modified), trigger
   immediate collection and preservation to immutable storage with integrity hashing.

5. **Track custodian acknowledgments**: Send hold notices to all human custodians; record
   acknowledgment timestamps; escalate non-responses after 72 hours.

6. **Release hold**: Upon legal counsel authorization, lift hold exemptions; restore normal
   retention policies; produce a chain-of-custody report for the matter record; trigger
   data-redaction for any data not subject to other retention requirements.

## Output Format

Legal hold record with: `hold_id`, `matter_name`, `hold_status` (ACTIVE/RELEASED),
`custodians` (count and list with acknowledgment status), `data_volume_preserved`,
`retention_policies_suspended` (list), `hold_placed_date`, and `release_date` (if released).

## References

- `references/legal-hold-protocol.md` — hold scope definition template, custodian notification workflow, chain-of-custody requirements