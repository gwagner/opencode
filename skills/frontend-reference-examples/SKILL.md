---
name: frontend-reference-examples
description: Finds reusable HTML, CSS, JavaScript, accessibility, and example-data references for matching frontend components. Use when implementing or revising a UI component represented in this skill's catalog.
---

# Frontend reference examples

Use these references as implementation aids, not product authority.

## Workflow

1. Read [`index.md`](index.md) and match the requested surface by component name, alias, purpose, or interaction.
2. Read only the matching component document. Do not load every reference.
3. Confirm approved requirements, specifications, repository conventions, and existing components before adapting an example. Those sources override references.
4. Reuse semantic structure, accessibility behavior, style hooks, interaction boundaries, and state coverage where applicable. Do not copy irrelevant markup or fabricate an API contract.
5. Keep server-derived data outside client-component state. Example JavaScript may render caller-provided data and emit interaction events, but it must not fetch server data. HTMX or the existing server layer owns requests, errors, fragments, and swaps.
6. Preserve stable `data-*` hooks only when they serve styling, testing, behavior, or integration. Do not treat sample identifiers or values as production data.
7. Validate the adapted component with project-native checks and the frontend agent's visual-validation workflow.

## Reference document contract

Each component document should include, when applicable:

- names, aliases, intent, and unsuitable uses;
- semantic HTML template;
- styleable CSS and documented custom properties;
- JavaScript inputs, emitted events, focus behavior, and ownership boundary;
- clearly labelled illustrative API or fixture data;
- loading, empty, success, partial, and error states;
- responsive and accessibility behavior;
- adaptation and test checklists;
- provenance and limitations.

If no reference matches, follow approved project conventions. Do not force the nearest example onto an unrelated surface.
