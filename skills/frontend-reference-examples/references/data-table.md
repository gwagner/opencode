# Data table

## Match

**Component:** Data table. **Aliases:** table, results table, history table, paginated table, actionable rows, SSE, background refresh, live rows.

Use for a named, ordered collection whose values must remain comparable in native table semantics. It presents caller-formatted headings and inert cells, an optional whole-row action, a named overflow boundary, and parent-supplied states, pagination, recovery, and dialog integration. Suitable for operational results and histories; not for editable grids, spreadsheets, trees, card lists, charts, or an append-only live log. Do not force pagination, a dialog, a parent table shell, or a feature-specific refresh policy into this reference.

This is adaptable implementation material, not product authority. Requirements, approved specifications, and adopting-project conventions override it.

## Ownership and behavior contract

Visible regions: caller-selected heading level, summary, named focusable overflow wrapper, native table, parent shell/card treatment, parent feedback/status/empty/recovery areas, optional pagination, and optional dialog-host hook. Optional capabilities: row activation and SSE incremental row refresh.

- The caller supplies already localized/formatted title, summary, scroll name, headings, ordered cell parts, labels, fallback copy, actions, pagination, recovery descriptor, and stable IDs. The component only presents them. It must not interpret domain values, HTML, status meaning, dates, ordering, authorization, eligibility, or navigation targets.
- Cell parts are ordered and allowlisted: `text`, `strong`, `status-badge`, and `time`. They are escaped inert values, never arbitrary HTML or interactive content. `time` supplies display text and a machine-readable datetime value; it does not parse either.
- `data-table:activate`: an unmodified primary pointer-up on the same eligible row, or `Enter`/`Space` on that row; detail `{action, context, rowIdentity, tableIdentity}`. All identities are stable. No automatic focus move; parent owns resulting navigation/dialog and restoration.
- `data-table:page-activate`: enabled native paging-button activation; detail `{tableIdentity, page}` with a positive one-based integer. Parent owns request, loading, failure, replacement, and focus restoration.
- `data-table:recovery-activate`: enabled native recovery-button activation; detail `{action, context, tableIdentity}`. Parent owns retry semantics and focus after its result.
- Parent/server/HTMX owns initial render, large or structural replacement, navigation, dialogs, loading, errors, empty state, recovery, pagination, authorization, validation, fragment requests, and swaps. Client JavaScript only normalizes presentation interactions and emits events.
- Optional SSE owns only existing-row complete `<tr>` `outerHTML` updates. A structural SSE signal asks the HTMX/parent owner to reconcile; it never inserts, removes, reorders, repages, or changes columns client-side. The parent coalesces signals and must not overlap reconciliation requests.
- Do not nest links, buttons, inputs, or independently interactive content in an actionable row. Make rows with such controls inert and use a dedicated actions column.

### Server-driven contract

**Status:** user-approved reference parent contract; adoption remains subject to the adopting feature's approved authority.

| Field | Contract |
| --- | --- |
| Mode and identity | Optional SSE hybrid. Table ID is a non-empty stable token; row identity is unique within its current table. URI path value is URL-path encoded. |
| Stream | `GET /ui/components/v1/data-tables/{tableID}/events`; authorization is server-owned. Empty body; `Accept: text/event-stream`; `Cache-Control: no-cache`; reconnect sends `Last-Event-ID`. `200` is `text/event-stream` and `Cache-Control: no-cache`. |
| Cache/reconnect | Server emits `retry: 10000` unless an adopter's approved contract changes it. Keep the SSE connection open while the document is hidden. Event IDs are monotonic decimal integers within one table stream. The HTMX SSE adapter records the last accepted ID per table and rejects duplicate, malformed, or lower IDs **before** any swap, including after reconnect. |
| Row success | Event name `data-table-row-update-{tableID}-{rowIdentity}`. Data is one complete compatible `<tr>`; target is its matching row and swap is `outerHTML`. Returned markup retains row `id`, `data-data-table-row-id`, and event binding. The server selects, authorizes, formats, and renders it. |
| Structural success | Event name `data-table-structural-change-{tableID}`. Data is a complete inert signal element with the same table ID and monotonic event ID. Its `outerHTML` swap updates only the signal; JavaScript emits `data-table:structural-change` with `{tableIdentity, eventID}`. HTMX/parent coalesces this event, permits no concurrent reconciliation request, and performs the approved full structural fragment swap. |
| Failures | Stream loss retains truthful DOM and uses parent-supplied polite status while SSE reconnects. HTTP/authorization/validation failure UI, retry affordance, and focus are server/HTMX/parent-owned. No client rollback or fabricated state. |
| Structural limits | SSE cannot change rows, summary, empty state, headings, ordering, pagination, or shell. Those changes require the parent/HTMX replacement contract. SSE has no cadence; reconnect, not polling, is its refresh behavior. |

## Implementation-facing presentation model

```go
package presentation

// DataTableView contains display-ready data-table presentation values.
type DataTableView struct {
	ID               string
	Title            string
	HeadingLevel     int
	HeadingID        string
	Summary          string
	ScrollLabel      string
	Columns          []DataTableColumnView
	Rows             []DataTableRowView
	Empty            *DataTableEmptyView
	Feedback         *DataTableFeedbackView
	Pagination       *DataTablePaginationView
	Recovery         *DataTableRecoveryView
	DetailDialogHost *DataTableDetailDialogHostView
	SSE              *DataTableSSEView
	Loading          bool
	LoadingText      string
	Status           string
	CardTreatment    bool
}

// DataTableColumnView contains one ordered display-ready column heading.
type DataTableColumnView struct { Key, Label string }

// DataTableRowView contains one stable row and its optional action.
type DataTableRowView struct { Identity string; Cells []DataTableCellView; Action *DataTableRowActionView }

// DataTableCellView contains ordered inert allowlisted cell parts.
type DataTableCellView struct { Parts []DataTableCellPartView }

// DataTableCellPartView contains one text, strong, status-badge, or time part.
type DataTableCellPartView struct { Kind, Text, DateTime, StatusKind string }

// DataTableRowActionView defines an eligible whole-row activation.
type DataTableRowActionView struct { Name, Context, AccessibleLabel string }

// DataTableEmptyView contains optional parent-supplied empty-state copy.
type DataTableEmptyView struct { Title, Message string }

// DataTableFeedbackView contains parent-supplied visible feedback.
type DataTableFeedbackView struct { Title, Message string; IsError bool }

// DataTablePaginationView contains parent-owned display-ready page controls.
type DataTablePaginationView struct { AccessibleLabel, Summary string; Previous, Next DataTablePageActionView }

// DataTablePageActionView defines one native previous or next page control.
type DataTablePageActionView struct { Label string; Page int; Disabled bool }

// DataTableRecoveryView defines an optional parent-owned recovery activation.
type DataTableRecoveryView struct { Label, Action, Context string; Disabled bool }

// DataTableDetailDialogHostView defines a stable hook for a parent-owned dialog.
type DataTableDetailDialogHostView struct { ID string }

// DataTableSSEView enables the optional approved per-row SSE stream.
type DataTableSSEView struct { StreamURI, StructuralSignalID string }
```

Required: `ID`, `Title`, `HeadingLevel` (integer 1–6), `ScrollLabel`, non-empty unique column `Key`s, and one ordered cell per column in every row. `HeadingID` is optional: when blank, derive `{ID}-title`; when supplied, it must be a nonblank stable safe DOM token matching `^[A-Za-z][A-Za-z0-9_-]*$`, unique in the document, and not duplicate another emitted ID. `ID` and row identities are stable DOM/SSE-safe tokens; row identity is unique in the rendered table. Each part `Kind` is exactly `text`, `strong`, `status-badge`, or `time`; `Text` is required; `DateTime` is required only for `time`; `StatusKind` is required only for `status-badge`. Render no unknown kind. `Action`, `Empty`, `Feedback`, `Pagination`, `Recovery`, `DetailDialogHost`, and `SSE` are nil when absent. Empty output requires `Empty`; nonempty output must not render it. `LoadingText` is required when `Loading`; `CardTreatment` is explicit caller-selected presentation state, not a domain fact.

Format/localize values and fallbacks before rendering. Use `html/template`; all supplied text and attributes remain contextually escaped. This Go adapter is reusable presentation material, not evidence an adopter uses Go; an illustrative TypeScript renderer maps it to the same fields/invariants.

## Semantic template

```gohtml
{{- $titleID := .HeadingID -}}
{{- if not $titleID }}{{ $titleID = printf "%s-title" .ID }}{{ end -}}
<section id="{{ .ID }}-region" data-data-table-component data-data-table-id="{{ .ID }}" aria-labelledby="{{ $titleID }}" {{ if .Loading }}aria-busy="true"{{ end }}{{ with .SSE }} hx-ext="sse" sse-connect="{{ .StreamURI }}"{{ end }}>
  <header data-data-table-heading>
    {{ if eq .HeadingLevel 1 }}<h1 id="{{ $titleID }}">{{ .Title }}</h1>{{ else if eq .HeadingLevel 2 }}<h2 id="{{ $titleID }}">{{ .Title }}</h2>{{ else if eq .HeadingLevel 3 }}<h3 id="{{ $titleID }}">{{ .Title }}</h3>{{ else if eq .HeadingLevel 4 }}<h4 id="{{ $titleID }}">{{ .Title }}</h4>{{ else if eq .HeadingLevel 5 }}<h5 id="{{ $titleID }}">{{ .Title }}</h5>{{ else }}<h6 id="{{ $titleID }}">{{ .Title }}</h6>{{ end }}
    {{ if .Summary }}<span data-data-table-count>{{ .Summary }}</span>{{ end }}
  </header>
  <div data-data-table-shell {{ if .CardTreatment }}data-data-table-card{{ end }}>
    {{ if .Loading }}<p data-data-table-loading role="status">{{ .LoadingText }}</p>{{ end }}
    {{ if .Rows }}<div data-data-table tabindex="0" aria-label="{{ .ScrollLabel }}"><table data-data-table-inner aria-labelledby="{{ $titleID }}"><thead><tr>{{ range .Columns }}<th scope="col" data-data-table-column="{{ .Key }}">{{ .Label }}</th>{{ end }}</tr></thead><tbody>{{ range .Rows }}<tr id="{{ $.ID }}-row-{{ .Identity }}" data-data-table-row data-data-table-row-id="{{ .Identity }}" {{ with $.SSE }}sse-swap="data-table-row-update-{{ $.ID }}-{{ .Identity }}" hx-swap="outerHTML"{{ end }}{{ with .Action }} data-data-table-action="{{ .Name }}"{{ if .Context }} data-data-table-action-context="{{ .Context }}"{{ end }} tabindex="0" aria-label="{{ .AccessibleLabel }}"{{ end }}>{{ range .Cells }}<td>{{ range .Parts }}{{ if eq .Kind "text" }}{{ .Text }}{{ else if eq .Kind "strong" }}<strong>{{ .Text }}</strong>{{ else if eq .Kind "status-badge" }}<span data-status-badge data-status="{{ .StatusKind }}">{{ .Text }}</span>{{ else if eq .Kind "time" }}<time datetime="{{ .DateTime }}">{{ .Text }}</time>{{ end }}{{ end }}</td>{{ end }}</tr>{{ end }}</tbody></table></div>{{ else with .Empty }}<div data-data-table-empty><strong>{{ .Title }}</strong>{{ if .Message }}<span>{{ .Message }}</span>{{ end }}</div>{{ end }}{{ end }}
    {{ with .Pagination }}<nav data-data-table-pagination aria-label="{{ .AccessibleLabel }}"><button type="button" data-data-table-page="{{ .Previous.Page }}" {{ if .Previous.Disabled }}disabled{{ end }}>{{ .Previous.Label }}</button><span data-data-table-page-summary>{{ .Summary }}</span><button type="button" data-data-table-page="{{ .Next.Page }}" {{ if .Next.Disabled }}disabled{{ end }}>{{ .Next.Label }}</button></nav>{{ end }}
    {{ with .Feedback }}<div data-data-table-feedback {{ if .IsError }}role="alert"{{ else }}role="status"{{ end }}><strong>{{ .Title }}</strong><span>{{ .Message }}</span></div>{{ end }}
    {{ with .Recovery }}<button type="button" data-data-table-recovery="{{ .Action }}" {{ if .Context }}data-data-table-recovery-context="{{ .Context }}"{{ end }} {{ if .Disabled }}disabled{{ end }}>{{ .Label }}</button>{{ end }}
  </div>
  <p data-data-table-status role="status" aria-live="polite">{{ .Status }}</p>
  {{ with .SSE }}<span id="{{ .StructuralSignalID }}" data-data-table-structural-signal data-data-table-id="{{ $.ID }}" hidden sse-swap="data-table-structural-change-{{ $.ID }}" hx-swap="outerHTML"></span>{{ end }}
  {{ with .DetailDialogHost }}<div id="{{ .ID }}" data-data-table-detail-dialog-host></div>{{ end }}
</section>
```

Validate `HeadingLevel` and supplied `HeadingID` before template execution; the final heading branch is safe only after that validation. Tests cover a blank derived ID, a supplied existing stable heading ID, invalid/duplicate IDs rejected before output, and the same resolved ID on section, heading, and table association. Optional attributes/regions are omitted with their structure. The named wrapper is the immediate table parent; card treatment is a caller-selected shell hook, not mandated table framing. The structural signal is inert and is not user-facing.

## CSS rules

```css
[data-data-table-component] { max-width: 100%; min-width: 0; color: var(--data-table-text); }
[data-data-table-heading] { display:flex; flex-wrap:wrap; gap:.75rem; justify-content:space-between; margin:0 0 .75rem; }
[data-data-table-heading] :is(h1,h2,h3,h4,h5,h6) { margin:0; font:inherit; font-weight:800; }
[data-data-table-card] { background:var(--data-table-surface); border:1px solid var(--data-table-border); border-radius:var(--data-table-radius); box-shadow:var(--data-table-shadow); }
[data-data-table][hidden], [data-data-table-empty][hidden] { display:none; }
[data-data-table] { max-width:100%; min-width:0; overflow-x:auto; }
[data-data-table]:focus-visible, [data-data-table-inner] tr[data-data-table-action]:focus-visible, [data-data-table-pagination] button:focus-visible, [data-data-table-recovery]:focus-visible { outline:3px solid var(--data-table-focus-ring); outline-offset:2px; }
[data-data-table-inner] { border-collapse:collapse; min-width:max-content; width:100%; }
[data-data-table-inner] :is(th,td) { border-bottom:1px solid var(--data-table-border); padding:.8rem .9rem; text-align:left; vertical-align:top; }
[data-data-table-inner] th { background:var(--data-table-surface-subtle); }
[data-data-table-inner] tbody tr:last-child td { border-bottom:0; }
[data-data-table-inner] tr[data-data-table-action] { cursor:pointer; }
[data-data-table-inner] tr[data-data-table-action]:hover { background:var(--data-table-focus-surface); }
[data-data-table-pagination] { display:flex; flex-wrap:wrap; gap:.75rem; padding:.875rem 0; }
[data-data-table-pagination] button, [data-data-table-recovery] { min-height:2.75rem; padding:.625rem .875rem; }
[data-data-table-pagination] button:disabled, [data-data-table-recovery]:disabled { cursor:not-allowed; opacity:.55; }
[data-data-table-loading], [data-data-table-feedback], [data-data-table-empty] { padding:.875rem 0; }
[data-data-table-status] { min-height:1.25rem; }
@media (max-width:40rem) { [data-data-table-pagination] button { flex:1 1 8rem; } [data-data-table-page-summary] { flex-basis:100%; } }
@media (prefers-reduced-motion:reduce) { [data-data-table-component] * { scroll-behavior:auto; } }
```

Tokens describe table text, surface, border, card, focus, and focus-surface semantics; replace with project tokens. Card styling applies only when the parent selects it. Hidden, disabled, visible keyboard focus, narrow overflow, and reduced motion are covered.

## JavaScript example

Delegated JavaScript assumes HTMX plus an SSE extension owns stream connection and swaps. Its SSE-adapter lifecycle must call `acceptSSEEvent(tableIdentity, eventID)` before a swap; a rejected event never reaches HTMX swap handling. It accepts only conforming DOM and emits the three events above. Pointer activation requires same-row primary unmodified down/up; `Enter`/`Space` require row focus. Native buttons retain native keyboard behavior. Before a focused SSE row `outerHTML` swap it snapshots table/row identity by stable row DOM ID; after that swap it focuses only the same replacement row, never a different row or external focus. It does not fetch, call APIs, render server data, or own fragments.

```js
"use strict";
const pressed = new Map(), focusSnapshots = new Map(), lastSSEEvent = new Map();
// Called by the HTMX SSE adapter before it invokes an SSE swap.
const acceptSSEEvent = (tableIdentity, eventID) => {
  if (!/^\d+$/.test(eventID)) return false;
  const next = BigInt(eventID), previous = lastSSEEvent.get(tableIdentity);
  if (previous !== undefined && next <= previous) return false;
  lastSSEEvent.set(tableIdentity, next); return true;
};
const row = t => t instanceof Element ? t.closest("tr[data-data-table-row][data-data-table-action]") : null;
const tableFor = e => e.closest("[data-data-table-component][data-data-table-id]");
const activate = r => { const t = tableFor(r); if (!t) return; r.dispatchEvent(new CustomEvent("data-table:activate", {bubbles:true, detail:{action:r.dataset.dataTableAction, context:r.dataset.dataTableActionContext || "", rowIdentity:r.dataset.dataTableRowId, tableIdentity:t.dataset.dataTableId}})); };
document.addEventListener("pointerdown", e => { const r=row(e.target); if (e.isPrimary && e.button===0 && !e.altKey&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey && r) pressed.set(e.pointerId,r); });
document.addEventListener("pointerup", e => { const r=pressed.get(e.pointerId); pressed.delete(e.pointerId); if (r && e.isPrimary && e.button===0 && !e.altKey&&!e.ctrlKey&&!e.metaKey&&!e.shiftKey && row(e.target)===r) activate(r); });
document.addEventListener("pointercancel", e => pressed.delete(e.pointerId));
document.addEventListener("keydown", e => { const r=row(e.target); if (r===e.target && !e.repeat && (e.key==="Enter"||e.key===" ")) { e.preventDefault(); activate(r); } });
document.addEventListener("click", e => { const b=e.target instanceof Element && e.target.closest("button[data-data-table-page],button[data-data-table-recovery]"); if (!b || b.disabled) return; const t=tableFor(b); if (!t) return; const page=Number(b.dataset.dataTablePage); const recovery=b.dataset.dataTableRecovery; if (Number.isInteger(page)&&page>0) b.dispatchEvent(new CustomEvent("data-table:page-activate",{bubbles:true,detail:{tableIdentity:t.dataset.dataTableId,page}})); if (recovery) b.dispatchEvent(new CustomEvent("data-table:recovery-activate",{bubbles:true,detail:{tableIdentity:t.dataset.dataTableId,action:recovery,context:b.dataset.dataTableRecoveryContext||""}})); });
document.addEventListener("htmx:beforeSwap", e => { const r=e.detail.target; if (r instanceof HTMLTableRowElement && document.activeElement===r) { const t=tableFor(r); if (t && r.id && r.dataset.dataTableRowId) focusSnapshots.set(r.id,{tableIdentity:t.dataset.dataTableId,rowIdentity:r.dataset.dataTableRowId}); } });
document.addEventListener("htmx:afterSwap", e => { const target=e.detail.target; const saved=target instanceof Element && target.id ? focusSnapshots.get(target.id) : null; if (target instanceof Element && target.id) focusSnapshots.delete(target.id); if (saved) { const next=document.querySelector(`[data-data-table-id="${CSS.escape(saved.tableIdentity)}"] tr[data-data-table-row-id="${CSS.escape(saved.rowIdentity)}"]`); if (next instanceof HTMLElement) next.focus(); } if (target instanceof Element && target.matches("[data-data-table-structural-signal]")) { const next=document.getElementById(target.id); if (next?.matches("[data-data-table-structural-signal]")) next.dispatchEvent(new CustomEvent("data-table:structural-change",{bubbles:true,detail:{tableIdentity:next.dataset.dataTableId,eventID:next.dataset.dataTableEventId||""}})); } });
```

The server must include `data-data-table-event-id` on structural signal replacements. This sample assumes the adopting HTMX version supplies the replaced element as `event.detail.target` for both `htmx:beforeSwap` and `htmx:afterSwap`, retaining its stable row ID across an `outerHTML` swap; verify that lifecycle behavior. The parent listener deduplicates/coalesces event IDs and refuses overlapping reconcile requests; this example intentionally does neither request nor swap.

## Illustrative view data

Non-authoritative fixture: establishes no endpoint, domain schema, field names, enum, sorting, filtering, pagination, or business rule.

```go
table := presentation.DataTableView{ID:"example-results", Title:"Results", HeadingLevel:2, HeadingID:"existing-results-heading", Summary:"1 item", ScrollLabel:"Scrollable results table", CardTreatment:true,
	Columns: []presentation.DataTableColumnView{{Key:"name",Label:"Name"},{Key:"state",Label:"State"},{Key:"updated",Label:"Updated"}},
	Rows: []presentation.DataTableRowView{{Identity:"item-42", Cells: []presentation.DataTableCellView{{Parts:[]presentation.DataTableCellPartView{{Kind:"strong",Text:"Example item"}}},{Parts:[]presentation.DataTableCellPartView{{Kind:"status-badge",StatusKind:"active",Text:"Active"}}},{Parts:[]presentation.DataTableCellPartView{{Kind:"time",DateTime:"2026-09-06T19:52:00Z",Text:"6 September 2026, 19:52 UTC"}}}}, Action:&presentation.DataTableRowActionView{Name:"open-detail",Context:"results",AccessibleLabel:"Open details for Example item"}}},
	Pagination:&presentation.DataTablePaginationView{AccessibleLabel:"Result pages",Summary:"Page 1 of 1",Previous:presentation.DataTablePageActionView{Label:"Previous",Page:1,Disabled:true},Next:presentation.DataTablePageActionView{Label:"Next",Page:1,Disabled:true}},
	Feedback:&presentation.DataTableFeedbackView{Title:"Latest results shown",Message:"Updates may reconnect automatically."}, Recovery:&presentation.DataTableRecoveryView{Label:"Try again",Action:"retry-results"}, DetailDialogHost:&presentation.DataTableDetailDialogHostView{ID:"example-results-dialog-host"},
	SSE:&presentation.DataTableSSEView{StreamURI:"/ui/components/v1/data-tables/example-results/events",StructuralSignalID:"example-results-structural-signal"}, Status:"Connected for row updates."}
```

## States and failures

| State | Visibility and announcement | Focus/recovery | Owner |
| --- | --- | --- | --- |
| Loading | Parent shows loading copy and `aria-busy`; truthful rows may remain. | Retain focus; parent controls recovery. | Parent/server/HTMX |
| Success | Rows, summary, parent paging; SSE may replace matching rows. | Same focused row restores after SSE replacement only. | Server/HTMX/SSE |
| Empty | Parent shows supplied empty title and optional message; table absent. | Focus stays outside removed table; parent recovery if supplied. | Parent/server/HTMX |
| Partial values | Render caller-formatted fallback parts. | No change. | Caller |
| Request failure | Retain truthful content; visible feedback/status announces failure or reconnect. | Retain focus; native recovery emits event. | Parent/server/HTMX |
| Action failure | Parent shows confirmed-data failure; no client rollback. | Parent restores activated row/button or its fallback. | Parent/server/HTMX |

## Accessibility and responsive checks

- Native `table`, `thead`, `tbody`, `th scope="col"`, and `td`; visible heading names the table.
- Heading level is caller chosen but validated 1–6; do not skip hierarchy merely for table styling.
- Wrapper has its visible/accessible scroll-purpose label, `tabindex="0"`, visible focus, native horizontal keyboard scrolling, and no activation behavior.
- Eligible rows have one named tab stop and primary pointer/Enter/Space activation; inert rows have none. Cell parts, including badges/time, are inert.
- Use visible status/error text and polite announcements; color is supplementary. Buttons use native disabled semantics and at least 44px targets.
- At zoom and narrow widths, no clipping/document overflow; far columns remain reachable. Preserve reading order and table semantics; never cardify rows.
- Test SSE focused-row replacement, duplicate/older event rejection, structural signal coalescing/no overlap, `Last-Event-ID`, hidden-document connected behavior, and modal focus ownership separately.

## Adaptation and test checklist

- Replace every fixture value, generic token, stream URI, event consumer, card decision, copy, action, dialog host, and optional capability with approved adopter values.
- Validate heading level, blank-derived/supplied-safe-unique heading ID, IDs, unique column/row identity, exact cell count, allowlisted parts, action completeness, and optional-state invariants before render.
- Test populated/empty/loading/partial/request-failure/action-failure, one/full/final page boundaries, native disabled controls, pointer cancellation/modifiers, keyboard paths, and all emitted details.
- Test semantic associations, names, focus order/restoration, live feedback, inert cells, contrast, 200% zoom, and narrow containment.
- Server/HTMX tests own authorization, stream headers, event IDs/names/data, `Last-Event-ID`, reconnect, complete-row fragments, structural reconciliation/swap, and no-overlap coalescing. Capture runnable-route visual evidence where supported.

## Provenance and limitations

User-supplied intent, 2026-09-06: this FRE is the parent reference; validated caller heading level/ID, optional hybrid HTMX/SSE model, row updates, structural signals, inert-part allowlist, recovery event, and SSE continuity rules. Current approved parent citation: `/project/specification/frontend/components/data-table.md` (FE-CMP-020), read 2026-09-06. It adopts this reference as normative for its scope; requirements and approved specifications remain authority for each adopter. Existing parent contract includes stream URI, complete-row `outerHTML`, activation/page event names, named focusable overflow wrapper, card option, and parent-owned shell/state/pagination/dialog ownership.

Reference decisions: HTMX SSE extension is assumed to emit `htmx:beforeSwap`/`htmx:afterSwap` with a target; verify against the adopting HTMX version. The exact structural signal markup and parent reconciliation endpoint are intentionally not prescribed. Unsupported: arbitrary cell HTML, client data fetching/state reconstruction, SSE structural DOM mutation, nested row controls, and universal SSE. Source-derived behavior may change; reference date: 2026-09-06.
