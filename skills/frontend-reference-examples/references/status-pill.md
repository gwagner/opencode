---
type: component-reference
title: Status pill
description: Adaptable, non-interactive inline label for a caller-classified status, kind, or identifier.
tags:
  - frontend
  - component
  - status
  - badge
timestamp: 2026-09-06
---

# Status pill

## Match

- **Component:** Status pill. **Aliases:** badge, status badge, kind badge, resource kind, label pill, identifier pill, HTMX refresh.
- Presents a short, already-formatted status, kind, or identifier with a caller-selected color tone. Suitable in cards, tables, detail headers, and compact metadata.
- Do not use for actions, filters, toggles, notifications, multi-select tokens, or a long/unbounded value. Use a button/filter control, alert, tag editor, or data table instead.
- This is adaptable implementation material, not product authority.

## Ownership and behavior contract

- Owns one non-interactive visible label, optional accessible description, pill shape, and caller-selected visual tone.
- The caller supplies formatted `Label`, `Tone`, optional `Description.Text`, visibility, and a stable `ID`. It presents them only; it must not infer status, translate identifiers, normalize casing, or map domain values to tones. Its declared HTMX refresh is the sole request behavior.
- **Events:** Not applicable: a status pill is not interactive and emits no event. It neither moves focus nor owns feedback.
- **Illustrative HTMX refresh template — not an approved adopter contract:** `GET /ui/components/v1/status-pills/{id}` every 10 seconds (`hx-trigger="every 10s"`). `{id}` is the URL-path-encoded `ID`; the request has no body and carries HTMX's `HX-Request: true` header. It targets `[data-status-pill-region]` and swaps `outerHTML`. `200 OK` returns `Content-Type: text/html`, `Cache-Control: no-store`, and one complete region rendered from `StatusPillView` with the same `ID`. A recoverable application failure returns `200 OK` with that complete region, a caller-formatted neutral label, and an optional visible description; transport failures remain HTTP errors and must be announced by the HTMX owner without replacing a truthful existing pill. The server owns authorization, data lookup, rendering, and all resulting state. The 10-second cadence is the reference default; an adopter may use it only when approved for that component.
- Composition: use inline text only; do not nest links, buttons, inputs, headings, or other interactive content inside it. Do not use a pill as the only representation of a time-critical alert.

## Implementation-facing presentation model

```go
package presentation

// StatusPillView is the display-ready data for one non-interactive status pill.
type StatusPillView struct {
	ID          string
	Label       string
	Tone        string
	Description *StatusPillDescriptionView
	Hidden      bool
}

// StatusPillDescriptionView supplies optional extra context for assistive technology.
type StatusPillDescriptionView struct {
	Text string
}
```

- Required: `ID` is unique within its rendered document; `Label` is nonempty already-formatted visible text; `Tone` is a project-approved, CSS-safe presentation token such as `success`, `danger`, `warning`, `info`, or `neutral`.
- Optional: `Description` is nil when `Label` is sufficient. `Hidden` hides the stable update region when true.
- Invariant: callers select tone and label independently; tone never supplies business meaning without the visible label. Keep `ID` stable across parent refreshes when the same displayed item persists.
- All strings are display-ready. The caller formats/localizes labels and descriptions, supplies its fallback label, and passes untrusted text normally so `html/template` escapes it. Render `Description` only when non-nil and its text is nonempty.
- This Go model is a reusable presentation adapter, not evidence that an adopter uses Go. **Illustrative mapping:** a TypeScript renderer can use `{ id, label, tone, description?: { text }, hidden }` with the same constraints.

## Semantic template

```gohtml
{{define "status-pill"}}
  <span
    id="{{.ID}}-region"
    data-status-pill-region
    hx-get="/ui/components/v1/status-pills/{{urlquery .ID}}"
    hx-trigger="every 10s"
    hx-target="this"
    hx-swap="outerHTML"
    {{if .Hidden}} hidden{{end}}
  >
    <span
      id="{{.ID}}"
      data-status-pill
      data-status-pill-tone="{{.Tone}}"
      {{if .Description}}{{if .Description.Text}}aria-describedby="{{.ID}}-description"{{end}}{{end}}
    >
      {{.Label}}
    </span>
    {{if .Description}}{{if .Description.Text}}
      <span id="{{.ID}}-description" class="status-pill__description">{{.Description.Text}}</span>
    {{end}}{{end}}
  </span>
{{end}}
```

`data-status-pill` scopes shared styling; `data-status-pill-tone` selects only a documented visual tone. `[data-status-pill-region]` is the HTMX swap boundary for the declared URI. The conditional nonempty description and its `aria-describedby` attribute appear together. `ID` is the only path value and must be URL-path-safe or encoded by the rendering boundary.

## CSS rules

```css
/* Existing project tokens observed in supplied CSS. */
[data-status-pill] {
  --status-pill-surface: var(--eo-pill-neutral-surface);
  --status-pill-border: var(--eo-pill-neutral-border);
  --status-pill-text: var(--eo-pill-neutral-text);
  display: inline-block;
  max-inline-size: 100%;
  overflow-wrap: anywhere;
  border: 1px solid var(--status-pill-border);
  border-radius: 9999px;
  background: var(--status-pill-surface);
  color: var(--status-pill-text);
  padding: .25rem .625rem;
  font-size: .75rem;
  font-weight: 800;
  line-height: 1.25;
}

[data-status-pill-tone="success"] { --status-pill-surface: var(--eo-success-surface); --status-pill-border: var(--eo-success-border); --status-pill-text: var(--eo-success-text); }
[data-status-pill-tone="danger"]  { --status-pill-surface: var(--eo-danger-surface); --status-pill-border: var(--eo-danger-border); --status-pill-text: var(--eo-danger-text); }
[data-status-pill-tone="warning"] { --status-pill-surface: var(--eo-warning-surface); --status-pill-border: var(--eo-warning-border); --status-pill-text: var(--eo-warning-text); }
[data-status-pill-tone="info"]    { --status-pill-surface: var(--eo-info-surface); --status-pill-border: var(--eo-info-border); --status-pill-text: var(--eo-info-text); }
[data-status-pill-region][hidden], [data-status-pill][hidden] { display: none; }
[data-status-pill-region][aria-busy="true"] { cursor: progress; }
[data-status-pill-region].htmx-request { opacity: .7; }
.status-pill__description { position: absolute; inline-size: 1px; block-size: 1px; margin: -1px; overflow: hidden; clip: rect(0, 0, 0, 0); white-space: nowrap; }

@media (max-width: 40rem) {
  [data-status-pill] { white-space: normal; }
}
```

`--status-pill-*` name surface, border, and text roles; override them per container only when a documented tone is insufficient. No motion or keyboard focus applies because this is not interactive. The `[hidden]` selector supports parent-owned visibility.

## JavaScript example

Not applicable: the component has no client-side presentation interaction, input handling, emitted event, pointer/keyboard behavior, or focus handling.

## Illustrative view data

```go
package presentation

var ExampleStatusPill = StatusPillView{
	ID:    "status-pill-example",
	Label: "Resolved",
	Tone:  "success",
	Description: &StatusPillDescriptionView{
		Text: "No further action is currently required.",
	},
}

var ExampleKindPill = StatusPillView{
	ID:    "kind-pill-example",
	Label: "response_time",
	Tone:  "neutral",
}
```

Non-authoritative: these establish no endpoint, domain schema, field name, enum, sorting, filtering, pagination, or business rule.

## States and failures

| State | Visibility | Announcement | Focus | Recovery | Boundary |
| --- | --- | --- | --- | --- | --- |
| Loading | HTMX applies `.htmx-request`; retain the visible label. | Parent-owned status region, only when useful. | Unchanged. | Next 10-second refresh. | HTMX/server. |
| Success | Render label and selected tone. | None; status is read in normal reading order. | Unchanged. | Not applicable. | Parent/template. |
| Empty | Omit pill when no meaningful label exists. | Parent owns any empty-state message. | Unchanged. | Parent context. | Server/HTMX/parent. |
| Partial values | Render only a valid label; omit nil description. | None. | Unchanged. | Parent supplies fallback label or omits it. | Parent. |
| Request failure | Retain a truthful prior region for transport failure; server returns a complete neutral/error-compatible region for recoverable application failure. | Parent error region. | Unchanged. | Automatic next refresh or parent retry. | HTMX/server. |
| Action failure | Do not optimistically recolor this passive component. | Parent action-error region. | Parent restores action focus. | Parent retry/correction. | Server/HTMX/parent. |

## Accessibility and responsive checks

- Use a `span`; its visible label is its accessible text. Add the optional description only for essential extra context.
- No keyboard operation, focus target, live region, or disabled state applies. Do not add `role="status"` merely to announce every passive change.
- Pair color with the visible label; ensure tone contrast meets project requirements. Never convey a critical condition by color alone.
- Verify adjacent controls retain at least adequate target size; the pill itself is not a target. At 200% zoom and narrow widths, it wraps/breaks long labels without clipping or horizontal inaccessible overflow.

## Adaptation and test checklist

- Replace/confirm illustrative labels, IDs, the `success`/`neutral` tones, `--status-pill-*` overrides, and optional descriptions. Confirm the approved tone vocabulary and any dark-mode token values.
- Test normal, hidden, nil-description, long-label, localized-label, unknown-tone fallback, loading/empty, request-failure, and action-failure contexts.
- Test no pointer or keyboard interaction/event is introduced; verify the rendered text, description linkage, semantic `span`, escaping, contrast, zoom, and narrow layout.
- Test `GET /ui/components/v1/status-pills/{id}`: empty request body, `HX-Request: true`, `text/html`/`no-store` response, 10-second trigger, `outerHTML` target/swap, success fragment, recoverable-error fragment, and transport-failure announcement. Verify whole-region replacement preserves the region ID for the same displayed item. Where supported, capture runnable-route visual evidence for each adopted tone.

## Provenance and limitations

- **User-supplied intent:** one reusable pill for `data-resource-kind` and `data-status-badge`, with changeable colors.
- **User-supplied contract intent (2026-09-06):** the pill independently uses HTMX refresh; component documents define server presentation contracts.
- **Observed supplied CSS:** existing `--eo-pill-*`, semantic success/danger/warning/info tokens, `[data-resource-kind]`, `[data-status-badge]`, and `[data-status]` selectors.
- **Reference design decisions:** generic `[data-status-pill]` and four semantic tones replace per-domain selector duplication; neutral remains the base. The exact tone vocabulary and mappings are unverified.
- Intentionally unsupported: interactive filters, icon-only pills, count/remove tokens, automatic status-to-color mapping, client-side swaps, and component-owned HTMX request configuration.
- Reference date: 2026-09-06; supplied CSS behavior may change.
