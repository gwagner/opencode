---
name: server-driven-component-contract
description: Defines explicit backend contracts for independently server-driven frontend components using HTMX or Server-Sent Events.
classification: non-technical
opencode_permission:
  read: allow
  question: allow
  skill:
    grillme: allow
inputs:
  - one component capability
  - caller-provided permitted approved or observed transport authority paths
---

# Server-driven component contract

## Inputs

Require one component capability and caller-provided permitted approved or observed transport authority paths.

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
4. Define every response: success status; response content type and cache headers; complete HTML fragment or SSE event-data schema; validation/action/transport failure behavior; explicit loading, populated, empty, pending, error, recovery, and last-known-good behavior; status announcement; focus behavior; and retry, stop, or recovery behavior.
5. For **HTMX**, define trigger and exact interval when automatic. A cadence must state its default and whether implementation may override it.
6. Define the owning refresh boundary and preservation behavior for applicable draft input, selection, pagination, filters, ranges, modal identity, focus, scroll, last-known-good content, and unaffected siblings.
7. For **SSE**, define stream URI, `text/event-stream`, cache policy, reconnect behavior including `Last-Event-ID` and `retry`, event names, event data, per-element targets, and behavior for insertion, removal, ordering, pagination, and other structural changes. SSE has no polling interval. For an HTMX SSE extension integration, require `hx-ext="sse"` and `sse-connect` on the same element; place each `sse-swap` listener on that element or a descendant; match named events exactly; use `message` for unnamed events; and define any `sse-close` event.
8. For every `hx-trigger="sse:<event-name>"` callback, define the triggering event and the resulting HTTP request under the request contract.
9. Verify the template attributes, presentation model, backend route, response fragment, and tests use identical names and contracts. Backend code owns authorization, validation, mutations, data selection, and rendering; client components do not reconstruct server state.

## Required contract record

Record these fields in the component reference or approved specification:

| Field | Required content |
| --- | --- |
| Mode | HTMX or SSE; capability covered |
| Identity | Component/element ID, encoded path variables, fragment root |
| Request or stream | Method and URI; auth; inputs/headers/body/content type; cache behavior |
| Refresh | HTMX trigger/interval and override rule, or SSE reconnect/event rules |
| Success | Status, response headers/content type, complete fragment or event-data contract, target/swap |
| Failures | Validation, action, transport, loading/empty/pending/error, last-known-good, visible feedback, focus, retry/stop/recovery |
| Preservation | Refresh boundary; applicable input, selection, page/filter/range, modal, focus, scroll, and sibling behavior |
| Structural changes | Explicitly supported or separately routed; mandatory for SSE |
| Evidence/status | Source, approved/proposed/observed status, assumptions/open questions |

## Completion

Do not scaffold a server-driven component or its backend route while required fields are absent. Create a bounded specification handoff or ask the blocking question instead.
