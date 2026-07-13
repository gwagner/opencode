---
name: specification-quality-gate
description: Performs a final completeness, consistency, evidence, stack, workflow, API, data, frontend, security, and implementation-readiness review.
compatibility: opencode
metadata:
  domain: quality-assurance
---

# Specification quality gate

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
- State transitions have triggers and entry criteria.
- Validation and failure recovery are described.
- Security and operational concerns are addressed.
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

Write only under `/project/specification/`.

Return a concise completion summary listing:

- Files created or updated
- Capabilities covered
- Confidence
- Major gaps
- Important open questions
- Validation performed
- Analysis limitations
