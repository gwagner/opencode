# Data table

## Match

**Aliases:** table, data table, results table, history table, paginated table, actionable rows.

Use for consistently presenting a named collection with a summary, semantic columns, empty and status states, optional actionable rows, and pagination. Domain-specific callers supply headings, cells, labels, action identifiers, and pagination metadata. Do not use this as an editable grid, spreadsheet, tree grid, chart, or live log stream.

This reference is adaptable implementation material. Approved requirements, API specifications, and repository conventions remain authoritative.

## Ownership and behavior contract

The component owns its visible heading, count or summary, table surface, overflow behavior, empty state, pagination controls, status region, and interaction event contracts.

- The server or parent supplies already-formatted column headings, rows, accessible labels, action identifiers, and pagination metadata.
- The component presents supplied values; it does not fetch server data, interpret domain values, or open detail UI.
- An actionable row emits `data-table:activate` with its action, optional context, and stable row identity.
- A pagination control emits `data-table:page-activate` with its stable table identity and requested one-based page.
- A server layer or HTMX boundary outside client-owned DOM owns requests, loading failures, server fragments, and swaps.
- The component must work without actionable rows or pagination when those capabilities do not apply.

## Go view model

Use a presentation-specific model rather than passing domain, database, or transport types into the template. Format dates, numbers, fallback text, and pagination labels before rendering.

```go
package presentation

// DataTableView contains display-ready values for the data-table template.
type DataTableView struct {
	ID          string
	Title       string
	Summary     string
	ScrollLabel string
	Columns     []DataTableColumnView
	Rows        []DataTableRowView
	Empty       DataTableEmptyView
	Pagination  *DataTablePaginationView
	Status      string
}

// DataTableColumnView contains one display-ready column heading.
type DataTableColumnView struct {
	Label string
}

// DataTableRowView contains cells and an optional activation contract.
type DataTableRowView struct {
	Identity string
	Cells    []DataTableCellView
	Action   *DataTableRowActionView
}

// DataTableCellView contains plain text or a semantic status badge.
type DataTableCellView struct {
	Text   string
	Status *DataTableStatusView
}

// DataTableStatusView contains a style hook and visible status label.
type DataTableStatusView struct {
	Kind  string
	Label string
}

// DataTableRowActionView defines activation metadata for one row.
type DataTableRowActionView struct {
	Name            string
	Context         string
	AccessibleLabel string
}

// DataTableEmptyView contains feedback shown when Rows is empty.
type DataTableEmptyView struct {
	Title   string
	Message string
}

// DataTablePaginationView contains display-ready paging controls.
type DataTablePaginationView struct {
	AccessibleLabel string
	Summary         string
	Previous        DataTablePageActionView
	Next            DataTablePageActionView
}

// DataTablePageActionView defines one previous or next page action.
type DataTablePageActionView struct {
	Label    string
	Page     int
	Disabled bool
}
```

`ID` and row identities must be stable, non-empty DOM-safe tokens. Keep cell count and order aligned with `Columns`. Set `Action` only when all action fields required by the template are available. `Pagination` is `nil` for an unpaged collection. Parse the template with `html/template` so supplied text and attribute values are contextually escaped.

## GoHTML template

```gohtml
{{- $titleID := printf "%s-title" .ID -}}
<section
  data-data-table-component
  data-data-table-id="{{ .ID }}"
  aria-labelledby="{{ $titleID }}"
>
  <div data-data-table-heading>
    <h2 id="{{ $titleID }}">{{ .Title }}</h2>
    <span data-data-table-count>{{ .Summary }}</span>
  </div>

  <div data-data-table-card>
    <div data-data-table tabindex="0" aria-label="{{ .ScrollLabel }}" {{ if not .Rows }}hidden{{ end }}>
      <table data-data-table-inner aria-labelledby="{{ $titleID }}">
        <thead>
          <tr>
            {{ range .Columns }}
            <th scope="col">{{ .Label }}</th>
            {{ end }}
          </tr>
        </thead>
        <tbody>
          {{ range .Rows }}
          <tr
            data-data-table-row
            data-data-table-row-id="{{ .Identity }}"
            {{ with .Action }}
            data-data-table-action="{{ .Name }}"
            {{ if .Context }}data-data-table-action-context="{{ .Context }}"{{ end }}
            tabindex="0"
            aria-label="{{ .AccessibleLabel }}"
            {{ end }}
          >
            {{ range .Cells }}
            <td>
              {{ with .Status }}<span data-status-badge data-status="{{ .Kind }}">{{ .Label }}</span>{{ else }}{{ .Text }}{{ end }}
            </td>
            {{ end }}
          </tr>
          {{ end }}
        </tbody>
      </table>
    </div>

    <div data-data-table-empty {{ if .Rows }}hidden{{ end }}>
      <strong>{{ .Empty.Title }}</strong>
      <span>{{ .Empty.Message }}</span>
    </div>

    {{ with .Pagination }}
    <nav data-data-table-pagination aria-label="{{ .AccessibleLabel }}">
      <button type="button" data-data-table-page="{{ .Previous.Page }}" {{ if .Previous.Disabled }}disabled{{ end }}>{{ .Previous.Label }}</button>
      <span data-data-table-page-summary>{{ .Summary }}</span>
      <button type="button" data-data-table-page="{{ .Next.Page }}" {{ if .Next.Disabled }}disabled{{ end }}>{{ .Next.Label }}</button>
    </nav>
    {{ end }}
  </div>

  <p data-data-table-status role="status" aria-live="polite">{{ .Status }}</p>
</section>
```

The `with .Action` block omits action attributes, `tabindex`, and the row `aria-label` together for static rows. A nil `Pagination` omits pagination. Place dialogs and other destinations outside server-swappable table regions.

## CSS rules

Prefer project tokens. These rules use generic `--data-table-*` tokens for semantic colors, soft gradients, rounded cards, and visible focus rings.

```css
[data-data-table-component] {
  min-width: 0;
  max-width: 100%;
  color: var(--data-table-text);
}

[data-data-table-heading] {
  align-items: center;
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: space-between;
  margin: 0 0 0.75rem;
}

[data-data-table-heading] h2 {
  color: var(--data-table-text);
  font-size: 1rem;
  font-weight: 800;
  margin: 0;
}

[data-data-table-count] {
  align-items: center;
  background: var(--data-table-accent-soft);
  border: 1px solid var(--data-table-accent-border);
  border-radius: 9999px;
  color: var(--data-table-accent-text);
  display: inline-flex;
  font-size: 0.8125rem;
  font-weight: 800;
  padding: 0.3rem 0.65rem;
}

[data-data-table-card] {
  background: var(--data-table-surface-gradient);
  border: 1px solid var(--data-table-border);
  border-radius: 1rem;
  box-shadow: 0 12px 30px var(--data-table-shadow);
  overflow: hidden;
}

[data-data-table] {
  max-width: 100%;
  min-width: 0;
  overflow-x: auto;
}

[data-data-table]:focus-visible {
  outline: 3px solid var(--data-table-focus-ring);
  outline-offset: -3px;
}

[data-data-table-inner] {
  border-collapse: separate;
  border-spacing: 0;
  color: var(--data-table-muted-text);
  font-size: 0.875rem;
  width: 100%;
}

[data-data-table-inner] th,
[data-data-table-inner] td {
  border-bottom: 1px solid var(--data-table-border);
  padding: 0.8rem 0.9rem;
  text-align: left;
  vertical-align: top;
}

[data-data-table-inner] th {
  background: var(--data-table-surface-subtle);
  color: var(--data-table-muted-text);
  font-size: 0.75rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

[data-data-table-inner] tbody tr:last-child td {
  border-bottom: 0;
}

[data-data-table-inner] tbody tr[data-data-table-action] {
  cursor: pointer;
}

[data-data-table-inner] tbody tr[data-data-table-action]:hover {
  background: var(--data-table-surface-subtle);
}

[data-data-table-inner] tbody tr[data-data-table-action]:focus-visible {
  background: var(--data-table-focus-surface);
  outline: 3px solid var(--data-table-focus-ring);
  outline-offset: -3px;
}

[data-data-table-empty] {
  color: var(--data-table-text);
  gap: 0.375rem;
  justify-items: start;
  padding: 1.25rem;
}

[data-data-table-empty] strong,
[data-data-table-empty] span {
  display: block;
}

[data-data-table-empty] span,
[data-data-table-status],
[data-data-table-page-summary] {
  color: var(--data-table-muted-text);
  font-size: 0.875rem;
}

[data-data-table-empty][hidden] {
  display: none;
}

[data-data-table-pagination] {
  align-items: center;
  border-top: 1px solid var(--data-table-border);
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  justify-content: flex-end;
  padding: 0.875rem 1rem;
}

[data-data-table-pagination] button {
  background: var(--data-table-surface);
  border: 1px solid var(--data-table-border-strong);
  border-radius: 0.75rem;
  color: var(--data-table-text);
  font-size: 0.875rem;
  font-weight: 700;
  min-height: 2.75rem;
  padding: 0.625rem 0.875rem;
}

[data-data-table-pagination] button:hover:not(:disabled) {
  background: var(--data-table-surface-subtle);
  border-color: var(--data-table-muted-text);
}

[data-data-table-pagination] button:focus-visible {
  outline: 3px solid var(--data-table-focus-ring);
  outline-offset: 2px;
}

[data-data-table-pagination] button:disabled {
  cursor: not-allowed;
  opacity: 0.55;
}

[data-data-table-status] {
  margin: 0.75rem 0 0;
  min-height: 1.25rem;
}

@media (max-width: 40rem) {
  [data-data-table-pagination] {
    align-items: stretch;
    display: grid;
    grid-template-columns: 1fr 1fr;
  }

  [data-data-table-page-summary] {
    grid-column: 1 / -1;
    grid-row: 1;
    text-align: center;
  }
}

@media (prefers-reduced-motion: reduce) {
  [data-data-table-component] * {
    scroll-behavior: auto;
  }
}
```

## JavaScript example

This presentation adapter uses event delegation so the same interaction works for any conforming table, including server-rendered rows replaced outside client-owned DOM. It performs no requests and no swaps.

```js
"use strict";

const pointerRows = new Map();

function actionableDataTableRow(target) {
  if (!(target instanceof Element)) return null;

  const row = target.closest("tr[data-data-table-row][data-data-table-action]");
  if (!row || row.tabIndex !== 0 || !row.getAttribute("aria-label")) return null;
  if (!row.dataset.dataTableRowId || !row.dataset.dataTableAction) return null;

  return row;
}

function dispatchDataTableActivation(row) {
  const detail = {
    action: row.dataset.dataTableAction ?? "",
    context: row.dataset.dataTableActionContext ?? "",
    rowIdentity: row.dataset.dataTableRowId ?? "",
  };

  if (!detail.action || !detail.rowIdentity) return;

  row.dispatchEvent(new CustomEvent("data-table:activate", {
    bubbles: true,
    detail,
  }));
}

document.addEventListener("pointerdown", (event) => {
  if (!event.isPrimary || event.button !== 0 || event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;

  const row = actionableDataTableRow(event.target);
  if (row) pointerRows.set(event.pointerId, row);
});

document.addEventListener("pointerup", (event) => {
  const pressedRow = pointerRows.get(event.pointerId);
  pointerRows.delete(event.pointerId);

  if (
    !pressedRow ||
    !event.isPrimary ||
    event.button !== 0 ||
    event.altKey ||
    event.ctrlKey ||
    event.metaKey ||
    event.shiftKey ||
    actionableDataTableRow(event.target) !== pressedRow
  ) return;

  dispatchDataTableActivation(pressedRow);
});

document.addEventListener("pointercancel", (event) => {
  pointerRows.delete(event.pointerId);
});

document.addEventListener("keydown", (event) => {
  if (event.repeat || (event.key !== "Enter" && event.key !== " ")) return;

  const row = actionableDataTableRow(event.target);
  if (!row || event.target !== row) return;

  event.preventDefault();
  dispatchDataTableActivation(row);
});

document.addEventListener("click", (event) => {
  if (!(event.target instanceof Element)) return;

  const button = event.target.closest("button[data-data-table-page]");
  if (!button || button.disabled) return;

  const table = button.closest("[data-data-table-component][data-data-table-id]");
  const page = Number(button.dataset.dataTablePage);
  if (!table || !Number.isInteger(page) || page < 1) return;

  button.dispatchEvent(new CustomEvent("data-table:page-activate", {
    bubbles: true,
    detail: {
      tableIdentity: table.dataset.dataTableId,
      page,
    },
  }));
});
```

Native buttons provide keyboard pagination activation. Do not place links, buttons, inputs, or other independent controls inside an actionable row; use a dedicated actions column and make that row non-actionable when nested controls are required.

## Illustrative view data

This fixture demonstrates caller-supplied display data. It is **not an authoritative endpoint, domain schema, field-name, status-enum, timestamp-format, sorting, or pagination contract**.

```go
table := presentation.DataTableView{
	ID:          "example-results",
	Title:       "Results",
	Summary:     "60 items",
	ScrollLabel: "Scrollable results table",
	Columns: []presentation.DataTableColumnView{
		{Label: "Name"},
		{Label: "Status"},
		{Label: "Updated"},
	},
	Rows: []presentation.DataTableRowView{
		{
			Identity: "item-42",
			Cells: []presentation.DataTableCellView{
				{Text: "Example item"},
				{Status: &presentation.DataTableStatusView{Kind: "active", Label: "Active"}},
				{Text: "5 September 2026, 19:52 UTC"},
			},
			Action: &presentation.DataTableRowActionView{
				Name:            "open-detail",
				Context:         "results",
				AccessibleLabel: "Open details for Example item",
			},
		},
	},
	Empty: presentation.DataTableEmptyView{
		Title:   "No results",
		Message: "No items are available.",
	},
	Pagination: &presentation.DataTablePaginationView{
		AccessibleLabel: "Result pages",
		Summary:         "Page 1 of 3",
		Previous: presentation.DataTablePageActionView{
			Label:    "Previous",
			Page:     1,
			Disabled: true,
		},
		Next: presentation.DataTablePageActionView{
			Label: "Next",
			Page:  2,
		},
	},
}
```

## States and failures

| State | Expected presentation |
| --- | --- |
| Loading | Retain the title and headings, mark the request-owned region busy, and expose project-standard loading feedback without client-side fetching. |
| Success | Show supplied rows, summary, and applicable pagination actions. |
| Empty | Hide the table body or table, show the explicit empty state, display a zero summary, and disable or omit pagination. |
| Partial values | Present caller-formatted fallback text such as an em dash; preserve the row's accessible meaning. |
| Request failure | The request owner renders a persistent, recoverable error and retry action without swapping client-owned DOM. |
| Action failure | Preserve or restore focus to the activated row or page control, announce the failure, and allow retry. |

## Accessibility and responsive checks

- Keep a real table with `scope="col"` headers; do not recreate tabular data with generic grids.
- Give the table an accessible name through its visible heading.
- Make the horizontal scroll region keyboard reachable and visibly focused.
- For actionable rows, require a stable identity, action, `tabindex="0"`, meaningful `aria-label`, pointer activation, `Enter`, `Space`, and visible focus.
- Avoid nested interactive controls in actionable rows.
- Keep status text visible; color may reinforce but never replace meaning.
- Announce asynchronous status changes through the polite status region; persistent errors need visible error UI.
- Keep pagination targets at least 44 CSS pixels high and expose disabled state natively.
- At narrow widths, retain horizontal scrolling without clipping the page and keep pagination readable.

## Adaptation and test checklist

- Replace illustrative headings, cells, actions, and pagination metadata with approved caller contracts.
- Use project date, number, status, localization, and design-token conventions.
- Test static and actionable rows, including pointer cancellation, modifier keys, `Enter`, `Space`, and event details.
- Test zero, one, full-page, and final-page collections plus page event details and disabled boundaries.
- Test accessible names, scoped headers, overflow focus, row focus, empty feedback, and status announcements.
- Test light, dark, explicit appearance, and narrow-screen presentation where supported.
- Keep request and swap tests at the owning server or HTMX boundary.
- Capture baseline and post-change evidence for every affected runnable route.

## Provenance and limitations

Adapted from user-provided authenticated-app CSS and delegated row-activation JavaScript on 2026-09-05. The source established the design-token palette, table spacing and typography, overflow behavior, actionable-row focus treatment, and generic activation event. The surrounding component structure, pagination event, illustrative data, and state guidance are reference designs rather than observed or approved production contracts.
