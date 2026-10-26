---
name: github-issue-capture
description: Creates or deduplicates one complete GitHub work issue in the current checkout's repository.
classification: technical
opencode_permission:
  shell:
    "gh auth status": allow
    "gh repo view --json nameWithOwner,url": allow
    "gh issue list --state open --limit 1000 --json number,title,body,labels,url": allow
    "gh issue create --title * --body-file /tmp/opencode/github-issue-manager-issue.md": allow
    "rm -f /tmp/opencode/github-issue-manager-issue.md": allow
  edit:
    "/tmp/opencode/github-issue-manager-issue.md": allow
inputs:
  - complete title and body for one atomic work item
  - current Git checkout with a GitHub origin
  - authenticated GitHub CLI
---

# GitHub issue capture

## Inputs

Require a complete title and body for one atomic work item, the current checkout's repository, and an authenticated GitHub CLI.

## Procedure

Verify authentication and repository identity. Compare the requested title and body with open issues. Return an equivalent issue without mutation when one exists. Otherwise write the body to `/tmp/opencode/github-issue-manager-issue.md`, create one issue, then remove the temporary file.

## Boundaries

Never create branches, start work, publish pull requests, or create blocked issues.

## Completion

Report the issue URL and whether it was created or deduplicated.
