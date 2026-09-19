---
name: htmx
description: Implements HTMX server-fragment requests, form actions, errors, loading states, and safe swap ownership.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: htmx
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: htmx
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: htmx
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: htmx
inputs:
  - approved HTMX interaction contract
  - affected route and fragment
---

# HTMX

## Deterministic workflow

```yaml
request: "HTMX server-rendered interaction with safe swap ownership"
workflow:
  - id: "define-server-driven-contract"
    when: "Before implementing an independently server-driven component."
    skill: "server-driven-component-contract"
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Use for HTMX server-rendered HTML interactions. For independently server-driven components, load `server-driven-component-contract` first. That skill owns SSE contracts.

1. Define each request method, URI template and encoded path variables, authorization, query/header/body schema, request content type, cache behavior, response status/content type/cache headers, complete response fragment, target, and swap mode.
2. For every automatic HTMX refresh, define its trigger, exact interval, default/override rule, loading state, failure rendering, and retry or stop behavior. Record any unspecified value as an open question; do not infer it from the component.
3. Keep validation, authorization, mutations, and resulting server state backend-authoritative.
4. Define loading and error rendering for each request; return fragments compatible with the declared target.
5. Give every swappable region one owner. Do not target, replace, or morph DOM inside a client-component-owned root.
6. Pass server data to client components only through declared inputs; consume component events at a boundary outside the component. Verify the rendered `hx-*` attributes, backend route, payload, response fragment, and tests match the declared contract.
