---
name: issue-worktree-validation
description: Verifies that one user-requested attached issue has a clean existing OpenChamber worktree before implementation.
classification: technical
opencode_permission:
  shell:
    "python3 /code/skills/openchamber-worktree-validation/scripts/validate-worktree.py *": allow
  external_directory:
    "/code/skills/openchamber-worktree-validation/scripts/validate-worktree.py": allow
  skill:
    openchamber-worktree-validation: allow
inputs:
  - user-requested attached issue context
  - current OpenChamber-linked worktree
  - expected base branch
---

# Issue worktree validation

## Inputs

Require a user-requested attached issue context, the current OpenChamber-linked worktree, and its expected base branch.

## Workflow

```yaml
request: "One user-requested attached issue worktree disposition."
workflow:
  - id: worktree
    when: "Implementation is requested for the attached issue."
    skill: openchamber-worktree-validation
```

## Procedure

Require caller-supplied evidence that the user requested implementation of the attached issue and that dependencies are resolved, then invoke `openchamber-worktree-validation`. Issue labels are informational and do not dispatch work.

## Completion

Report the attached issue identity, worktree disposition, and blocker.
