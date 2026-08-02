---
name: tailwind
description: Configures Tailwind standalone CLI input, content scanning, generated CSS output, and backend static-file serving.
---

# Tailwind standalone CLI

Use when a TypeScript or server-rendered frontend needs generated Tailwind CSS without a bundler.

1. Locate the project-approved standalone CLI and declare its CSS input and generated output paths.
2. Scan every source that emits classes, including TypeScript, HTML, and server templates.
3. Keep generated CSS outside handwritten source paths and exclude it from content scanning.
4. Add focused build/watch commands only when supported by repository tooling.
5. Confirm the backend serves the generated output as a static asset with a stable URL.
