---
name: frontend-component-modeling
description: Designs or reconstructs frontend routes, screens, TypeScript components, Tailwind conventions, states, events, validation, accessibility, and backend dependencies.
classification: non-technical
opencode_permission:
  read: allow
  question: allow
  skill:
    server-driven-component-contract: allow
    grillme: allow
inputs:
  - frontend scope
  - caller-provided permitted authority source and observed evidence paths
compatibility: opencode
metadata:
  domain: frontend-architecture
  preferred-framework: lit
---

# Frontend and component modeling

## Inputs

Require frontend scope and caller-provided permitted authority, source, and observed evidence paths.

## Deterministic workflow

```yaml
request: "Frontend component model with explicit server-driven contracts"
workflow:
  - id: "model-server-driven-contract"
    when: "For every independently server-driven component."
    skill: "server-driven-component-contract"
```

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
- Pending state
- Empty state
- Success state
- Error state
- Recovery state
- Last-known-good behavior
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
- Stable behavior-oriented hooks

When frontend interaction logging is required, define one shared emitter contract rather than component-owned transport. Specify the effective mode supplied by trusted backend configuration, versioned allowlisted event codes and fields, exact interaction triggers and outcomes, bounded queue and batch limits, flush behavior, same-origin endpoint contract, authentication and request protection, retry and drop behavior, and user-workflow behavior when telemetry is unavailable. Diagnostic events MUST identify routes or surfaces, actions, state transitions, validation, failure, and recovery without raw field values, payloads, rendered content, credentials, session identifiers, or personal or regulated data. Browser code MUST NOT select a more permissive mode, severity, tenant, user identity, environment, or sink.

## UI discipline

- Prefer modular components with explicit boundaries.
- Keep domain transitions server-authoritative.
- Define confirmation behavior for destructive actions.
- Specify field-level and form-level errors.
- Define stale or concurrent update behavior.
- For each asynchronous region, define initial-loading, populated, empty, pending, error, recovery, and last-known-good behavior. Empty is not error, and post-load failure must not erase valid unaffected content unless authority requires it.
- Define a preservation matrix for applicable draft input, selection, pagination, filters, ranges, modal identity, focus, scroll, and unaffected sibling content.
- Prefer native semantics, shared components and semantic tokens, visible focus, stable `data-*` behavior hooks, and one accessible action path.
- Identify data shown to business users, not merely that a dashboard exists.
- Do not invent frontend implementation when none exists; label required surfaces as proposed or expected.
- Define a server-fragment versus client-component boundary: HTMX owns forms, requests, errors, and server-fragment swaps; client components own interaction behavior and emit events.
- For every independently server-driven component, load `server-driven-component-contract` and specify mode, identity, HTTP method/URI or SSE stream, authorization, inputs/headers/body/content types, cache behavior, target/swap or event targets, complete fragment/event data, loading/empty/pending/error/recovery states, preservation behavior, and structural-update behavior. For HTMX automatic refresh specify trigger, exact interval, and override rule; SSE has reconnect behavior, not a polling interval. Mark values not established by authority as open questions.
- Never specify an HTMX swap inside client-component-owned DOM. Client components receive server-provided inputs and do not fetch or own backend-derived state.
