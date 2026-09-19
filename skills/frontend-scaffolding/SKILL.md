---
name: frontend-scaffolding
description: Scaffolds modular TypeScript, HTMX, and Tailwind frontend components under /code/src/frontend from approved specifications.
---

# Frontend scaffolding

## Deterministic workflow

```yaml
request: "Rendered frontend scaffold from approved specifications"
workflow:
  - id: "define-server-driven-contract"
    when: "Before implementing an independently server-driven component."
    skill: "server-driven-component-contract"
  - id: "apply-matching-reference"
    when: "When a matching catalog component exists."
    skill: "frontend-reference-examples"
  - id: "implement-htmx"
    when: "When the scaffold includes HTMX work."
    skill: "htmx"
  - id: "configure-tailwind"
    when: "When Tailwind configuration or generation changes."
    skill: "tailwind"
  - id: "capture-visual-artifacts"
    when: "For each affected route runnable with documented project tooling."
    skill: "browser-visual-capture"
  - id: "compare-visual-artifacts"
    when: "After baseline and post-change artifacts are captured for a runnable affected route."
    skill: "browser-visual-compare"
```

Use only for approved frontend scaffolding or a modification to a rendered frontend component. Work only under `/code/src/frontend/`.

1. Read approved specifications and repository conventions for routes, backend stack, fragment contracts, and static-asset integration. Do not invent missing behavior or contracts.
2. Every created or modified rendered component has exactly one owned root element. Use the semantically correct element when one applies (`article`, `nav`, `aside`, `form`, and similar); do not force a literal `<section>` or an incorrect landmark. When no semantic container applies, use `<div data-component="ComponentName">`, with the component's exact PascalCase name. Keep that component's markup, style hooks, and event wiring within its root.
3. Preserve ownership boundaries: client components own interaction behavior and emit events; HTMX owns forms, requests, errors, and server-fragment swaps. Do not swap inside a client-component-owned root. For an independently server-driven component, load `server-driven-component-contract` before implementation; do not infer incomplete contracts.
4. Load `frontend-reference-examples` only for a matching catalog component. For a bounded existing-UI alignment task, use its review-and-align mode before editing. Load `htmx` for HTMX work and `tailwind` when Tailwind configuration or generation changes.
5. Identify affected user-visible routes. If none are affected, record `Visual validation: not applicable`. For each route runnable with documented project tooling, load `browser-visual-capture` and `browser-visual-compare`, derive structured expectations from approved acceptance criteria, and run both workflows; failed expectations or comparison errors fail validation. For an unrunnable affected route, follow the capture skill's gap workflow and report `Visual validation: blocked`; do not substitute manual screenshot judgment or report it as passed.
6. If a required API, fragment, stream, or static-asset route is missing, do not implement backend code or invent a contract. Report a bounded backend implementation handoff containing the needed contract and acceptance criteria.
