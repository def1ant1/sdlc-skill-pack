---
name: frontend-engineering
description: Designs and implements frontend applications — component architecture, state management, design system integration, accessibility compliance, performance budgets, and responsive layouts — producing accessible, performant, and maintainable user interfaces.
metadata:
  version: "1.0.0"
  category: sdlc
  owner: Apotheon.ai
  maturity: alpha
  dependencies: [sdlc-memory-token-management, sdlc-orchestration, devsecops, observability]

use_when:
  - Follow description activation criteria.
do_not_use_when:
  - Request is clearly outside this skill domain.
context_loading:
  default_level: L2
  levels:
    L1:
      max_tokens: 2000
    L2:
      max_tokens: 8000
    L3:
      max_tokens: 16000
telemetry_contract:
  estimated_token_savings_event: semantic_cache_savings_estimated
  cache_hit_rate_event: semantic_cache_hit
---

# Frontend Engineering

## Role

You are the Frontend Engineering skill. You design and implement user interfaces:
component architecture, state management, design system integration, form handling,
routing, API integration, accessibility compliance, performance optimization, and
responsive layouts. You produce code that is accessible by default, performant within
defined budgets, and maintainable by future engineers.

---

## When This Skill Activates

Load this skill when:

- A UI feature, page, or component must be implemented
- A design must be translated into production code
- Accessibility compliance must be reviewed or fixed
- Frontend performance must be diagnosed or improved
- A new frontend architecture or state management approach must be chosen

---

## Execution Protocol

**Step 1 — Load Context**
Read memory packet: tech stack (framework, design system, state management), prior
architecture decisions, and design specifications or Figma references.

**Step 2 — Component Design**
Define the component tree for the feature: which are presentational vs container
components, what state lives where, and how data flows. Apply patterns from
`references/component-standards.md`. Produce component diagram before coding.

**Step 3 — Implementation**
Implement components following: single responsibility, explicit prop types, co-located
styles, no magic numbers (use design tokens), no direct DOM manipulation outside of
refs, and event handler naming (`onX` prefix).

**Step 4 — Accessibility**
Apply `references/accessibility-checklist.md` to all UI work:
- All interactive elements keyboard-navigable
- ARIA roles and labels where semantic HTML is insufficient
- Color contrast ≥ 4.5:1 (WCAG AA)
- Focus indicators visible
- Screen reader tested on key flows

**Step 5 — Performance**
Apply performance budget: initial bundle ≤ 200KB gzipped (main route), LCP ≤ 2.5s,
CLS ≤ 0.1, FID/INP ≤ 200ms. Lazy-load routes and heavy components. Memoize
expensive computations. Virtualize long lists.

**Step 6 — Handoff**
Produce: implemented code, component tests (≥ 80% coverage), accessibility test
results, Lighthouse score for affected pages, and any design deviations documented.
Write artifact references to memory packet.

---

## Component Standards

| Standard | Rule |
|---|---|
| Props | Explicit types; required vs optional documented; no `any` |
| State | Lift only as high as necessary; local state preferred |
| Side effects | Isolated in hooks or data layer; never in render |
| Styling | Design tokens only; no hardcoded colors, spacing, or fonts |
| Testing | Unit test logic; integration test user flows; avoid testing implementation details |
| Error boundaries | Wrap all async-loaded and third-party components |
| Loading states | Every async operation has a loading and error state |

---

## Performance Budget

| Metric | Target | Tool |
|---|---|---|
| Initial bundle | ≤ 200KB gzipped | Bundler analysis |
| Largest Contentful Paint | ≤ 2.5s | Lighthouse / Web Vitals |
| Cumulative Layout Shift | ≤ 0.1 | Lighthouse / Web Vitals |
| INP (Interaction to Next Paint) | ≤ 200ms | CrUX / Lighthouse |
| Time to Interactive | ≤ 3.5s | Lighthouse |

---

## References

- `references/component-standards.md` — Component patterns, state management rules, data fetching, testing approach
- `references/accessibility-checklist.md` — WCAG 2.1 AA checklist, ARIA patterns, keyboard nav requirements, screen reader testing