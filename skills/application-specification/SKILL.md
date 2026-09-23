---
name: application-specification
description: Defines the common structure, rigor, terminology, and output rules for implementation-ready application specifications.
classification: non-technical
opencode_permission:
  read: allow
  skill:
    okf-reader: allow
    okf-formatter: allow
inputs:
  - specification scope
  - requirements or code evidence
  - permitted destination
compatibility: opencode
metadata:
  domain: software-architecture
  artifact: application-specification
---

# Application specification

## Inputs

Require a specification scope, requirements or code evidence, and a permitted destination.

## Deterministic workflow

```yaml
request: "Implementation-ready application specification"
workflow:
  - id: "read-existing-knowledge"
    when: "When reviewing existing knowledge documents."
    skill: "okf-reader"
  - id: "format-final-documents"
    when: "When writing final specification documents."
    skill: "okf-formatter"
```

Use this skill whenever producing or materially revising an application specification.

## Objective

Produce a product-oriented, implementation-ready specification. Describe the application engineers must build or the application demonstrably represented by the source material.

Do not produce a package inventory, generic architecture essay, or aspirational product brief.

## Required content and document boundaries

Deliver the applicable concerns below as linked, independently retrievable OKF concepts. Do not assemble them as sections of one omnibus specification.

- Product context, goals, and non-goals
- Actors, roles, permissions, and use cases
- Functional requirements
- One architecture or component boundary per concept
- One workflow or state model per concept
- One data model, API contract, integration, webhook, or frontend surface per concept
- Validation, errors, and recovery for the concept they govern
- Security, privacy, audit, deployment, and operations when applicable
- Risks, assumptions, gaps, open questions, implementation phases, and traceability

Use an `index.md` to route readers to these concepts with concise descriptions. Keep each concept body at or below the 800-word default set by `knowledge-document-slicing`; only an indivisible external contract or generated artifact may exceed it, with the exception recorded in its parent index. State inapplicable or unknown concerns in the nearest relevant concept rather than creating empty documents.

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

Write completed specifications to the workflow's declared, permitted specification destination. If no workflow destination is declared, default to `/project/specification/`.

Use the `okf-formatter` skill for all final documents. Use `okf-reader` when reviewing existing knowledge documents.
