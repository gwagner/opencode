---
name: frontend-reference-lookup
description: Selects a matching frontend reference catalog entry for a bounded component or route without adapting code.
classification: non-technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
inputs:
  - component or route scope
  - approved behavior
  - caller-provided permitted frontend reference catalog paths
---

# Frontend reference lookup

## Inputs

Require component or route scope, approved behavior, and caller-provided permitted frontend reference catalog paths.

## Procedure

1. Read the catalog `index.md` and match by component name, alias, purpose, or interaction.
2. Read only the matching entry or entries needed to distinguish a match.
3. Report the selected entry, relevant semantic or interaction evidence, and no-match result when applicable.
4. Do not edit code, adapt a reference, capture visuals, or validate a route.

## Completion

Report `passed` with the selected path and evidence, or `blocked` when the catalog or approved behavior is unavailable.
