---
name: frontend-component-modeling
description: Designs or reconstructs frontend routes, screens, TypeScript components, Tailwind conventions, states, events, validation, accessibility, and backend dependencies.
compatibility: opencode
metadata:
  domain: frontend-architecture
  preferred-framework: lit
---

# Frontend and component modeling

## Actual versus approved stack

When designing from requirements, select a frontend stack only when approved requirements or an explicit architecture decision establishes it. When TypeScript components, Tailwind, and server-backed flows are approved, model their boundaries using:

- HTML
- TypeScript components
- Tailwind CSS
- Server-backed flows

When no stack is approved, record a bounded architecture decision or open question instead of silently choosing one. When reverse engineering, document the actual stack. Do not claim a component framework or Tailwind if the repository uses another technology.

## Route and screen inventory

For each screen define:

- Route
- User role
- Purpose
- Required data
- Primary actions
- Navigation entry points
- Loading state
- Empty state
- Success state
- Error state
- Permission behavior

## Component table

| Component | Responsibility | Properties | Events | Local state | Server dependencies | User interactions | Source |
|---|---|---|---|---|---|---|---|

For interactive components, describe:

- Public properties
- Presentation-only state; never backend data state
- Custom events
- Slots
- Lifecycle behavior
- Validation
- Accessibility semantics
- Styling conventions

## UI discipline

- Prefer modular components with explicit boundaries.
- Keep domain transitions server-authoritative.
- Define confirmation behavior for destructive actions.
- Specify field-level and form-level errors.
- Define stale or concurrent update behavior.
- Identify data shown to business users, not merely that a dashboard exists.
- Do not invent frontend implementation when none exists; label required surfaces as proposed or expected.
- Define a server-fragment versus client-component boundary: HTMX owns forms, requests, errors, and server-fragment swaps; client components own interaction behavior and emit events.
- Never specify an HTMX swap inside client-component-owned DOM. Client components receive server-provided inputs and do not fetch or own backend-derived state.
