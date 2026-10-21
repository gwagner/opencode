---
name: git-agent-skill-change-publication
description: Commits and pushes one validated directly owned agent or skill change batch without creating a pull request.
classification: technical
opencode_permission:
  read: allow
  shell:
    "git branch --show-current": allow
    "git status --porcelain=v1 -z": allow
    "git diff -- *": allow
    "git add -- *": allow
    "git diff --cached -- *": allow
    "git commit -m *": allow
    "git rev-parse HEAD": allow
    "git ls-remote --heads origin *": allow
    "git push --set-upstream origin *": allow
inputs:
  - explicit direct agent-builder commit-and-push authorization
  - pre-edit ownership baseline from git-change-baseline
  - one completed agent or skill change batch
  - caller-permitted changed agent, skill, and required root README paths
  - passed project-validation result
  - current Git worktree with an origin remote
---

# Git agent and skill change publication

## Inputs

Require explicit authorization for a directly invoked `agent-builder` to commit and push, a pre-edit ownership baseline from `git-change-baseline`, one completed agent or skill change batch, caller-permitted changed paths under `/code/agents/**` or `/code/skills/**` plus `/code/README.md` only when it directly documents that change, a passed `project-validation` result, and the current Git worktree with an `origin` remote. Read only the supplied changed paths; the caller remains the runtime path restrictor.

## Procedure

1. Stop unless `agent-builder` was directly invoked, the user explicitly authorized both commit and push, and the pre-edit baseline was captured before the first task-owned edit. A delegated invocation is ineligible even when its caller requests publication.
2. Run `git branch --show-current`. Require a nonempty branch other than `main`; never create, move, rename, or switch a branch.
3. Run `git status --porcelain=v1 -z`. Compare every changed path with the baseline and the completed change report. Stop on a staged path, an unreported path absent from the baseline, a change to a baseline path by this task, or any ownership ambiguity.
4. Require every task-owned path to be under `/code/agents/**` or `/code/skills/**`. Permit `/code/README.md` only when its changed content directly documents the same agent or skill behavior. Reject every other task-owned path.
5. Require the final `project-validation` status to be `passed`; reject failed, skipped, blocked, stale, or missing evidence. Review `git diff -- <owned paths>` for tracked changes and read each task-owned untracked path. Require the batch to match the approved scope and change report.
6. Resolve the pre-commit HEAD with `git rev-parse HEAD`, then run `git ls-remote --heads origin <branch>` once to require an available `origin` and record the remote branch state. When the remote branch exists, require its single object ID to equal the pre-commit HEAD so the later push cannot publish another unpushed commit. An absent remote branch is permitted only under the explicit push authorization.
7. Stage only the owned paths with `git add -- <owned paths>`, rerun `git status --porcelain=v1 -z`, and require the complete staged path set to equal the owned path set. Review `git diff --cached -- <owned paths>` and stop before committing if the staged content differs from the reviewed batch.
8. Create one descriptive commit with `git commit -m <message>`, passing the message as one data argument without evaluating its content. Resolve the commit with `git rev-parse HEAD`, rerun `git status --porcelain=v1 -z`, and require every remaining path to match a preserved baseline path.
9. Push only the current branch with `git push --set-upstream origin <branch>`. Never force-push. Run `git ls-remote --heads origin <branch>` and require its single returned object ID to equal the committed HEAD.

## Boundaries

- Never use this skill from a delegated `agent-builder` run; the calling orchestrator retains commit and publication ownership.
- Never commit an unvalidated, pre-existing, unrelated, unreported, or ambiguously owned path.
- Never amend, reset, restore, clean, stash, merge, pull, fetch, create or switch a branch, open a pull request, or mutate a worktree or GitHub issue.
- A commit that succeeds before a failed or unverifiable push remains a local commit and must be reported without retrying an ambiguous push.

## Completion

Report the branch, committed paths, commit object ID, preserved baseline paths, push result, verified remote object ID, and blockers.
