# Knowledge Note Taxonomy

The Knowledge Curation Assistant stores **proposed** and **curated** memory as knowledge notes.

## Note categories

- **fact**: Stable, verifiable statement that should persist until superseded.
- **preference**: User preference for style, tooling, output format, or process.
- **constraint**: Boundary or non-negotiable rule (policy, legal, timeline, budget).
- **decision**: Chosen option with rationale and expected impact.
- **procedure**: Repeatable steps or playbook guidance.
- **warning**: Deprecated, unsafe, or disallowed guidance.

## Lifecycle states

- `proposed`: Extracted from conversation; pending explicit approval.
- `approved`: Accepted as active memory.
- `edited`: Updated by user/editor while preserving provenance.
- `rejected`: Not retained for retrieval.
- `archived`: Historical but no longer active.
- `superseded`: Replaced by a newer note.

## Required metadata

- `id`: Stable note identifier.
- `title`: Short human label.
- `category`: One of the taxonomy categories.
- `status`: Lifecycle state.
- `statement`: Canonical memory statement.
- `provenance`: Conversation and message references.
- `impact_links`: Artifact/entity references affected by this note.
- `confidence`: low/medium/high.
- `staleness`: fresh/stale/conflicted.

## Conflict and staleness signals

A note is flagged when:

1. A newer note with overlapping subject contradicts its statement.
2. A note has an explicit expiration date that has passed.
3. A user issues deprecation commands (e.g., “don’t use that anymore”).
