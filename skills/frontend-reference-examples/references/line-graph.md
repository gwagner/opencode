# Match

**Component:** Line graph. **Aliases:** graph, chart, time-series chart, line chart, metric visualization, range selector.

Use it to present caller-supplied chronological numeric series, an accessible chart summary, optional time-range choices, and rendering feedback. Suitable for comparable time-based metrics. Do not use it for categorical comparison, unformatted/raw measurements, data entry, an unrelated aggregate, or a table needing row actions; use a bar-chart reference, form control, summary card, or data table instead. This is adaptable implementation material, not product authority.

# Ownership and behavior contract

The component owns its heading/summary, canvas frame, nonvisual series summary, optional range-control group, and live feedback. The caller supplies already formatted heading, summary, visible range labels, UTC or localized point labels, series labels, point values, empty/failure copy, and stable component/series IDs. The component presents those values only; it must not interpret metric names, infer units, create missing data, sort business records, calculate ranges, authorize access, or turn visualization-only points into records.

`line-graph:range-change` is emitted on an enabled range-button click or Space/Enter activation. Its `detail` is `{ graphID, range, trigger }`; `graphID` is `LineGraphView.ID`, `range` is the selected `LineGraphRangeView.ID`, and `trigger` is `"pointer"` or `"keyboard"`. The initiating button retains focus. This reference-design event is not an observed production event; its consumer owns selection, requests, rendering data, and busy/failure state.

Server, HTMX, or the parent owns requests, authorization, validation, loading data, errors, navigation, fragment replacement, dialogs, and swaps. The client example only emits the selection intent. Do not nest range buttons in links, row activators, dialogs, or other interactive controls. A graph may accompany a table, but must not make a canvas substitute for the table when exact values or actions are required.

## Server-driven contract

Not applicable: this reference is presentation-driven. Data reads are owned by its parent, not by this graph reference.

# Implementation-facing presentation model

```go
package presentation

// LineGraphView is a caller-formatted time-series graph and its optional controls.
type LineGraphView struct {
	ID                 string
	Heading            string
	Summary            string
	CanvasLabel        string
	Series             []LineGraphSeriesView
	RangeControl       *LineGraphRangeControlView
	Feedback           *LineGraphFeedbackView
	EmptyState         *LineGraphEmptyStateView
}

// LineGraphSeriesView is one ordered, display-ready series and its accessible point summary.
type LineGraphSeriesView struct {
	ID     string
	Label  string
	Points []LineGraphPointView
}

// LineGraphPointView is one caller-formatted point label and displayed value.
type LineGraphPointView struct {
	Label string
	Value string
}

// LineGraphRangeControlView is an optional named group of mutually exclusive range choices.
type LineGraphRangeControlView struct {
	Label    string
	Disabled bool
	Ranges   []LineGraphRangeView
}

// LineGraphRangeView is one stable, caller-formatted range choice.
type LineGraphRangeView struct {
	ID       string
	Label    string
	Selected bool
}

// LineGraphFeedbackView is an optional polite status message.
type LineGraphFeedbackView struct {
	Message string
}

// LineGraphEmptyStateView is optional visible copy used when no drawable series exists.
type LineGraphEmptyStateView struct {
	Message string
	Hint    string
}
```

`ID`, `Heading`, `CanvasLabel`, and every series/range `ID` are required and stable within the adopted surface. `Summary` is required formatted context. `Series` is chronological; each series has compatible point-label ordering. `Value` is display-ready text. The adopting chart renderer receives an equivalent caller-supplied numeric plotting adapter; it must not parse localized display text. `RangeControl`, `Feedback`, and `EmptyState` are optional; render `EmptyState` only when `Series` is empty. `Selected` is exactly one range when controls exist; `Disabled` is explicit presentation state. Do not expose domain, database, transport, or API objects.

Format labels, units, and timestamps before adaptation; use the product's localization and UTC/display rules. Escape all text/attributes. Treat missing optional feedback as absent, not an empty live region. The Go shape is a reusable presentation adapter, not evidence that an adopter uses Go; a TypeScript renderer may illustratively map these fields to readonly view interfaces of the same shape.

# Semantic template

```gohtml
{{define "line-graph"}}
<section data-line-graph data-line-graph-id="{{.ID}}" aria-labelledby="{{.ID}}-heading"{{if and .RangeControl .RangeControl.Disabled}} aria-busy="true"{{end}}>
  <header data-line-graph-heading>
    <h2 id="{{.ID}}-heading">{{.Heading}}</h2>
    <p>{{.Summary}}</p>
  </header>
  {{with .RangeControl}}
  <div data-line-graph-ranges role="group" aria-label="{{.Label}}"{{if .Disabled}} aria-busy="true"{{end}}>
    {{range .Ranges}}
    <button data-line-graph-range data-line-graph-range-id="{{.ID}}" type="button" aria-pressed="{{.Selected}}"{{if $.RangeControl.Disabled}} disabled{{end}}>{{.Label}}</button>
    {{end}}
  </div>
  {{end}}
  {{if .Series}}
  <div data-line-graph-frame>
    <canvas data-line-graph-canvas role="img" aria-label="{{.CanvasLabel}}"></canvas>
  </div>
  <div data-line-graph-summary class="line-graph__visually-hidden">
    {{range .Series}}<section><h3>{{.Label}}</h3><ul>{{range .Points}}<li>{{.Label}}: {{.Value}}</li>{{end}}</ul></section>{{end}}
  </div>
  {{else if .EmptyState}}
  <div data-line-graph-empty><p>{{.EmptyState.Message}}</p><p>{{.EmptyState.Hint}}</p></div>
  {{end}}
  {{with .Feedback}}<p data-line-graph-status role="status" aria-live="polite">{{.Message}}</p>{{end}}
</section>
{{end}}
```

The canvas renderer receives the caller's normalized series separately; it never fetches. `data-line-graph*` hooks identify styling, delegated range intent, and chart mounting only.

# CSS rules

```css
[data-line-graph] { min-width: 0; }
[data-line-graph][hidden] { display: none; }
[data-line-graph-heading] { display: flex; flex-wrap: wrap; gap: .5rem 1rem; align-items: baseline; justify-content: space-between; }
[data-line-graph-heading] h2, [data-line-graph-heading] p { margin: 0; }
[data-line-graph-heading] p, [data-line-graph-status] { color: var(--line-graph-muted, #64748b); }
[data-line-graph-ranges] { display: flex; flex-wrap: wrap; gap: .5rem; margin: .75rem 0; }
[data-line-graph-range] { min-height: 2.75rem; border: 1px solid var(--line-graph-border, #64748b); border-radius: 999px; background: var(--line-graph-surface, #fff); color: var(--line-graph-text, #0f172a); padding: .4rem .75rem; }
[data-line-graph-range][aria-pressed="true"] { border-color: var(--line-graph-selected-border, #2563eb); background: var(--line-graph-selected-surface, #eff6ff); color: var(--line-graph-selected-text, #1d4ed8); }
[data-line-graph-range]:disabled { cursor: not-allowed; opacity: .6; }
[data-line-graph-range]:focus-visible { outline: 3px solid var(--line-graph-focus, #2563eb); outline-offset: 2px; }
[data-line-graph-frame] { box-sizing: border-box; height: 18rem; max-width: 100%; overflow: hidden; border: 1px solid var(--line-graph-border, #64748b); border-radius: .875rem; background: var(--line-graph-surface, #fff); padding: 1rem; }
[data-line-graph-canvas] { display: block; width: 100% !important; height: 100% !important; }
[data-line-graph-empty] { padding: 1rem; border: 1px dashed var(--line-graph-border, #64748b); }
.line-graph__visually-hidden { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
@media (max-width: 640px) { [data-line-graph-frame] { height: 14rem; padding: .75rem; } [data-line-graph-range] { flex: 1 1 auto; } }
@media (prefers-reduced-motion: reduce) { [data-line-graph-canvas] { transition: none; } }
```

The generic custom properties describe muted text, frame surface/border, selected control surface/border/text, and focus. Map them to the adopting project's semantic tokens. Hidden summary remains available to assistive technology. Disabled state uses native `disabled`; selected state is not color-only.

# JavaScript example

Event delegation assumes this script is installed once on `document`. It accepts only matching enabled buttons, determines pointer versus keyboard activation, emits no fetch/swap, and leaves focus on the button.

```js
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-line-graph-range]");
  if (!(button instanceof HTMLButtonElement) || button.disabled) return;
  const root = button.closest("[data-line-graph]");
  if (!root) return;
  root.dispatchEvent(new CustomEvent("line-graph:range-change", {
    bubbles: true,
    detail: {
      graphID: root.dataset.lineGraphId,
      range: button.dataset.lineGraphRangeId,
      trigger: event.detail === 0 ? "keyboard" : "pointer",
    },
  }));
});
```

Native buttons provide pointer, Tab, Space, and Enter behavior. The parent updates `aria-pressed`, `disabled`, feedback, and supplied chart data only after its owned outcome.

# Illustrative view data

```go
// Non-authoritative fixture: establishes no endpoint, domain schema, field name,
// enum, sorting, filtering, pagination, or business rule.
view := presentation.LineGraphView{
	ID: "sample-trend", Heading: "Trend", Summary: "2 samples · current period", CanvasLabel: "Trend line graph",
	RangeControl: &presentation.LineGraphRangeControlView{Label: "Displayed period", Ranges: []presentation.LineGraphRangeView{{ID: "current", Label: "Current", Selected: true}, {ID: "previous", Label: "Previous"}}},
	Series: []presentation.LineGraphSeriesView{{ID: "sample-series", Label: "Sample series", Points: []presentation.LineGraphPointView{{Label: "Period start", Value: "124"}, {Label: "Period end", Value: "98"}}}},
	Feedback: &presentation.LineGraphFeedbackView{Message: "Updated."},
}
```

# States and failures

| State | Visibility and announcement | Focus | Recovery | Owner |
| --- | --- | --- | --- | --- |
| Loading | Retain prior graph if present; otherwise heading/controls plus polite loading feedback | Retain current control | Wait | Parent/server |
| Success | Canvas, nonvisual summary, and optional updated feedback | Retain initiating control | Choose range | Parent/chart renderer |
| Empty | Visible empty copy; no canvas; no announcement unless state changed | Retain control | Caller-provided alternative | Parent/server |
| Partial values | Render supplied points/gaps; explain unavailable series in supplied feedback | Retain control | Choose another range | Parent/chart renderer |
| Request failure | Retain last graph and announce failure, or show empty failure copy initially | Retain control | Parent-provided retry | Server/HTMX/parent |
| Action failure | Keep prior selected presentation; announce supplied failure | Return/retain initiating button | Retry parent action | Parent/server |

# Accessibility and responsive checks

Use a labelled `section`, native button group, canvas `role="img"` with a meaningful label, and a text-equivalent series summary. Tab reaches range buttons in DOM order; Space/Enter activate them; focus never moves solely for refresh. Status updates are polite. Provide visible labels, native disabled semantics, color-independent selected/error meaning, and at least 44px controls. At 200% zoom and narrow widths, controls wrap and the frame stays within the document; no clipped labels or inaccessible overflow. Validate chart tooltip/date formatting separately in the chart renderer.

# Adaptation and test checklist

Replace fixture text/IDs, fallback colors, token mappings, event consumer, canvas renderer, range choices, feedback, and any optional controls. Confirm metric semantics, timestamps, localization, authorization, data ownership, and whether a companion table is required. Test populated, loading, empty, partial, retained-content failure, and action-failure states; pointer/keyboard events and exact event detail; button names/disabled state, canvas alternative, focus, contrast, zoom, and 390px layout. Keep request, fragment, authorization, and swap tests with the server/HTMX/parent owner. Where supported, capture runnable-route visual evidence.

# Provenance and limitations

**User-supplied intent:** turn the existing graph into a reusable reference component. Product-specific implementation and authority sources were intentionally not retained in this reusable reference.

Reference decisions: this isolates a generic caller-supplied graph and a proposed emitted intent event; it claims no product API or runtime behavior. It intentionally does not cover a chart-library configuration, server contracts, polling, data synthesis, metric catalogs, table/dialog behavior, or product-specific variants. Reference date: **2026-09-06**.
