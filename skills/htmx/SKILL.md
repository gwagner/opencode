---
name: htmx
description: Implements HTMX server-fragment requests, form actions, errors, loading states, and safe swap ownership.
---

# HTMX

## Deterministic workflow

```yaml
request: "HTMX server-rendered interaction with safe swap ownership"
workflow:
  - id: "define-server-driven-contract"
    when: "Before implementing an independently server-driven component."
    skill: "server-driven-component-contract"
```

Use for HTMX server-rendered HTML interactions. For independently server-driven components, load `server-driven-component-contract` first. That skill owns SSE contracts.

1. Define each request method, URI template and encoded path variables, authorization, query/header/body schema, request content type, cache behavior, response status/content type/cache headers, complete response fragment, target, and swap mode.
2. For every automatic HTMX refresh, define its trigger, exact interval, default/override rule, loading state, failure rendering, and retry or stop behavior. Record any unspecified value as an open question; do not infer it from the component.
3. Keep validation, authorization, mutations, and resulting server state backend-authoritative.
4. Define loading and error rendering for each request; return fragments compatible with the declared target.
5. Give every swappable region one owner. Do not target, replace, or morph DOM inside a client-component-owned root.
6. Pass server data to client components only through declared inputs; consume component events at a boundary outside the component. Verify the rendered `hx-*` attributes, backend route, payload, response fragment, and tests match the declared contract.
