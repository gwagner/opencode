---
name: frontend-reference-examples
description: Loads one selected frontend catalog entry as non-authoritative implementation guidance without adapting code.
classification: non-technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
inputs:
  - caller-provided permitted selected catalog entry path
  - approved behavior
---

# Frontend reference examples

## Inputs

Require a caller-provided permitted selected catalog entry path and approved behavior.

Use the selected reference as implementation guidance, not product authority. A transport contract in a reference is illustrative unless the adopting component has its own approved contract.

## Workflow

1. Verify the selected path is under the accessible catalog and corresponds to the caller's selection evidence.
2. Read only the selected entry. Do not load every reference.
3. Extract applicable semantic structure, accessibility behavior, state coverage, stable hooks, interaction boundaries, responsive behavior, and limitations.
4. Separate reusable guidance from illustrative transport, identifiers, values, and fixture data. Do not turn an illustrative contract into approved behavior.
5. Report conflicts between the reference and approved behavior or repository conventions; authority and repository conventions win.
6. Do not edit code, adapt the reference, establish a server contract, capture visuals, or claim validation.

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

If the selected entry does not match, report the mismatch; do not force it onto an unrelated surface.

## Completion

Report the selected path, reusable guidance, excluded illustrative details, conflicts, limitations, and blockers.
