---
name: lit-components
description: Implements TypeScript Lit components with server-provided inputs, custom-event outputs, and accessible interaction behavior.
---

# Lit components

Use for Lit component implementation.

1. Define typed public properties for server-provided inputs and document custom events at the component boundary.
2. Keep reactive state presentation-only: focus, expanded state, client validation display, and pending interaction state are allowed. Do not fetch data or own server-derived data state.
3. Use semantic HTML, labels, keyboard interaction, focus management, and accessible names.
4. Emit events for actions; let the containing server/HTMX flow own requests and state transitions.
5. Treat each Lit root as DOM owned by Lit. HTMX may target a sibling or parent-owned region, never component internals.
