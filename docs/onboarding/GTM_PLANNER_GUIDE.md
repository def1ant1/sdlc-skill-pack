# GTM Planner Guide

The GTM Planner (`scripts/orchestration/plan_gtm_workflow.py`) routes
go-to-market objectives to the correct sequence of GTM skills, producing
an execution plan compatible with the Apotheon workflow runtime.

---

## When to Use the GTM Planner

Use the GTM planner (not the SDLC planner) when the objective is:
- Product launch coordination
- Organic search / SEO
- Paid acquisition campaigns
- Content strategy and publishing
- Customer success and retention
- Revenue optimization (churn, pricing, expansion)
- Analytics and attribution

Use the SDLC planner (`plan_workflow.py`) for engineering objectives
(architecture, coding, testing, deployment).

---

## Registered GTM Skills

| Skill | Routing Keywords | Description |
|---|---|---|
| `launch-planning` | launch, go-to-market, GTM, announce | End-to-end product launch coordination |
| `seo-engineering` | SEO, organic, search, keyword, ranking | Technical SEO and content gap analysis |
| `content-marketing` | content, blog, article, copywriting | Content strategy and asset production |
| `ai-search-optimization` | AI search, GEO, LLM visibility, SGE | Generative engine optimization |
| `paid-acquisition` | paid, ads, PPC, Google Ads, LinkedIn Ads | Paid channel management |
| `analytics-intelligence` | analytics, attribution, tracking, events | GA4, Mixpanel, event taxonomy |
| `customer-success` | customer success, onboarding, churn, NPS | CS playbooks and health scoring |
| `revenue-optimization` | revenue, pricing, LTV, churn, MRR | Revenue levers and pricing strategy |

---

## Usage

### Basic

```bash
python scripts/orchestration/plan_gtm_workflow.py "<objective>"
```

### Pipe into runtime

```bash
python scripts/orchestration/plan_gtm_workflow.py "Launch B2B SaaS to enterprise market" | \
  python scripts/runtime/execute_workflow.py
```

### Dry run (plan only, no execution)

```bash
python scripts/orchestration/plan_gtm_workflow.py "Improve organic traffic" | \
  python scripts/runtime/execute_workflow.py --dry-run
```

### Save plan to file for review

```bash
python scripts/orchestration/plan_gtm_workflow.py "Reduce churn rate" > gtm_plan.json
# Review plan...
python scripts/runtime/execute_workflow.py --plan gtm_plan.json
```

---

## Output Schema

```json
{
  "plan_id": "GTM-1746619200-a3f7b2c1",
  "objective": "Launch developer tools product",
  "skill_chain": [
    {
      "step": 1,
      "skill": "launch-planning",
      "phase": "planning",
      "gate_before_next": null
    },
    {
      "step": 2,
      "skill": "analytics-intelligence",
      "phase": "instrumentation",
      "gate_before_next": "Verify tracking live"
    },
    {
      "step": 3,
      "skill": "seo-engineering",
      "phase": "organic",
      "gate_before_next": null
    }
  ]
}
```

Fields:
- `plan_id` — Unique plan identifier (format: `GTM-<timestamp>-<random>`)
- `objective` — Original objective string (preserved verbatim)
- `skill_chain` — Ordered list of skills to execute
- `gate_before_next` — Optional human checkpoint description between steps

---

## Skill Execution Order

The planner builds a dependency-ordered chain. Typical ordering:

```
launch-planning
    → analytics-intelligence    (instrument before generating traffic)
    → seo-engineering           (organic foundation)
    → content-marketing         (assets for SEO + paid)
    → paid-acquisition          (amplify with paid)
    → customer-success          (capture and retain)
    → revenue-optimization      (optimize monetization)
```

For objective-specific plans, only relevant skills are included. A pure
SEO objective may only chain `seo-engineering` and `content-marketing`.

---

## Context Passing Between Steps

Each skill receives:
- `objective` — the original user objective
- `context_packet` — accumulated decisions, artifacts, and risks from prior steps
- `additional_context` — last 2 step outputs (truncated to 2000 chars each)

This means `revenue-optimization` has access to the launch plan, analytics
configuration, and content strategy when it runs.

---

## Adding a New GTM Skill

1. Create the skill under `skills/<name>/SKILL.md` following the skill authoring guide
2. Add the skill name to `plan_gtm_workflow.py`'s routing table
3. Add a `SKILL.md` on-disk assertion to `tests/scripts/test_plan_gtm_workflow.py`
4. Add the name to `EXPECTED_GTM_SKILLS` in the test file
5. Run `pytest tests/scripts/test_plan_gtm_workflow.py` to verify

---

## Troubleshooting

| Issue | Cause | Fix |
|---|---|---|
| Plan routes to unknown skill | New skill not in routing table | Add to `plan_gtm_workflow.py` |
| `detect_skill_gaps.py` flags GTM dependency | Alias not in `_KNOWN_ALIASES` | Add to the alias set |
| Execution fails at Step 1 | Missing `ANTHROPIC_API_KEY` | Export the env var |
| HITL gate triggers unexpectedly | Output contains approval keyword | Review skill output or adjust detection phrases in `skill_activity.py` |