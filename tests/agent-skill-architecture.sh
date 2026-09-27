#!/bin/sh
# shellcheck disable=SC2016 # Backticks are literal Markdown assertions.
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH='' cd -- "$script_dir/.." && pwd)

root_agents="$root/AGENTS.md"
grep -Fq 'dynamically resolve `/code` by running `git rev-parse --show-toplevel`' "$root_agents"
grep -Fq 'returned Git root of the current linked worktree is the code root' "$root_agents"
grep -Fq 'Resolve `/project` from the `references.docs.path` value in `/code/.opencode/opencode.json`.' "$root_agents"
grep -Fq 'exact path `/code` or `/project`, or when it is followed immediately by `/`' "$root_agents"
grep -Fq 'Preserve the unmatched suffix' "$root_agents"
grep -Fq 'resolve `/code/src` but do not rewrite `/codebase`' "$root_agents"
grep -Fq '`.opencode/opencode.json` is missing or malformed' "$root_agents"
grep -Fq '`references.docs.path` is missing' "$root_agents"
grep -Fq 'configured docs directory is missing or inaccessible' "$root_agents"
grep -Fq 'treat `/project` as not configured and continue without project documentation' "$root_agents"
grep -Fq 'None of these conditions is a blocker.' "$root_agents"
if grep -Fq 'important-paths.md' "$root_agents"; then
  printf '%s\n' 'root agent instructions still depend on important-paths.md' >&2
  exit 1
fi

for file in "$root"/agents/*.md; do
  expected=$(basename "$file" .md)
  grep -q "^name: $expected$" "$file"
done

for file in "$root"/skills/*/SKILL.md; do
  expected=$(basename "$(dirname "$file")")
  grep -q "^name: $expected$" "$file"
done

reference_skill="$root/skills/frontend-reference-examples"
grep -q '^name: frontend-reference-examples$' "$reference_skill/SKILL.md"
grep -q '\[Data table\](references/data-table.md)' "$reference_skill/index.md"
test -f "$reference_skill/references/data-table.md"
test ! -e "$reference_skill/monitor-check-history-table.md"
grep -q 'not an approved adopter contract' "$reference_skill/references/data-table.md"
grep -q 'does not fetch' "$reference_skill/references/data-table.md"
grep -q '^## Semantic template$' "$reference_skill/references/data-table.md"
grep -q '^type DataTableView struct {$' "$reference_skill/references/data-table.md"
grep -q 'data-table:activate' "$reference_skill/references/data-table.md"
grep -q 'data-table:page-activate' "$reference_skill/references/data-table.md"

grep -q 'node /code/skills/browser-visual-capture/scripts/capture-screenshots.mjs' "$root/skills/browser-visual-capture/SKILL.md"
if grep -q '/project/.opencode/skills/browser-visual-capture/scripts' "$root/skills/browser-visual-capture/SKILL.md"; then
  printf '%s\n' 'browser-capture skill still depends on the runtime mirror path' >&2
  exit 1
fi

grep -q 'only when approved requirements or an explicit architecture decision establishes it' "$root/skills/frontend-component-modeling/SKILL.md"
reverse_engineer="$root/agents/reverse-engineer-app-spec.md"
grep -q '^    "/project/context.md": allow$' "$reverse_engineer"
grep -q '^    "/project/handoff.md": allow$' "$reverse_engineer"

detector="$root/agents/spec-gap-detector.md"
handoff="$root/skills/specification-gap-handoff/SKILL.md"
test ! -e "$root/agents/reconcile-spec-to-code.md"
grep -q '^  task: deny$' "$detector"
grep -q '^    "/code/specification-gaps.md": allow$' "$detector"
grep -q 'Your sole artifact is `/code/specification-gaps.md`' "$detector"
grep -q 'Never delegate directly' "$detector"
grep -q '^name: specification-gap-handoff$' "$handoff"
grep -q '`implemented-without-authority`' "$handoff"
grep -q 'assign the earliest authoritative owner' "$handoff"
grep -q 'Report `implementation-divergence` separately and omit `internal-detail`' "$handoff"

for owner in prd-strategist app-spec-architect code-spec-engineer; do
  file="$root/agents/$owner.md"
  grep -q '^    "python3 /project/\.opencode/scripts/retrieve-knowledge\.py \*": allow$' "$file"
done

issue_worktree_skill="$root/skills/issue-worktree-validation/SKILL.md"
issue_contract="$root/skills/github-work-issue-contract/SKILL.md"
github_sdlc="$root/agents/github-sdlc.md"
issue_manager="$root/agents/github-issue-manager.md"
sdlc_orchestrator="$root/agents/sdlc-orchestrator.md"

assert_primary_implementation_route() {
  awk '
    /^        - when: "?Any approved action edits an agent or skill\."?$/ { if (state == 0) state = 1 }
    /^          agent: "?agent-builder"?$/ { if (state == 1) state = 2 }
    /^        - when: "?.*defect requiring diagnosis and correction\."?$/ { if (state == 2) state = 3 }
    /^          agent: "?bug-fixer"?$/ { if (state == 3) state = 4 }
    /^        - when: "?otherwise"?$/ { if (state == 4) state = 5 }
    /^          agent: "?code-implementor"?$/ { if (state == 5) state = 6 }
    END { exit state != 6 }
  ' "$1"
}

test -f "$github_sdlc"
test -f "$issue_manager"
test ! -e "$root/agents/todo-planner.md"
test ! -e "$root/skills/git-auto-commit/SKILL.md"
test ! -e "$root/skills/github-issue-state-change/SKILL.md"
grep -Fq -- '- `Execution route` — exactly `github-sdlc` for every ready issue.' "$issue_contract"
grep -Fq 'MUST hand the request to `github-sdlc`' "$issue_contract"
grep -Fq 'Any other agent MUST NOT process this issue directly.' "$issue_contract"
grep -Fq 'does not natively select, route, or dispatch an OpenChamber agent' "$issue_contract"
grep -q '^description: .*fast-forwards a clean issue worktree to refreshed origin/main before implementation\.$' "$issue_worktree_skill"
grep -q '^    "git fetch origin main": allow$' "$issue_worktree_skill"
grep -q '^    "git rev-parse origin/main": allow$' "$issue_worktree_skill"
grep -q '^    "git merge-base --is-ancestor HEAD origin/main": allow$' "$issue_worktree_skill"
grep -q '^    "git merge --ff-only origin/main": allow$' "$issue_worktree_skill"
if grep -Eqi 'caller[- ]attest|attestation' "$issue_worktree_skill"; then
  printf '%s\n' 'issue-worktree validation still requires caller attestation' >&2
  exit 1
fi
grep -Fq 'refreshed `origin/main` equality or safe fast-forward' "$issue_worktree_skill"
grep -Fq 'sufficient alternate safety evidence to begin implementation' "$issue_worktree_skill"
grep -Fq 'They establish current-worktree eligibility, not OpenChamber lifecycle provenance' "$issue_worktree_skill"
grep -Fq 'Do not request or block on provenance evidence that is not machine-verifiable.' "$issue_worktree_skill"
grep -Fq 'Require distinct resolved directories' "$issue_worktree_skill"
grep -Fq 'Require the current root to appear exactly once and reject duplicate, missing, detached, locked, or prunable entries' "$issue_worktree_skill"
grep -Fq 'Require a nonempty branch other than `main`.' "$issue_worktree_skill"
grep -Fq 'Require no staged, unstaged, untracked, or conflicted state before implementation begins.' "$issue_worktree_skill"
grep -Fq 'do not fetch or synchronize' "$issue_worktree_skill"
grep -Fq 'retain the status and HEAD as recovery evidence' "$issue_worktree_skill"
grep -Fq 'run `git merge-base --is-ancestor HEAD origin/main`' "$issue_worktree_skill"
grep -Fq 'updated with `git merge --ff-only origin/main`' "$issue_worktree_skill"
grep -Fq 'This is the only permitted synchronization' "$issue_worktree_skill"
grep -Fq 'a branch that is ahead of or divergent from refreshed `origin/main`' "$issue_worktree_skill"
grep -Fq 'preserve the branch as recovery evidence' "$issue_worktree_skill"
grep -Fq 'Require `openchamber:ready`, absence of `openchamber:blocked`, and an `Execution route` equal to the active agent identity.' "$issue_worktree_skill"
grep -Fq 'require caller-provided evidence that every referenced issue is closed' "$issue_worktree_skill"
if grep -q 'git rev-parse main' "$issue_worktree_skill"; then
  printf '%s\n' 'issue-worktree validation still compares against local main' >&2
  exit 1
fi
grep -q 'refreshed remote-main revision' "$issue_worktree_skill"
grep -Fq 'recreate the issue worktree from the named refreshed remote-main revision' "$issue_worktree_skill"
grep -q '^    "git merge-base --is-ancestor HEAD origin/main": allow$' "$github_sdlc"
grep -q '^    "git merge --ff-only origin/main": allow$' "$github_sdlc"
grep -Fq 'performs its only permitted safe fast-forward' "$github_sdlc"
grep -Fq 'Local `main` is the OpenChamber creation starting point' "$issue_contract"
grep -Fq 'may fast-forward only a clean eligible issue branch when Git proves it is a true fast-forward' "$issue_contract"
grep -Fq 'A dirty, ahead, or divergent branch remains blocked with recovery evidence' "$issue_contract"
grep -q '^  read: allow$' "$root/skills/github-blocked-issue-resolution/SKILL.md"
grep -Fq 'caller-permitted paths to authoritative sources' "$root/skills/github-blocked-issue-resolution/SKILL.md"

assert_primary_implementation_route "$github_sdlc"
assert_primary_implementation_route "$sdlc_orchestrator"

for skill in issue-worktree-validation git-change-baseline git-delegated-change-commit \
  github-pr-publication github-pr-check-validation github-pr-approved-merge \
  github-issue-comment github-issue-close; do
  test -f "$root/skills/$skill/SKILL.md"
  grep -q "^    $skill: allow$" "$github_sdlc"
  grep -q "^    skill: $skill$" "$github_sdlc"
done
grep -Fq 'Approve squash-merging this exact pull request head and deleting its remote feature branch?' "$github_sdlc"
grep -Fq 'id: pre-closure-update' "$github_sdlc"
grep -Fq 'The pre-closure issue update was verified for the unchanged pull-request head.' "$github_sdlc"
grep -Fq 'gh issue comment --attach' "$github_sdlc"
grep -q '^    "gh issue comment --help": allow$' "$github_sdlc"
grep -Fq 'never use HTTP/API upload workarounds' "$github_sdlc"
grep -Fq 'pre-closure issue update' "$issue_contract"
grep -Fq 'gh issue comment --attach' "$issue_contract"
grep -Fq 'When browser impact is absent, the update must state that visual evidence is not required.' "$issue_contract"
issue_comment="$root/skills/github-issue-comment/SKILL.md"
grep -Fq '"gh issue comment * --body-file /tmp/opencode/github-issue-manager-comment.md": allow' "$issue_comment"
grep -Fq '"gh issue comment * --body-file /tmp/opencode/github-issue-manager-comment.md --attach *": allow' "$issue_comment"
grep -Fq 'native `gh issue comment --attach`' "$issue_comment"
grep -Fq 'run `gh issue comment --help`. Stop unless it lists `--attach`.' "$issue_comment"
grep -Fq 'never use an HTTP/API upload workaround' "$issue_comment"
grep -q '^    "gh issue comment --help": allow$' "$issue_manager"
grep -Fq '"gh issue comment * --body-file /tmp/opencode/github-issue-manager-comment.md --attach *": allow' "$issue_manager"
grep -q '^    "/tmp/opencode/\*\*": allow$' "$issue_manager"
for delegate in code-implementor bug-fixer; do
  file="$root/agents/$delegate.md"
  grep -Fq 'same-scenario baseline and post-change screenshot paths under `/tmp/opencode`' "$file"
done
for visual_skill in browser-visual-capture browser-visual-compare frontend-impact-validation; do
  if grep -q '"/tmp/\*\*": allow' "$root/skills/$visual_skill/SKILL.md"; then
    printf '%s\n' "$visual_skill still permits artifacts outside /tmp/opencode" >&2
    exit 1
  fi
done
grep -Fq "const TEMP_ROOT = '/tmp/opencode';" "$root/skills/browser-visual-capture/scripts/capture-screenshots.mjs"
grep -Fq "const TEMP_ROOT = '/tmp/opencode';" "$root/skills/browser-visual-compare/scripts/compare-screenshots.mjs"
approved_merge="$root/skills/github-pr-approved-merge/SKILL.md"
check_validation="$root/skills/github-pr-check-validation/SKILL.md"
grep -Fq 'explicit user merge approval naming the exact pull request and head commit' "$approved_merge"
grep -q '^    "gh pr merge \* --squash --match-head-commit \*": allow$' "$approved_merge"
grep -q '^    "git ls-remote --heads origin \*": allow$' "$approved_merge"
grep -q '^    "git push origin --delete \*": allow$' "$approved_merge"
for file in "$check_validation" "$approved_merge"; do
  grep -q '^    "gh pr checks \* --required --json bucket,name,state,workflow,link": allow$' "$file"
  grep -q '^    "gh api --include repos/\*/branches/\*/protection": allow$' "$file"
  grep -Fq "'gh api \"repos/*/rulesets?includes_parents=true\"': allow" "$file"
  grep -Fq "stderr is exactly \`no required checks reported on the '<head branch>' branch\`" "$file"
  grep -Fq 'where `<head branch>` is the exact checked `headRefName`' "$file"
  grep -Fq 'verify configuration instead of accepting the CLI outcome alone' "$file"
  grep -Fq 'HTTP status `404` and a parseable JSON `message` exactly `Branch not protected`' "$file"
  grep -Fq 'Only that combination verifies zero configured required checks' "$file"
  grep -Fq 'failed, pending, cancelled, skipped-required, timed-out, unavailable, and ambiguous evidence' "$file"
  if grep -Fq 'A successful empty array (`[]`) is a verified empty required-check set and passes.' "$file"; then
    printf '%s\n' "$file still accepts empty required checks without configuration evidence" >&2
    exit 1
  fi
done
grep -q '^    "gh pr view \* --json number,url,state,baseRefName,headRefName,headRefOid": allow$' "$check_validation"
grep -Fq 'require the head commit, head branch, and base branch to remain unchanged.' "$check_validation"
grep -Fq 'gh pr merge <pr> --squash --match-head-commit <approved head>' "$approved_merge"
grep -Fq 'Require open state, base `main`, mergeable status, an exact match between its head, the approved head, and the passed-check evidence, and unchanged head commit, head branch, and base branch.' "$approved_merge"
grep -Fq 'require a second `git ls-remote --heads origin <head branch>` to return no ref' "$approved_merge"
grep -Fq 'Never delete or switch the local branch or worktree.' "$approved_merge"
grep -q '^    "gh pr merge \* --squash --match-head-commit \*": allow$' "$github_sdlc"
grep -q '^    "git ls-remote --heads origin \*": allow$' "$github_sdlc"
grep -q '^    "git push origin --delete \*": allow$' "$github_sdlc"
grep -q '^    "gh pr checks \* --required --json bucket,name,state,workflow,link": allow$' "$github_sdlc"
grep -q '^    "gh api --include repos/\*/branches/\*/protection": allow$' "$github_sdlc"
grep -Fq "'gh api \"repos/*/rulesets?includes_parents=true\"': allow" "$github_sdlc"
grep -Fq 'known CLI 2.100.0 outcome of exit `1`, empty stdout' "$github_sdlc"
grep -Fq "stderr \`no required checks reported on the '<head branch>' branch\`, where \`<head branch>\` is the exact checked pull-request head branch" "$github_sdlc"
grep -Fq 'HTTP `404` with JSON `message` `Branch not protected`' "$github_sdlc"
grep -Fq 'Failed, pending, cancelled, skipped-required, timed-out, unavailable, or other ambiguous evidence blocks.' "$github_sdlc"
grep -Fq 'Optional checks never become required.' "$github_sdlc"
if grep -Fq 'verified empty required-check set' "$github_sdlc"; then
  printf '%s\n' 'github-sdlc still accepts empty required checks without configuration evidence' >&2
  exit 1
fi

for skill in github-work-issue-contract github-issue-capture \
  github-blocked-issue-resolution github-issue-update github-issue-comment \
  github-issue-close github-issue-reopen github-issue-deletion; do
  test -f "$root/skills/$skill/SKILL.md"
  grep -q "^    $skill: allow$" "$issue_manager"
done
grep -Fq 'contract_status `validated_ready`' "$issue_manager"
grep -Fq 'Reuse complete authority unchanged.' "$issue_manager"
grep -Fq 'Delegate only incomplete authority, serially, to `prd-strategist`, then `app-spec-architect`, then `code-spec-engineer`.' "$issue_manager"
grep -Fq 'agent: prd-strategist' "$issue_manager"
grep -Fq 'agent: app-spec-architect' "$issue_manager"
grep -Fq 'agent: code-spec-engineer' "$issue_manager"
grep -Fq 'Re-read each returned path' "$issue_manager"
grep -Fq 'use `grillme` once with established context, re-evaluate its answer, and ask no further question until that re-evaluation identifies another blocker.' "$issue_manager"
grep -Fq 'requires refusal: report the blocker and exact next need without calling capture or creating an issue.' "$issue_manager"
grep -Fq 'Pass only a `new_candidate` with complete authority to `github-work-issue-contract`' "$issue_manager"
grep -Fq 'call capture only when it returns `contract_status: validated_ready`.' "$issue_manager"
grep -Fq 'A duplicate open issue is returned without mutation.' "$issue_manager"
grep -Fq 'github-blocked-issue-resolution' "$issue_manager"
grep -Fq 'Existing issues bypass new-candidate readiness and retain their applicable operation, including `github-blocked-issue-resolution` for blocked-state reconciliation.' "$issue_manager"

# Authority gaps are owned in upstream-to-downstream order; complete authority
# has no owner stage whose condition can apply.
assert_authority_owner_order() {
  awk '
    /^  - id: product-authority$/ { if (state == 0) state = 1; next }
    /^    when: "Verified readiness assessment identifies missing or changed product intent\."$/ { if (state == 1) state = 2; next }
    /^    agent: prd-strategist$/ { if (state == 2) state = 3; next }
    /^  - id: shared-authority$/ { if (state == 3) state = 4; next }
    /^    when: "Verified readiness assessment identifies missing shared architecture or a cross-feature decision after product intent is sufficient\."$/ { if (state == 4) state = 5; next }
    /^    agent: app-spec-architect$/ { if (state == 5) state = 6; next }
    /^  - id: feature-authority$/ { if (state == 6) state = 7; next }
    /^    when: "Verified readiness assessment identifies a missing bounded feature contract after upstream authority is sufficient\."$/ { if (state == 7) state = 8; next }
    /^    agent: code-spec-engineer$/ { if (state == 8) state = 9; next }
    END { exit state != 9 }
  ' "$1"
}
assert_authority_owner_order "$issue_manager"

if grep -Fq 'gh issue create --title * --body-file /tmp/opencode/github-issue-manager-issue.md --label openchamber:blocked' "$issue_manager"; then
  printf '%s\n' 'github-issue-manager still permits new blocked issue creation' >&2
  exit 1
fi
for lifecycle in new_candidate existing_issue; do
  grep -Fq "$lifecycle" "$issue_contract"
done
for failure in authority_missing authority_conflict blocking_question non_atomic_scope schema_incomplete route_unknown new_blocked_forbidden; do
  grep -Fq "$failure" "$issue_contract"
done
grep -Fq 'contract_status: validated_ready' "$issue_contract"
grep -Fq 'For `lifecycle_context: new_candidate`, return `contract_status: validated_ready` only when authority is complete and consistent, there are no blocking questions, the scope is atomic, the route is known, and the complete ready schema is present.' "$issue_contract"
grep -Fq '`status_label: openchamber:ready`, `execution_route: github-sdlc`' "$issue_contract"
grep -Fq 'Reject any `new_candidate` that selects or contains blocked status as `new_blocked_forbidden`.' "$issue_contract"
grep -Fq 'Only for `lifecycle_context: existing_issue`, a blocked issue may have `openchamber:blocked`' "$issue_contract"
grep -Fq 'contract_status: validated_ready' "$root/skills/github-issue-capture/SKILL.md"
grep -Fq 'verified authority references' "$root/skills/github-issue-capture/SKILL.md"
capture_skill="$root/skills/github-issue-capture/SKILL.md"
grep -Fq 'Never infer readiness from a caller assertion.' "$capture_skill"
grep -Fq 'If an equivalent open issue exists, return its URL and do not create another issue.' "$capture_skill"
grep -Fq 'Never coordinate authority, infer readiness, create a blocked issue, or mutate an existing issue.' "$capture_skill"
grep -Fq 'Create exactly one ready issue with `gh issue create --title <title> --body-file /tmp/opencode/github-issue-manager-issue.md --label openchamber:ready`.' "$capture_skill"
grep -Fq 'Completion requires an open issue, the exact canonical body, `openchamber:ready`, and absence of `openchamber:blocked`.' "$capture_skill"
grep -Fq 'execution_route: github-sdlc' "$capture_skill"
if grep -Fq 'gh label create openchamber:blocked' "$capture_skill" || \
  grep -Fq 'gh issue create --title * --body-file /tmp/opencode/github-issue-manager-issue.md --label openchamber:blocked' "$capture_skill" || \
  grep -Fq 'ready or blocked status' "$capture_skill"; then
  printf '%s\n' 'github-issue-capture still contains blocked-label creation or input behavior' >&2
  exit 1
fi
grep -Fq 'explicitly confirms permanent deletion of that exact issue in the current turn' "$root/skills/github-issue-deletion/SKILL.md"

for delegate in agent-builder bug-fixer code-implementor api-integration-tester; do
  file="$root/agents/$delegate.md"
  grep -q 'Never stage, commit, push' "$file"
  if grep -Eq '^    "git (add|commit)|^    (git-auto-commit|git-delegated-change-commit): allow$|^  - id: "?[^"[:space:]]*commit' "$file"; then
    printf '%s\n' "$delegate still owns a commit permission, skill, or stage" >&2
    exit 1
  fi
done

grep -q '^    git-delegated-change-commit: allow$' "$sdlc_orchestrator"
grep -q '^  - id: "implementation-commit"$' "$sdlc_orchestrator"
grep -q '^  - id: "api-integration-tests"$' "$sdlc_orchestrator"
grep -q '^    when: "Implementation changed an API endpoint, API contract,' "$sdlc_orchestrator"
grep -q '^    agent: "api-integration-tester"$' "$sdlc_orchestrator"
grep -q '^  - id: "api-test-commit"$' "$sdlc_orchestrator"
grep -Fq 'Delegates never stage or commit.' "$sdlc_orchestrator"
grep -Fq 'Do not merge, delete the branch, push, open a pull request, mutate a GitHub issue, or contact a remote.' "$sdlc_orchestrator"
if grep -Eq '^    "(git push|gh )' "$sdlc_orchestrator"; then
  printf '%s\n' 'sdlc-orchestrator still has remote lifecycle permissions' >&2
  exit 1
fi

grep -q 'under `/code/specification/`' "$root/agents/reverse-engineer-app-spec.md"
grep -q '/project/.opencode/scripts/retrieve-knowledge.py' "$root/skills/okf-reader/SKILL.md"
if grep -R -q '/code/scripts/retrieve-knowledge.py' "$root/agents" "$root/skills"; then
  printf '%s\n' 'retrieval workflow still uses the application code mount' >&2
  exit 1
fi
