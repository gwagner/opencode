# On-off switch

## Match

**Component:** On-off switch. **Aliases:** toggle switch, boolean switch, active/inactive switch, on/off control, paused/running control, up/down control, HTMX switch.

Use to change one independent, immediately understandable binary presentation state with caller-supplied labels. Suitable for settings or controls where either label pair describes the two possible states. Do not use for submitting a form, choosing among more than two options, destructive confirmation, or a navigation tab. Do not force checkboxes requiring a conventional checkmark, segmented controls, radio groups, or async action buttons into this reference.

This is adaptable implementation material, not product authority.

## Ownership and behavior contract

The component owns the visible label, native checkbox, track and thumb, current-state text, optional feedback, disabled and busy presentation, independent HTMX mutation contract, and `on-off-switch:change` event. The caller supplies formatted label, on/off labels, checked/disabled/busy state, and optional feedback. It presents them without interpreting what either state means.

`on-off-switch:change` fires after a user changes the native checkbox. Its detail is `{ switchIdentity, checked, stateLabel }`; `switchIdentity` is the stable component ID, `checked` is the selected Boolean, and `stateLabel` is the matching caller-supplied label. Focus remains on the checkbox.

**Independent HTMX contract:** the checkbox sends `PATCH /ui/components/v1/on-off-switches/{id}` on `change`. `{id}` is the URL-path-encoded `ID`; the `application/x-www-form-urlencoded` payload has exactly `checked=true` or `checked=false`. The request carries HTMX's `HX-Request: true` header, targets its closest `[data-on-off-switch-region]`, and swaps `outerHTML`. `200 OK` must return `Content-Type: text/html`, `Cache-Control: no-store`, and one complete region rendered from the confirmed `OnOffSwitchView`, retaining the same `ID`. A validation or action failure must return a complete confirmed-state region with `Feedback.IsError=true` and a visible retry path owned by the server. Transport failures leave the current region untouched; HTMX/server presents the error outside the component. The server owns validation, authorization, mutation, loading, error state, and fragment rendering. The JavaScript never rolls state back or replaces fragments.

Do not nest links, buttons, or other interactive controls inside the label. Do not place this independent control in a competing form submission contract.

## Implementation-facing presentation model

```go
package presentation

// OnOffSwitchView contains display-ready values for an on-off switch.
type OnOffSwitchView struct {
	ID        string
	Label     string
	OnLabel   string
	OffLabel  string
	Checked   bool
	Disabled  bool
	Busy      bool
	Feedback  *OnOffSwitchFeedbackView
}

// OnOffSwitchFeedbackView contains optional visible status or error feedback.
type OnOffSwitchFeedbackView struct {
	Message string
	IsError bool
}
```

`ID`, `Label`, `OnLabel`, and `OffLabel` are required. `ID` is a stable, non-empty, DOM-safe identity. `Feedback` is nil when there is none; `Message` is already localized text and `IsError` selects error presentation. `Checked`, `Disabled`, and `Busy` are explicit presentation states; disabled or busy controls must not accept changes. Format and localize all text and fallbacks before rendering; parse with `html/template` for contextual escaping. This Go model is a reusable presentation adapter, not evidence that an adopter uses Go. Other stacks should map this same shape illustratively.

## Semantic template

```gohtml
{{- $feedbackID := printf "%s-feedback" .ID -}}
<div id="{{ .ID }}-region" data-on-off-switch-region data-on-off-switch data-on-off-switch-id="{{ .ID }}" {{ if .Busy }}aria-busy="true"{{ end }}>
  <input
    id="{{ .ID }}"
    data-on-off-switch-input
    type="checkbox"
    {{ if .Checked }}checked{{ end }}
    {{ if or .Disabled .Busy }}disabled{{ end }}
    {{ with .Feedback }}aria-describedby="{{ $feedbackID }}"{{ end }}
    hx-patch="/ui/components/v1/on-off-switches/{{ urlquery .ID }}"
    hx-trigger="change"
    hx-target="closest [data-on-off-switch-region]"
    hx-swap="outerHTML"
    hx-disabled-elt="this"
    hx-vals='js:{checked: event.target.checked}'
  >
  <label data-on-off-switch-label for="{{ .ID }}">
    <span data-on-off-switch-name>{{ .Label }}</span>
    <span data-on-off-switch-control aria-hidden="true"><span data-on-off-switch-thumb></span></span>
    <span data-on-off-switch-state data-on-label="{{ .OnLabel }}" data-off-label="{{ .OffLabel }}">{{ if .Checked }}{{ .OnLabel }}{{ else }}{{ .OffLabel }}{{ end }}</span>
  </label>
  {{ with .Feedback }}
  <p id="{{ $feedbackID }}" data-on-off-switch-feedback {{ if .IsError }}role="alert"{{ else }}role="status" aria-live="polite"{{ end }}>{{ .Message }}</p>
  {{ end }}
</div>
```

The native checkbox supplies checked and disabled semantics. Optional described-by association and feedback are omitted together when unavailable. The HTMX `checked` payload is the sole request body, and `hx-disabled-elt="this"` prevents duplicate mutation while pending; do not place this independent component in a competing form submission contract. `[data-on-off-switch-region]` is the complete HTMX `outerHTML` swap boundary. Hooks support styles and the documented delegated event only.

## CSS rules

Use project tokens where available. `--on-off-switch-*` tokens respectively mean text, muted text, surface, border, on-state, focus ring, and error text.

```css
[data-on-off-switch] { color: var(--on-off-switch-text); max-width: 100%; }
[data-on-off-switch-region][hidden] { display: none; }
[data-on-off-switch-region].htmx-request [data-on-off-switch-label] { cursor: progress; opacity: .7; }
[data-on-off-switch-input] { block-size: 1px; inline-size: 1px; margin: -1px; opacity: 0; position: absolute; }
[data-on-off-switch-label] { align-items: center; cursor: pointer; display: inline-flex; flex-wrap: wrap; gap: .625rem; min-block-size: 2.75rem; }
[data-on-off-switch-name] { font-weight: 700; }
[data-on-off-switch-control] { background: var(--on-off-switch-surface); border: 1px solid var(--on-off-switch-border); border-radius: 999px; box-sizing: border-box; inline-size: 3rem; padding: .1875rem; transition: background-color .15s ease, border-color .15s ease; }
[data-on-off-switch-thumb] { background: var(--on-off-switch-text); border-radius: 50%; display: block; block-size: 1.25rem; inline-size: 1.25rem; transition: transform .15s ease; }
[data-on-off-switch-input]:checked + [data-on-off-switch-label] [data-on-off-switch-control] { background: var(--on-off-switch-on); border-color: var(--on-off-switch-on); }
[data-on-off-switch-input]:checked + [data-on-off-switch-label] [data-on-off-switch-thumb] { background: var(--on-off-switch-surface); transform: translateX(1.25rem); }
[data-on-off-switch-input]:focus-visible + [data-on-off-switch-label] { outline: 3px solid var(--on-off-switch-focus-ring); outline-offset: 3px; }
[data-on-off-switch-input]:disabled + [data-on-off-switch-label] { cursor: not-allowed; opacity: .55; }
[data-on-off-switch-feedback] { color: var(--on-off-switch-muted-text); margin: .375rem 0 0; }
[data-on-off-switch-feedback][role="alert"] { color: var(--on-off-switch-error-text); }
[data-on-off-switch][aria-busy="true"] [data-on-off-switch-label] { cursor: progress; }
@media (max-width: 30rem) { [data-on-off-switch-label] { align-items: flex-start; display: grid; grid-template-columns: 1fr auto; } [data-on-off-switch-state] { grid-column: 1 / -1; } }
@media (prefers-reduced-motion: reduce) { [data-on-off-switch-control], [data-on-off-switch-thumb] { transition: none; } }
```

The visually hidden input remains focusable; do not use `display: none`. Native disabled state is styled through `:disabled`.

## JavaScript example

This optional, document-level delegated adapter accepts native change events from conforming inputs and emits the documented custom event. It updates only caller-supplied state-label text; it fetches nothing and owns no server state, request, fragment, or swap.

```js
"use strict";

document.addEventListener("change", (event) => {
  if (!(event.target instanceof HTMLInputElement) || !event.target.matches("input[data-on-off-switch-input]")) return;
  const root = event.target.closest("[data-on-off-switch][data-on-off-switch-id]");
  const state = root?.querySelector("[data-on-off-switch-state][data-on-label][data-off-label]");
  if (!root || !state || event.target.disabled) return;

  const stateLabel = event.target.checked ? state.dataset.onLabel : state.dataset.offLabel;
  if (!stateLabel) return;
  state.textContent = stateLabel;
  event.target.dispatchEvent(new CustomEvent("on-off-switch:change", {
    bubbles: true,
    detail: { switchIdentity: root.dataset.onOffSwitchId, checked: event.target.checked, stateLabel },
  }));
});
```

Pointer and keyboard operation come from the native checkbox (including Space); focus remains there. Event consumers decide whether and how to request a state change.

## Illustrative view data

This non-authoritative fixture establishes no endpoint, domain schema, field name, enum, sorting, filtering, pagination, or business rule.

```go
switchView := presentation.OnOffSwitchView{
	ID:       "example-monitor-state",
	Label:    "Monitoring",
	OnLabel:  "Active",
	OffLabel: "Paused",
	Checked:  true,
	Feedback: &presentation.OnOffSwitchFeedbackView{Message: "Monitoring is active."},
}
```

## States and failures

| State | Visibility and announcement | Focus and recovery | Owner |
| --- | --- | --- | --- |
| Loading | HTMX applies `.htmx-request`; retain label and selected state. | Retain checkbox focus; server response disables when duplicate changes are unsafe. | HTMX/server |
| Success | `200 OK` replaces the region with confirmed state and optional polite status. | Restore checkbox focus by stable ID after swap. | HTMX/server |
| Empty | Not applicable: one switch always has a supplied state. | Not applicable. | Caller |
| Partial values | Do not render without required labels; use caller-formatted fallback only when authoritative. | No interactive fallback. | Caller |
| Request failure | Transport failure retains the current region; HTMX/server shows visible error outside it. | Retain checkbox focus; offer server-owned retry. | HTMX/server |
| Action failure | Return confirmed state plus `Feedback.IsError=true`; do not client-roll back. | Restore focus by stable ID after swap; offer server retry. | HTMX/server |

## Accessibility and responsive checks

- Use a native checkbox and a visible associated label; do not add `role="switch"` to a wrapper containing the checkbox.
- Ensure Space, pointer activation, native checked/disabled semantics, and visible focus work; do not add a duplicate keyboard handler.
- Keep label, current state text, and feedback visible; color and thumb position are supplementary only.
- Preserve source-order focus, restore focus to the stable checkbox after parent replacement, and announce asynchronous status politely or failures assertively.
- Maintain at least a 44 CSS-pixel target, usable 200% zoom, reflow on narrow screens, and no clipping or inaccessible overflow.

## Adaptation and test checklist

- Replace all fixture labels, ID, optional feedback, tokens, input-name behavior, and event consumer with approved contracts.
- Do not place the switch in a competing form submission contract.
- Test checked/unchecked label pairs, disabled/busy states, feedback absent/status/error, pointer and Space activation, and `on-off-switch:change` detail.
- Test accessible name, native checked and disabled semantics, focus visibility/restoration, color-independent state, target size, zoom, and narrow layout.
- Test `PATCH /ui/components/v1/on-off-switches/{id}` with `checked=true` and `checked=false`, `HX-Request: true`, `text/html`/`no-store` response, confirmed whole-region response, validation/action-error fragment, transport-error retention, focus restoration, and retry. Capture runnable-route visual evidence where supported.

## Provenance and limitations

Observed user-supplied markup on 2026-09-05: a labelled checkbox switch with `Active` and `Paused` labels, checked state, and control/text spans. This reference design replaces the wrapper `role="switch"` with native checkbox semantics to avoid competing controls, and adds the view model, event, feedback, CSS, and state guidance. User-supplied contract intent on 2026-09-06 establishes independent HTMX component endpoints under `/ui/components/v1`. Intentionally unsupported: tri-state values, client-owned optimistic state, parent-form submission, and nested controls.
