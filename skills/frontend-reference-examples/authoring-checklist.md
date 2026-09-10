# Catalog authoring checklist

For catalog authors only. Create one lowercase-hyphenated component document and its index row at a time. Use these headings in order; write `Not applicable:` with a reason rather than omitting a heading.

1. **Match** — name, aliases, user problem, suitable/unsuitable contexts, near neighbors, and non-authoritative status.
2. **Ownership and behavior contract** — regions, controls, caller data, emitted events and focus; assign requests, loading, errors, navigation, dialogs, and swaps to their owner. For independent HTMX/SSE behavior, use `server-driven-component-contract`.
3. **Implementation-facing presentation model** — documented, exported `package presentation` Go view types; display-ready fields, IDs, optionality, invariants, formatting, localization, escaping, and rendering rules. Keep domain, transport, and database objects out.
4. **Semantic template** — complete adaptable `gohtml` consuming that model, with semantic accessible structure, required/optional regions, feedback, and only purposeful stable hooks.
5. **CSS rules** — styleable selectors, project tokens or labelled generic properties, states, focus, narrow layouts, and reduced motion when applicable.
6. **JavaScript example** — only for presentation interaction; specify lifecycle, inputs, emitted events, keyboard/pointer behavior, and focus. Never fetch, own server state, or swap fragments.
7. **Illustrative view data** — a small non-authoritative Go fixture using the documented view model.
8. **States and failures** — loading, success, empty, partial, request/action failure; visibility, announcements, focus, recovery, and responsible boundary.
9. **Accessibility and responsive checks** — semantics, names, keyboard/focus behavior, announcements, alternatives, disabled behavior, color-independent meaning, target size, zoom, and overflow.
10. **Adaptation and test checklist** — values and behaviors to confirm; normal/boundary, input, event, accessibility, responsive, and server/HTMX tests; runnable-route visual evidence where supported.
11. **Provenance and limitations** — sources, observed versus supplied intent, reference decisions, assumptions, unsupported variations, and source date when applicable.

Before finalizing, make the filename, title, aliases, index row, events, model, selectors, and fixture consistent. Requirements, specifications, and repository conventions override references. Mark missing authority as proposed; never present it as production behavior. Report changed paths, evidence, assumptions, and blockers.
