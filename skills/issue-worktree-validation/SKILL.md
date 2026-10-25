---
name: issue-worktree-validation
description: Adds issue readiness and dependency gates to deterministic OpenChamber worktree validation.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py *": allow
  external_directory:
    "/code/skills/github_lifecycle_policy.py": allow
    "/tmp/opencode/lifecycle-policy.snapshot.json": allow
    "/code/skills/openchamber-worktree-validation/scripts/validate-worktree.py": allow
  skill:
    openchamber-worktree-validation: allow
inputs:
  - resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest
  - attached GitHub issue context
  - fresh-start or resumable lifecycle disposition
  - expected execution route
  - dependency closure evidence when dependencies are declared
  - current OpenChamber-linked worktree
---

# Issue worktree validation

## Inputs

Require the attached GitHub issue context, a fresh-start or resumable lifecycle disposition, the expected execution route, dependency closure evidence when dependencies are declared, the current OpenChamber-linked worktree, and an resolved `/tmp/opencode/lifecycle-policy.snapshot.json` and its expected digest.

## Workflow

```yaml
request: "One issue-eligible OpenChamber worktree disposition."
workflow:
  - id: worktree
    when: "After lifecycle recovery identifies a local-worktree stage."
    skill: openchamber-worktree-validation
```

## Procedure

1. Require the issue to be open with `openchamber:ready`, without `openchamber:blocked`, and with `Execution route` equal to `sdlc-orchestrator`.
2. Require verified closure evidence for every declared dependency. Return `waiting-external` when dependency state cannot currently be verified; do not infer closure.
3. Invoke `openchamber-worktree-validation` with the same policy in `fresh` mode for a fresh start, `resume-publication` mode with the expected head for resumable local publication, or `resume-pull-request` mode with the expected head for a recovered open pull request.
4. Continue to ownership baseline only on `passed` or `resume-pull-request`, and continue only to publication on `resume-publication`. Preserve and return every other disposition unchanged.

## Boundaries

- Never create, remove, prune, move, repair, or switch a worktree or branch.
- Never edit files, implement issue work, or mutate GitHub.
- Labels and route text are repository conventions, not native OpenChamber dispatch.

## Completion

Report issue readiness, route match, dependency state, worktree disposition, branch, head, base revision, and blocker.
