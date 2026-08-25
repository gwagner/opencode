---
name: browser-visual-capture
description: Captures baseline and post-change Chromium screenshots for one URL or URL sets to validate expected UI changes with deterministic visual-comparison settings.
---

# Browser Visual Capture

Use this skill when validating UI changes with screenshots before and after a code change.

## What it does

- Accepts one URL or many URLs.
- Launches Chromium with Chrome DevTools Protocol automation.
- Captures `baseline` or `post-change` screenshots.
- Saves PNG files and a JSON summary under `/tmp/` by default.
- Uses deterministic viewport, device scale factor, reduced motion, light color scheme, and fixed post-load wait.
- Reports every saved path and records graceful failures for unreachable pages.

## Prerequisites

- Node.js 20+.
- A Chromium-compatible executable available as `chromium`, `chromium-browser`, or `google-chrome`.
- No npm packages are required. Playwright is acceptable for manual alternatives, but the included script uses Chromium DevTools directly.
- Containerized environments are supported; Chromium is launched headless with sandbox disabled.

## Script

Run from any directory:

```sh
node /project/.opencode/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
  --phase baseline \
  --run-id checkout-button \
  https://example.test/page
```

Post-change capture with the same `--run-id` keeps results grouped for comparison:

```sh
node /project/.opencode/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
  --phase post-change \
  --run-id checkout-button \
  https://example.test/page
```

Multiple URLs may be positional arguments or a file with one URL per line:

```sh
node /project/.opencode/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
  --phase baseline \
  --urls-file /tmp/urls.txt \
  --viewport 1440x900 \
  --wait-ms 1000
```

## Options


| Option | Default | Notes |
| --- | --- | --- |
| `--phase baseline\|post-change` | required | Capture phase in filenames and summary. |
| `--run-id <id>` | timestamp | Collision-safe directory name. Reuse for baseline/post-change pair. |
| `--output-dir <path>` | `/tmp/opencode-browser-visual-capture` | Parent directory for run output; must stay under `/tmp/`. |
| `--urls-file <path>` | none | Reads one URL per line; blank lines and `#` comments ignored. |
| `--viewport <WxH>` | `1280x720` | Deterministic screenshot viewport. |
| `--wait-ms <ms>` | `750` | Fixed wait after page load for stable UI. |
| `--timeout-ms <ms>` | `15000` | Per-page navigation timeout. |
| `--chrome <path>` | auto-detect | Chromium executable. |

## Workflow

1. Capture baseline screenshots before the UI change.
2. Implement the UI change.
3. Capture post-change screenshots with the same URLs, viewport, and `--run-id`.
4. Compare the saved PNGs manually or with an image-diff tool.
5. Report saved paths and any failures from the JSON summary.

## Failure behavior

- Invalid or unreachable URLs are recorded in `summary.json` with an error.
- Successful URLs still produce screenshots when other URLs fail.
- The script exits nonzero if any URL fails, so validation can surface partial failure without hiding saved artifacts.
