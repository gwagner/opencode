# Frontend component references

Read only the component document matching the requested surface.

| Component | Aliases and triggers | Use for |
| --- | --- | --- |
| [Line graph](references/line-graph.md) | graph, chart, time-series chart, line chart, check-result graph, metric visualization, range selector | An accessible, caller-supplied time-series visualization with optional range controls and status feedback. |
| [Data table](references/data-table.md) | table, results table, history table, paginated table, actionable rows, SSE, background refresh, live rows | A native collection with optional hybrid HTMX structural reconciliation and per-row SSE `outerHTML` updates. |
| [On-off switch](references/on-off-switch.md) | toggle switch, boolean switch, active/inactive, on/off, paused/running, up/down, HTMX | An independent labelled native checkbox with a declared HTMX `PATCH` contract. |
| [Status pill](references/status-pill.md) | badge, status badge, kind badge, resource kind, label pill, identifier pill, HTMX refresh | An independent non-interactive compact label with a declared HTMX polling contract. |

## Adding a reference

Use one lowercase hyphenated Markdown file per component. Follow the component-document contract in [`SKILL.md`](SKILL.md), add one catalog row here, and distinguish illustrative fixtures from authoritative API contracts.
