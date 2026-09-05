# On-off switch

## Match

**Component:** On-off switch. **Aliases:** toggle switch, boolean switch, active/inactive switch, on/off control, paused/running control, up/down control.

Use to change one independent, immediately understandable binary presentation state with caller-supplied labels. Suitable for settings or controls where either label pair describes the two possible states. Do not use for submitting a form, choosing among more than two options, destructive confirmation, or a navigation tab. Do not force checkboxes requiring a conventional checkmark, segmented controls, radio groups, or async action buttons into this reference.

This is adaptable implementation material, not product authority.

## Ownership and behavior contract

The component owns the visible label, native checkbox, track and thumb, current-state text, optional feedback, disabled and busy presentation, and `on-off-switch:change` event. The caller supplies formatted label, on/off labels, checked/disabled/busy state, optional input name, and optional feedback. It presents them without interpreting what either state means.

`on-off-switch:change` fires after a user changes the native checkbox. Its detail is `{ switchIdentity, checked, stateLabel }`; `switchIdentity` is the stable component ID, `checked` is the selected Boolean, and `stateLabel` is the matching caller-supplied label. Focus remains on the checkbox. Server, HTMX, or the parent owns requests, loading, errors, confirmed-state replacement, navigation, dialogs, and swaps. The JavaScript never rolls state back or replaces fragments.

Do not nest links, buttons, or other interactive controls inside the label. A parent may wrap the input in a form only when its own approved form contract supplies the name and submission behavior.

## Implementation-facing presentation model

```go
package presentation

// OnOffSwitchView contains display-ready values for an on-off switch.
type OnOffSwitchView struct {
	ID        string
	Label     string
	OnLabel   string
	OffLabel  string
	InputName string
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

`ID`, `Label`, `OnLabel`, and `OffLabel` are required. `ID` is a stable, non-empty, DOM-safe identity. `InputName` is optional and is only for a parent-owned form. `Feedback` is nil when there is none; `Message` is already localized text and `IsError` selects error presentation. `Checked`, `Disabled`, and `Busy` are explicit presentation states; disabled or busy controls must not accept changes. Format and localize all text and fallbacks before rendering; parse with `html/template` for contextual escaping. This Go model is a reusable presentation adapter, not evidence that an adopter uses Go. Other stacks should map this same shape illustratively.

## Semantic template

```gohtml
{{- $feedbackID := printf "%s-feedback" .ID -}}
<div data-on-off-switch data-on-off-switch-id="{{ .ID }}" {{ if .Busy }}aria-busy="true"{{ end }}>
  <input
    id="{{ .ID }}"
    data-on-off-switch-input
    type="checkbox"
    {{ if .InputName }}name="{{ .InputName }}"{{ end }}
    {{ if .Checked }}checked{{ end }}
    {{ if or .Disabled .Busy }}disabled{{ end }}
    {{ with .Feedback }}aria-describedby="{{ $feedbackID }}"{{ end }}
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

The native checkbox supplies the checked and disabled semantics. Optional `name`, described-by association, and feedback are omitted together when unavailable. Hooks support styles and the documented delegated event only.

## CSS rules

Use project tokens where available. `--on-off-switch-*` tokens respectively mean text, muted text, surface, border, on-state, focus ring, and error text.

```css
[data-on-off-switch] { color: var(--on-off-switch-text); max-width: 100%; }
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
| Loading | Keep label and selected state; wrapper is busy. | Retain checkbox focus; disable when duplicate changes are unsafe. | Server/HTMX/parent |
| Success | Show supplied selected label and optional polite status. | Keep checkbox focus. | Server/HTMX/parent |
| Empty | Not applicable: one switch always has a supplied state. | Not applicable. | Caller |
| Partial values | Do not render without required labels; use caller-formatted fallback only when authoritative. | No interactive fallback. | Caller |
| Request failure | Keep visible error feedback with alert semantics. | Restore/retain checkbox focus; offer parent-owned retry. | Server/HTMX/parent |
| Action failure | Render confirmed state plus visible error; do not client-roll back. | Restore focus by stable ID after a parent swap; offer retry. | Server/HTMX/parent |

## Accessibility and responsive checks

- Use a native checkbox and a visible associated label; do not add `role="switch"` to a wrapper containing the checkbox.
- Ensure Space, pointer activation, native checked/disabled semantics, and visible focus work; do not add a duplicate keyboard handler.
- Keep label, current state text, and feedback visible; color and thumb position are supplementary only.
- Preserve source-order focus, restore focus to the stable checkbox after parent replacement, and announce asynchronous status politely or failures assertively.
- Maintain at least a 44 CSS-pixel target, usable 200% zoom, reflow on narrow screens, and no clipping or inaccessible overflow.

## Adaptation and test checklist

- Replace all fixture labels, ID, optional feedback, tokens, input-name behavior, and event consumer with approved contracts.
- Confirm whether a form owner needs `InputName`; do not infer submission values or server routes.
- Test checked/unchecked label pairs, disabled/busy states, feedback absent/status/error, pointer and Space activation, and `on-off-switch:change` detail.
- Test accessible name, native checked and disabled semantics, focus visibility/restoration, color-independent state, target size, zoom, and narrow layout.
- Keep request, fragment, swap, retry, and confirmed-state tests with their server or HTMX owner; capture runnable-route visual evidence where supported.

## Provenance and limitations

Observed user-supplied markup on 2026-09-05: a labelled checkbox switch with `Active` and `Paused` labels, checked state, and control/text spans. This reference design replaces the wrapper `role="switch"` with native checkbox semantics to avoid competing controls, and adds the view model, event, feedback, CSS, and state guidance. No authoritative requirement, endpoint, request behavior, token system, or persistence behavior was supplied. Intentionally unsupported: tri-state values, client-owned optimistic state, and nested controls.
