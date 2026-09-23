---
name: specification-quality-gate
description: Performs a final completeness, consistency, evidence, stack, workflow, API, data, frontend, security, and implementation-readiness review.
classification: non-technical
opencode_permission:
  read: allow
  skill:
    okf-formatter: allow
inputs:
  - draft specification
  - intended authority or evidence mode
  - permitted destination
compatibility: opencode
metadata:
  domain: quality-assurance
---

# Specification quality gate

## Inputs

Require a draft specification, intended authority or evidence mode, and permitted destination.

## Deterministic workflow

```yaml
request: "Final implementation-ready specification quality review"
workflow:
  - id: "format-final-specification"
    when: "When producing the final specification output."
    skill: "okf-formatter"
```

Run this skill immediately before finalizing specification documents.

## Completeness

Confirm:

- Product objective is clear.
- Actors and permissions are defined.
- Major use cases are end to end.
- Functional requirements have stable IDs.
- Architecture boundaries are concrete.
- Major entities and fields are defined.
- API operations are concrete.
- Frontend screens and components are concrete or explicitly absent.
- Each independently server-driven component has an explicit contract: mode, stable identity, HTTP method/URI or SSE stream, authorization, inputs/headers/body/content types, cache behavior, response fragment/event data, target/swap or event targets, loading/error/recovery, and implementation tests. HTMX automatic refreshes define trigger/interval/default-override behavior; SSE defines reconnect, event, and structural-update behavior without a polling interval.
- State transitions have triggers and entry criteria.
- Validation and failure recovery are described.
- Security and operational concerns are addressed.
- Forward-designed end-user interactions define environment-specific diagnostic and production-business logging modes, a named configuration variable with safe defaults and validation, permitted events and fields, privacy controls, volume and retention controls, verification, and controlled production override behavior. Reverse-engineered specifications classify observed evidence and any absence as a gap without asserting unobserved behavior.
- Required browser interaction logging defines a shared frontend emitter, backend-owned effective mode and catalog, bounded same-origin ingestion command, authentication and request protection, untrusted-input validation and redaction, trusted server enrichment, structured application-logger emission, deployment-owned sink routing, failure isolation, and frontend, backend, and release verification.
- Risks, assumptions, gaps, and open questions are visible.
- Traceability exists for material claims.

## Consistency

Check:

- State names match across workflow, API, data, and UI sections.
- Entity and field names are consistent.
- Endpoint requests and responses align with the data model.
- Permissions align across actors, APIs, and screens.
- Webhook behavior aligns with persistence and state changes.
- Implementation phases do not contradict dependencies.
- Recommendations are not presented as current behavior.

## Stack

For forward design, verify the required or preferred stack is reflected.

For reverse engineering, verify the actual stack is described and preferred technologies were not imposed.

## Evidence

For reverse-engineered specifications verify:

- Entry points and runtime wiring were inspected.
- Routes are registered and reachable.
- Migrations were read in order.
- Tests were inspected or executed.
- Interfaces were not mistaken for implementation.
- Placeholder behavior is labeled.
- Confidence and source references are present.

## Final output

Use `okf-formatter`.

Write only to the workflow's declared, permitted specification destination. If no workflow destination is declared, default to `/project/specification/`.

Return a concise completion summary listing:

- Files created or updated
- Capabilities covered
- Confidence
- Major gaps
- Important open questions
- Validation performed
- Analysis limitations
