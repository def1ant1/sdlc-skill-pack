# Context Budgeting

## Objective

Keep Claude focused on the smallest useful context window.

## Include

- latest user request
- current task objective
- relevant files
- active decisions
- constraints
- quality gates

## Summarize

- completed phases
- old discussion
- long research notes
- previous alternatives

## Exclude

- rejected ideas
- duplicate summaries
- unrelated standards
- full logs unless debugging

## Token Budget

| Area | Budget |
|---|---:|
| planning | 15% |
| source context | 35% |
| reasoning | 25% |
| output | 20% |
| buffer | 5% |
