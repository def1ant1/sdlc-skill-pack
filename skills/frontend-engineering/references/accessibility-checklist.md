# Accessibility Checklist

## Usage

Run this checklist for every new page, modal, and interactive component before
merging. Items marked [AUTO] are verified by automated tools. Items marked [MANUAL]
require human or assistive technology verification.

---

## 1. Semantic HTML

- [ ] [AUTO] Use semantic elements: `<header>`, `<nav>`, `<main>`, `<section>`, `<article>`, `<aside>`, `<footer>`
- [ ] [AUTO] Heading hierarchy: `<h1>` once per page; `<h2>`–`<h6>` in logical order, no skips
- [ ] [MANUAL] Page has exactly one `<main>` landmark
- [ ] [AUTO] Lists use `<ul>` / `<ol>` / `<dl>`; never fake lists with divs
- [ ] [AUTO] Tables use `<th>` with `scope`; have `<caption>` or `aria-label`

---

## 2. Keyboard Navigation

- [ ] [MANUAL] All interactive elements reachable via Tab key
- [ ] [MANUAL] Tab order is logical (follows visual reading order)
- [ ] [MANUAL] No keyboard traps (user can always Tab out of any component)
- [ ] [MANUAL] Modals trap focus correctly while open; restore focus on close
- [ ] [MANUAL] Custom dropdowns/menus support arrow key navigation
- [ ] [MANUAL] `Escape` closes modals, dropdowns, and popups

---

## 3. Focus Management

- [ ] [AUTO] No `outline: none` or `outline: 0` without a visible focus replacement
- [ ] [MANUAL] Focus ring is clearly visible (3:1 contrast ratio minimum)
- [ ] [MANUAL] On page navigation (SPA): focus moves to new page heading or main content
- [ ] [MANUAL] After async action (form submit): focus moves to success/error message

---

## 4. Color and Contrast

- [ ] [AUTO] Normal text: contrast ratio ≥ 4.5:1 against background
- [ ] [AUTO] Large text (≥ 18pt or ≥ 14pt bold): contrast ratio ≥ 3:1
- [ ] [AUTO] UI components and states (borders, icons): contrast ≥ 3:1
- [ ] [MANUAL] Information is not conveyed by color alone (add icon, pattern, or text)
- [ ] [AUTO] Error states: not indicated only by red color

---

## 5. Images and Icons

- [ ] [AUTO] All `<img>` elements have `alt` attribute
- [ ] [MANUAL] Informative images: `alt` describes the content and purpose
- [ ] [MANUAL] Decorative images: `alt=""` (empty, not missing)
- [ ] [MANUAL] Icon-only buttons: `aria-label` or visually hidden text (`<span class="sr-only">`)
- [ ] [MANUAL] SVG icons: `aria-hidden="true"` if decorative; `role="img"` + `<title>` if informative

---

## 6. Forms

- [ ] [AUTO] Every input has an associated `<label>` (via `for`/`id` or wrapping)
- [ ] [MANUAL] No placeholder-only labels (placeholder disappears on input)
- [ ] [AUTO] Required fields indicated: `required` attribute AND visible indication
- [ ] [AUTO] Error messages use `aria-describedby` to associate with the field
- [ ] [MANUAL] Error messages describe how to fix the error, not just that an error occurred
- [ ] [MANUAL] Form can be submitted and completed using keyboard only

---

## 7. Dynamic Content

- [ ] [MANUAL] Live regions (`aria-live`) used for status messages and alerts
- [ ] [MANUAL] Loading states announced: `aria-busy="true"` during load
- [ ] [MANUAL] Toast/notification messages announced to screen readers
- [ ] [MANUAL] After filtering/sorting: updated result count announced

---

## 8. Motion and Animation

- [ ] [AUTO] CSS uses `@media (prefers-reduced-motion: reduce)` to disable non-essential animation
- [ ] [MANUAL] No content flashes more than 3 times per second (seizure risk)
- [ ] [MANUAL] Auto-playing video/audio has a pause mechanism

---

## 9. Automated Testing Tools

Run in CI:
- `axe-core` via `jest-axe` in unit tests: `expect(await axe(container)).toHaveNoViolations()`
- Storybook + accessibility addon for visual review
- Lighthouse accessibility audit in E2E suite (target score: ≥ 90)

Manual verification:
- Screen reader: NVDA (Windows) + Firefox; VoiceOver (macOS) + Safari
- Keyboard-only navigation: complete every user flow
- Browser zoom: verify layout at 200% zoom

---

## Severity Classification

| Severity | Examples | Action |
|---|---|---|
| Critical (WCAG A) | Missing alt text, keyboard trap, no form labels | Block merge |
| High (WCAG AA) | Contrast failure, missing error association | Block merge |
| Medium (WCAG AAA or best practice) | Missing live regions, reduced-motion not respected | Fix in same sprint |
| Low (enhancement) | Verbose but not wrong ARIA, cosmetic focus ring | Backlog |