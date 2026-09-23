---
name: htmx
description: Implements HTMX server-fragment requests, form actions, errors, loading states, and safe swap ownership.
classification: technical
opencode_permission:
  read: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - approved HTMX interaction contract
  - affected route and fragment
  - caller-provided permitted implementation paths
---

# HTMX

## Inputs

Require an approved HTMX interaction contract, affected route and fragment, and caller-provided permitted implementation paths.

## Dead-code rule

Within the approved affected source and test scope, remove unused functions and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "HTMX server-rendered interaction with safe swap ownership"
workflow:
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Use for HTMX server-rendered HTML interactions only after the caller establishes any required independently server-driven component contract. This skill does not own SSE contracts.

1. Define each request method, URI template and encoded path variables, authorization, query/header/body schema, request content type, cache behavior, response status/content type/cache headers, complete response fragment, target, and swap mode.
2. For every automatic HTMX refresh, define its trigger, exact interval, default/override rule, loading state, failure rendering, and retry or stop behavior. Record any unspecified value as an open question; do not infer it from the component.
3. Keep validation, authorization, mutations, and resulting server state backend-authoritative.
4. Define loading and error rendering for each request; return fragments compatible with the declared target.
5. Give every swappable region one owner. Do not target, replace, or morph DOM inside a client-component-owned root.
6. Pass server data to client components only through declared inputs; consume component events at a boundary outside the component. Verify the rendered `hx-*` attributes, backend route, payload, response fragment, and tests match the declared contract.
