---
name: frontend-component-modeling
description: Designs or reconstructs frontend routes, screens, Lit web components, Tailwind conventions, states, events, validation, accessibility, and backend dependencies.
compatibility: opencode
metadata:
  domain: frontend-architecture
  preferred-framework: lit
---

# Frontend and component modeling

## Actual versus preferred stack

When designing from requirements, prefer:

- HTML
- Lit web components
- Tailwind CSS
- Server-backed flows

When reverse engineering, document the actual stack. Do not claim Lit or Tailwind if the repository uses another technology.

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

For Lit components, describe:

- Public properties
- Internal reactive state
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
