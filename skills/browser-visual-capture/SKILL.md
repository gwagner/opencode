---
name: browser-visual-capture
description: Captures deterministic baseline and post-change Chromium screenshots for one URL or URL set. Use when frontend validation needs reproducible visual artifacts.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: browser-visual-capture
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: browser-visual-capture
inputs:
  - URLs
  - capture phase
  - deterministic run ID and viewport
---

# Browser Visual Capture

Use this skill to capture screenshots before and after a frontend change. It does not evaluate whether differences are acceptable; the caller owns any separate comparison procedure.

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
node /code/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
  --phase baseline \
  --run-id checkout-button \
  https://example.test/page
```

Post-change capture with the same `--run-id` keeps results grouped for comparison:

```sh
node /code/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
  --phase post-change \
  --run-id checkout-button \
  https://example.test/page
```

Multiple URLs may be positional arguments or a file with one URL per line:

```sh
node /code/skills/browser-visual-capture/scripts/capture-screenshots.mjs \
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

1. Identify each affected user-visible route and its documented run mechanism.
2. Capture baseline screenshots before the UI change.
3. Implement the UI change.
4. Capture post-change screenshots with the same URLs, viewport, and `--run-id`.
5. Return the pair to the caller for any separately owned comparison procedure and task-specific expectation manifest derived from approved acceptance criteria.
6. Report saved paths and any capture failures from the JSON summaries.

## Unrunnable-route gap

If an affected route cannot be run with documented project tooling, do not treat visual validation as skipped. Report the route, missing run mechanism or fixture, acceptance criteria for baseline/post-change capture, and available evidence so the caller can own any separate follow-up procedure. Do not invent a server command or a mock route.

## Failure behavior

- Invalid or unreachable URLs are recorded in `summary.json` with an error.
- Successful URLs still produce screenshots when other URLs fail.
- The script exits nonzero if any URL fails, so validation can surface partial failure without hiding saved artifacts.
