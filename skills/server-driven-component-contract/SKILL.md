---
name: server-driven-component-contract
description: Defines explicit backend contracts for independently server-driven frontend components using HTMX or Server-Sent Events.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: server-driven-component-contract
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: server-driven-component-contract
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: server-driven-component-contract
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: server-driven-component-contract
    - agent: frontend-reference-builder
      source: /code/agents/frontend-reference-builder.md
      allowed_skill: server-driven-component-contract
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: server-driven-component-contract
inputs:
  - one component capability
  - approved or observed transport authority
---

# Server-driven component contract

## Deterministic workflow

```yaml
request: "Explicit approved server-driven component contract"
workflow:
  - id: "clarify-missing-contract"
    when: "When mode or a required contract value is missing and the agent may ask."
    skill: "grillme"
```

Use when a frontend component independently requests, mutates, or receives server-derived presentation data through HTMX or SSE. The approved component contract is normative for its backend implementation; styling and illustrative fixture data remain adaptable.

## Procedure

1. Select exactly one mode per component capability: **HTMX** for a request/response interaction or polling refresh; **SSE** for server-pushed background updates. When mode or a required contract value is missing, ask via `grillme` only when the agent may do so; otherwise record a blocking specification gap or handoff. Mark a user-proposed, unapproved contract as proposed; do not present it as implemented behavior.
2. Define the stable component and swap identities: component ID, URI path-variable encoding, fragment root, target, and swap mode. A returned fragment must retain the identity when it represents the same component or element.
3. Define every HTTP request: method; URI template; authorization; path, query, and header values; body schema and content type; and request cache behavior.
4. Define every response: success status; response content type and cache headers; complete HTML fragment or SSE event-data schema; validation/action/transport failure behavior; visible loading/error state; focus behavior; and retry, stop, or recovery behavior.
5. For **HTMX**, define trigger and exact interval when automatic. A cadence must state its default and whether implementation may override it.
6. For **SSE**, define stream URI, `text/event-stream`, cache policy, reconnect behavior including `Last-Event-ID` and `retry`, event names, event data, per-element targets, and behavior for insertion, removal, ordering, pagination, and other structural changes. SSE has no polling interval.
7. Verify the template attributes, presentation model, backend route, response fragment, and tests use identical names and contracts. Backend code owns authorization, validation, mutations, data selection, and rendering; client components do not reconstruct server state.

## Required contract record

Record these fields in the component reference or approved specification:

| Field | Required content |
| --- | --- |
| Mode | HTMX or SSE; capability covered |
| Identity | Component/element ID, encoded path variables, fragment root |
| Request or stream | Method and URI; auth; inputs/headers/body/content type; cache behavior |
| Refresh | HTMX trigger/interval and override rule, or SSE reconnect/event rules |
| Success | Status, response headers/content type, complete fragment or event-data contract, target/swap |
| Failures | Validation, action, transport, loading, visible feedback, focus, retry/stop/recovery |
| Structural changes | Explicitly supported or separately routed; mandatory for SSE |
| Evidence/status | Source, approved/proposed/observed status, assumptions/open questions |

## Completion

Do not scaffold a server-driven component or its backend route while required fields are absent. Create a bounded specification handoff or ask the blocking question instead.
