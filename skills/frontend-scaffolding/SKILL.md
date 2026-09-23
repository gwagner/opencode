---
name: frontend-scaffolding
description: Implements a bounded rendered frontend surface from an approved contract using the project's established templates, components, assets, and delivery path.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  question: allow
  skill:
    server-driven-component-contract: allow
    grillme: allow
    frontend-reference-lookup: allow
    frontend-reference-examples: allow
    htmx: allow
    tailwind: allow
    project-validation: allow
inputs:
  - approved frontend contract
  - affected component route and caller-provided permitted paths
  - approved source generation packaging and serving contract
---

# Frontend scaffolding

## Inputs

Require an approved frontend contract, affected component, route and caller-provided permitted paths, and approved source, generation, packaging and serving contract.

## Dead-code rule

Within the approved affected source and test scope, remove unused functions and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "Rendered frontend implementation from an approved contract"
workflow:
  - id: "define-server-driven-contract"
    when: "Before implementing an independently server-driven component."
    skill: "server-driven-component-contract"
  - id: "select-matching-reference"
    when: "Before implementation when an accessible reference catalog exists."
    skill: "frontend-reference-lookup"
  - id: "load-matching-reference"
    when: "After lookup selects a matching catalog entry."
    skill: "frontend-reference-examples"
  - id: "implement-htmx"
    when: "When the rendered surface includes HTMX work."
    skill: "htmx"
  - id: "configure-tailwind"
    when: "When Tailwind configuration or generation changes."
    skill: "tailwind"
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Use only for approved rendered frontend implementation. Work only in caller-permitted handwritten source, template, generated-output, packaging, and test paths.

1. Read approved specifications and repository conventions for routes, backend stack, fragment contracts, and static-asset integration. Do not invent missing behavior or contracts.
2. Identify the handwritten source, generated outputs, exact project-approved regeneration command, one packaging or embed owner, and production serving route. Edit handwritten source only; never patch generated or embedded output independently. Regenerate and verify source-to-generated-to-packaged-to-served parity.
3. Keep server-rendered documents and fragments in the project's established standalone template form. Browser code may enhance presentation and interaction but must not own authoritative domain state. Required assets must be current, same-origin, self-hosted when authority requires it, and independent of the process working directory.
4. Every created or modified rendered component has exactly one owned root element. Use the semantically correct element when one applies (`article`, `nav`, `aside`, `form`, and similar); do not force a literal `<section>` or an incorrect landmark. When no semantic container applies, use a stable project-conventional component hook. Keep that component's markup, style hooks, and event wiring within its root.
5. Preserve ownership boundaries: client components own interaction behavior and emit events; the established server-interaction layer owns forms, requests, errors, and server-fragment swaps. Do not swap inside a client-component-owned root. For an independently server-driven component, load `server-driven-component-contract` before implementation; do not infer incomplete contracts.
6. Use `frontend-reference-lookup` only to select a matching catalog entry, then use `frontend-reference-examples` to load that entry's non-authoritative guidance. Authority and repository conventions override it. Load `htmx` for HTMX work and `tailwind` when Tailwind configuration or generation changes.
7. For every asynchronous region, implement explicit initial-loading, populated, empty, pending, error, and recovery states. Empty is not error. Preserve last-known-good content and unaffected siblings after post-load failure where required.
8. Refresh only the owning boundary. Preserve applicable draft input, selection, pagination, filters, ranges, modal identity, focus, and scroll. Prefer native semantics, shared components and tokens, stable behavior-oriented hooks, visible focus, and one accessible action path.
9. When the approved contract requires interaction logging, use one shared frontend emitter and backend-supplied effective mode and event catalog. Emit only versioned allowlisted events and fields through the approved same-origin ingestion command. Enforce bounded queue, batch, field, retry, and flush behavior; never send raw input, payload, rendered content, credentials, session identifiers, personal or regulated data, or client-selected identity, tenant, environment, severity, or sink. Telemetry failure MUST NOT block or alter the user workflow, trigger recursive telemetry, or fall back to sensitive console output.
10. Classify browser impact by dependency closure rather than changed-file location. The calling code-editing workflow owns the later browser-impact gate for every direct or indirect browser-visible effect; this skill cannot claim browser-impact completion. Generic screenshots or pixel thresholds are diagnostic only.
11. If a required API, fragment, stream, interaction-log ingestion, static-asset route, generation command, packaging owner, or serving contract is missing, do not invent it. Report a bounded implementation or specification handoff.
