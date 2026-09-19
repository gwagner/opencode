---
name: browser-visual-compare
description: Compares deterministic baseline/post-change screenshot pairs against structured visual expectations. Use after browser-visual-capture for automated frontend visual validation.
---

# Browser Visual Compare

## Deterministic workflow

```yaml
request: "Acceptance-driven visual comparison result"
workflow:
  - id: "capture-screenshot-pairs"
    when: "Before evaluating baseline and post-change screenshots."
    skill: "browser-visual-capture"
```

Use this skill after `browser-visual-capture`. The calling agent supplies task-specific expectations from approved acceptance criteria; this skill owns reusable pixel comparison and pass/fail mechanics. Never infer product expectations from the screenshots.

## CLI

```sh
node /code/skills/browser-visual-compare/scripts/compare-screenshots.mjs \
  --manifest /tmp/visual-expectations.json \
  --baseline-summary /tmp/opencode-browser-visual-capture/example/baseline-summary.json \
  --post-change-summary /tmp/opencode-browser-visual-capture/example/post-change-summary.json \
  --output /tmp/opencode-browser-visual-capture/example/comparison.json
```

`--output` defaults to `comparison.json` beside the post-change summary. Output must resolve under `/tmp/`. The comparator uses exact RGBA pixel differences, requires equal image dimensions, and needs no npm packages.

Exit codes:

| Code | Report outcome | Meaning |
| --- | --- | --- |
| `0` | `success` | Every expectation passed. |
| `2` | `failed_expectation` | Comparison ran, but at least one expectation failed. |
| `1` | `execution_error` | Inputs, PNG decoding, pairing, or execution failed. |

The CLI writes `comparison.json` for all comparison outcomes once it has a usable output path. Each comparison has `pass`, `fail`, or `error` status, metrics, and reasons.

## Expectation manifest contract

Use one entry per route and captured state. Routes must exactly match URLs in both capture summaries.

```json
{
  "version": 1,
  "comparisons": [
    {
      "id": "route-default",
      "route": "https://example.test/page",
      "state": "default",
      "expected": "changed",
      "allowedDiffThreshold": 0.05,
      "expectedChangedRegions": [
        { "x": 100, "y": 120, "width": 300, "height": 80 }
      ],
      "ignoredRegions": [
        { "x": 1100, "y": 0, "width": 180, "height": 40 }
      ],
      "rationale": "Approved acceptance criteria identify this bounded visual change.",
      "acceptanceOutcome": "The approved region changes and all other nonignored pixels remain stable."
    }
  ]
}
```

Required entry fields:

- `id`: unique nonempty identifier.
- `route`: exact captured URL.
- `state`: nonempty captured-state label; descriptive only, so the route must identify the actual captured fixture/state.
- `expected`: `unchanged` or `changed`.
- `allowedDiffThreshold`: maximum changed-pixel ratio from `0` through `1`, after ignored regions are excluded.
- `rationale`: why the expectation follows from approved criteria.
- `acceptanceOutcome`: observable outcome that constitutes acceptance.

Optional rectangle arrays use integer CSS-pixel coordinates `{x,y,width,height}` and must fit inside the screenshot:

- `ignoredRegions`: dynamic pixels excluded from all metrics and region checks.
- `expectedChangedRegions`: valid only for `changed`. Every listed region must contain a changed, nonignored pixel, and no changed, nonignored pixel may occur outside their union.

`unchanged` passes when its diff ratio is at most the threshold. `changed` additionally requires at least one changed pixel. Keep thresholds and regions acceptance-driven; do not loosen them merely to make a comparison pass. Selectors are not accepted because capture summaries do not preserve selector geometry; use approved pixel rectangles or improve the capture contract separately.

## Workflow

1. Derive the manifest from approved acceptance criteria before evaluating screenshots.
2. Capture baseline and post-change summaries with identical URL sets, viewport, and run ID.
3. Run the comparator and retain `comparison.json` with the capture artifacts.
4. Treat exit `2` as failed validation and exit `1` as an execution blocker. Report the report path and concise reasons; do not replace the structured result with manual judgment.
