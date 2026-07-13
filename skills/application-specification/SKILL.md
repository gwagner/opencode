---
name: application-specification
description: Defines the common structure, rigor, terminology, and output rules for implementation-ready application specifications.
compatibility: opencode
metadata:
  domain: software-architecture
  artifact: application-specification
---

# Application specification

Use this skill whenever producing or materially revising an application specification.

## Objective

Produce a product-oriented, implementation-ready specification. Describe the application engineers must build or the application demonstrably represented by the source material.

Do not produce a package inventory, generic architecture essay, or aspirational product brief.

## Required minimum content

Include, when relevant:

1. Document metadata
2. Executive summary
3. Product and business context
4. Goals and non-goals
5. Actors, user roles, and permissions
6. User stories or use cases
7. End-to-end workflows
8. Functional requirements
9. System architecture
10. Component breakdown
11. Backend design
12. Frontend design
13. Data model
14. API contracts
15. External integrations
16. Webhook processing
17. State and funnel models
18. Validation, errors, and edge cases
19. Security, privacy, and audit
20. Deployment and operations
21. Risks, assumptions, gaps, and open questions
22. Recommended implementation phases, when requested or justified
23. Traceability matrix

At minimum, always include:

- Executive summary
- Architecture overview
- Functional requirements
- Data model
- Backend and API design
- Frontend and component design
- Workflow and state model
- Risks and open questions

## Writing requirements

- Use clear Markdown headings.
- Use concise prose and tables where comparison matters.
- Assign stable identifiers to important requirements, such as `FR-LEAD-001`.
- Define exact entities, fields, endpoints, states, triggers, and UI surfaces.
- Use repository or requirements terminology unless it is ambiguous.
- Define ambiguous terms in a glossary.
- Separate present behavior, intended behavior, recommendations, and unknowns.
- Avoid generic language such as “create an API,” “store the data,” or “build a dashboard.”
- Use “must” only for an authoritative requirement or clearly established application behavior.
- Use “should” for recommendations.
- Use “may” for optional behavior.

## Architecture principles

Unless source material explicitly requires otherwise:

- Prefer simple, maintainable architecture.
- Prefer explicit state models.
- Prefer transactional and auditable persistence.
- Prefer idempotent webhook and event processing.
- Avoid unnecessary distributed systems, queues, services, or frameworks.
- Preserve future extensibility without speculative abstraction.

## Output location

Write completed specifications under `/project/specification/`.

Use the `okf-formatter` skill for all final documents. Use `okf-reader` when reviewing existing knowledge documents.
