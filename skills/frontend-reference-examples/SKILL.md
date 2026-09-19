---
name: frontend-reference-examples
description: Finds reusable HTML, CSS, JavaScript, accessibility, and example-data references for matching frontend components. Use when implementing or revising a UI component represented in this skill's catalog.
---

# Frontend reference examples

## Deterministic workflow

```yaml
request: "Approved frontend reference adaptation or bounded UI alignment"
workflow:
  - id: "define-server-driven-contract"
    when: "When adapting an independently server-driven component."
    skill: "server-driven-component-contract"
  - id: "capture-visual-artifacts"
    when: "When validating a runnable adapted or aligned route."
    skill: "browser-visual-capture"
  - id: "compare-visual-artifacts"
    when: "After baseline and post-change visual artifacts are captured."
    skill: "browser-visual-compare"
```

Use these references as implementation aids, not product authority. A transport contract in a reference is an illustrative template unless the adopting component has its own approved server-driven contract; only that adopted contract is normative.

## Workflow

1. Read [`index.md`](index.md) and match the requested surface by component name, alias, purpose, or interaction.
2. Read only the matching component document. Do not load every reference.
3. Confirm approved requirements, specifications, repository conventions, and existing components before adapting an example. Those sources override references.
4. Reuse semantic structure, accessibility behavior, style hooks, interaction boundaries, and state coverage where applicable. For an independently server-driven component, load `server-driven-component-contract` and implement its declared transport contract exactly. Do not copy irrelevant markup or fabricate an unapproved contract.
5. Keep server-derived data outside client-component state. Example JavaScript may render caller-provided data and emit interaction events, but it must not fetch server data. HTMX or the existing server layer owns requests, errors, fragments, and swaps.
6. Preserve stable `data-*` hooks only when they serve styling, testing, behavior, or integration. Do not treat sample identifiers or values as production data.
7. Validate the adapted component with project-native checks, deterministic `browser-visual-capture` artifacts, and `browser-visual-compare` expectations derived from approved acceptance criteria.

## Review and align existing UI

Use this mode only for a requested, bounded set of existing routes or components.

1. Inspect the existing component and its affected route before selecting a reference. Confirm authoritative requirements, specifications, and repository conventions.
2. Match each surface to one catalog document by purpose and interaction. Record no match rather than forcing a near match.
3. Compare semantic structure, accessible names and keyboard behavior, responsive behavior, loading/empty/error states, presentation ownership, and documented stable hooks. Preserve authoritative behavior that differs from the reference.
4. Classify each delta: safe presentation alignment; approved behavior implementation; or authority/contract gap. Do not change a server, HTMX, or SSE contract from an illustrative reference unless that contract is approved for the adopting surface.
5. Apply the smallest safe change per component. When runnable, validate the affected route with project-native checks plus baseline/post-change capture and structured comparison; otherwise record the concrete visual-validation gap.

For each aligned surface, report the matched reference path, retained behavior, changes made, intentionally deferred differences, validation, and blockers.

## Reference document contract

Each component document should include, when applicable:

- names, aliases, intent, and unsuitable uses;
- semantic HTML template;
- styleable CSS and documented custom properties;
- JavaScript inputs, emitted events, focus behavior, and ownership boundary;
- a clearly labelled illustrative server-driven transport template, when the component independently uses HTMX or SSE: mode, URI/method or stream, identity, inputs, headers/body/content type, cache behavior, fragment/event data, target/swap, failures, and refresh behavior;
- clearly labelled illustrative API or fixture data;
- loading, empty, success, partial, and error states;
- responsive and accessibility behavior;
- adaptation and test checklists;
- provenance and limitations.

If no reference matches, follow approved project conventions. Do not force the nearest example onto an unrelated surface.

## Catalog authoring

Only when creating or revising a catalog reference, read [`authoring-checklist.md`](authoring-checklist.md). It is not needed when adapting a reference.
