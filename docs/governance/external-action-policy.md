# External Action Policy

## Purpose
Set execution boundaries for outbound actions affecting third parties.

## Policy
- Outbound communications, commitments, purchases, and contract-related actions require explicit policy authorization.
- High-impact or reputation-sensitive external actions require human approval.
- The system must avoid binding commitments, legal admissions, or financial promises without authorized review.
- All external actions must be traceable to a workflow decision and approval record.

## Required Controls
- Approval gates by action type and impact threshold.
- Recipient and payload validation before dispatch.
- Reversible/dry-run mode where supported.
