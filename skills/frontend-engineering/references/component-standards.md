# Component Standards

## Component Architecture Principles

1. **Single responsibility**: One component, one purpose. Extract sub-components aggressively.
2. **Props as interface**: All inputs via props; no ambient state, no context abuse.
3. **Composition over inheritance**: Build complex UIs by composing simple components.
4. **Accessibility by default**: ARIA, keyboard navigation, and focus management are not optional.
5. **Test the behavior, not the implementation**: Assert what the user sees and can do.

---

## Component File Structure

```
src/components/<ComponentName>/
  index.ts                    # re-exports
  <ComponentName>.tsx         # component implementation
  <ComponentName>.test.tsx    # unit tests (RTL)
  <ComponentName>.stories.tsx # Storybook stories
  types.ts                    # prop types and interfaces (if complex)
```

---

## Component Template

```tsx
import { type FC } from 'react'

export interface ButtonProps {
  label: string
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
  loading?: boolean
  onClick: () => void
  'aria-label'?: string  // required when label is not descriptive
}

export const Button: FC<ButtonProps> = ({
  label,
  variant = 'primary',
  disabled = false,
  loading = false,
  onClick,
  'aria-label': ariaLabel,
}) => {
  return (
    <button
      className={cn(styles.base, styles[variant])}
      disabled={disabled || loading}
      aria-disabled={disabled || loading}
      aria-busy={loading}
      aria-label={ariaLabel}
      onClick={onClick}
    >
      {loading ? <Spinner size="sm" /> : null}
      {label}
    </button>
  )
}
```

---

## Naming Conventions

| Item | Convention | Example |
|---|---|---|
| Component | PascalCase | `UserProfileCard` |
| Props interface | `{Component}Props` | `UserProfileCardProps` |
| Hook | `use` + camelCase | `useUserProfile` |
| Context | `{Name}Context` | `AuthContext` |
| Event handler | `handle` + Event | `handleSubmit`, `handleChange` |
| CSS module class | camelCase | `styles.cardHeader` |

---

## State Management Rules

| State Type | Where to Put It |
|---|---|
| Local UI state (open/closed, hover) | `useState` in component |
| Form state | React Hook Form |
| Derived from props | `useMemo` — never duplicate |
| Server data | TanStack Query (React Query) |
| Global app state | Zustand store |
| URL state | URL params / search params |

**Never** store server data in Zustand. **Never** use Context for frequently updating state.

---

## Accessibility Requirements (WCAG 2.1 AA)

| Criterion | Requirement |
|---|---|
| Keyboard navigation | All interactive elements reachable via Tab; logical order |
| Focus visible | Focus ring always visible (no `outline: none` without replacement) |
| Color contrast | Text: 4.5:1 ratio; large text: 3:1 |
| Alt text | All images with `alt` (empty `alt=""` for decorative images) |
| Form labels | Every input has associated `<label>` or `aria-label` |
| Error messages | Associated with field via `aria-describedby` |
| Interactive ARIA | Use semantic HTML first; ARIA only when semantic element unavailable |
| Motion | Respect `prefers-reduced-motion` |

---

## Performance Standards

| Metric | Target | Tool |
|---|---|---|
| LCP (Largest Contentful Paint) | ≤ 2.5s | Lighthouse, Web Vitals |
| CLS (Cumulative Layout Shift) | ≤ 0.1 | Lighthouse |
| FID / INP (Interaction to Next Paint) | ≤ 200ms | Web Vitals |
| JS bundle (gzipped) | ≤ 200KB initial | webpack-bundle-analyzer |
| Image optimization | WebP/AVIF; `loading="lazy"` for below-fold | next/image or equivalent |

---

## Testing Standards

Every component must have tests covering:

```tsx
describe('Button', () => {
  it('renders label text', () => { ... })
  it('calls onClick when clicked', () => { ... })
  it('is disabled when disabled prop is true', () => { ... })
  it('shows spinner when loading', () => { ... })
  it('is accessible: has correct role and aria attributes', () => { ... })
})
```

Use `@testing-library/react`. Never test implementation details (refs, internal state).
Assert user-visible outcomes.