# Improvement Workflow (Evolution + Skill Gap)

This workflow converts failed workflow evidence into PR-ready improvement proposals while keeping all high-risk changes human-gated.

## Flow

1. Collect failed workflow evidence (JSON).
2. Run `scripts/evolution/propose_skill_changes.py` to generate suggested patches/tests/evals.
3. Render PR-ready draft with `scripts/evolution/generate_skill_pr.py`.
4. Run `scripts/evolution/review_skill_change.py`.
5. Only proceed when an explicit human approver is recorded.

## Safety controls

- Auto-apply is disabled.
- Auto-merge is disabled.
- High-risk proposals require explicit human approval.
- PR checks enforce a human-approval marker.

## Example

```bash
python scripts/evolution/propose_skill_changes.py --failures runtime/evidence/failed_workflows.json --output runtime/evolution/proposals.json
python scripts/evolution/generate_skill_pr.py --proposal runtime/evolution/proposals.json --output runtime/evolution/proposal.md
python scripts/evolution/review_skill_change.py --proposal runtime/evolution/proposals.json --approved-by "operator@example.com"
```
