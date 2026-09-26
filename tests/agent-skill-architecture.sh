#!/bin/sh
# shellcheck disable=SC2016 # Backticks are literal Markdown assertions.
set -eu

script_dir=$(CDPATH='' cd -- "$(dirname -- "$0")" && pwd)
root=$(CDPATH='' cd -- "$script_dir/.." && pwd)

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
grep -q '^- `Execution route` — exactly `agent-builder` when any approved action edits `agents/\*\*` or `skills/\*\*`, including defect correction and mixed-scope work; otherwise `bug-fixer`' "$issue_contract"
grep -q '^- `Processing handoff` — a required prominent section that repeats the exact literal `agent-builder`, `bug-fixer`, or `code-implementor` value from `Execution route`, not a placeholder\.' "$issue_contract"
grep -q 'initially active session agent MUST hand the request to `<exact route value>`' "$issue_contract"
grep -q 'An agent other than `<exact route value>` MUST NOT investigate, plan, or implement this issue' "$issue_contract"
grep -q 'does not natively select, route, or dispatch an OpenChamber agent' "$issue_contract"
grep -q '^description: .*refreshed origin/main\.$' "$issue_worktree_skill"
grep -q '^    "git fetch origin main": allow$' "$issue_worktree_skill"
grep -q '^    "git rev-parse origin/main": allow$' "$issue_worktree_skill"
grep -q 'Run `git fetch origin main`, then resolve `git rev-parse HEAD` and `git rev-parse origin/main`' "$issue_worktree_skill"
if grep -q 'git rev-parse main' "$issue_worktree_skill"; then
  printf '%s\n' 'issue-worktree validation still compares against local main' >&2
  exit 1
fi
grep -q 'refreshed remote-main revision' "$issue_worktree_skill"
grep -q 'create a fresh issue worktree from the newest remote `main`' "$issue_worktree_skill"
for route in agent-builder bug-fixer code-implementor; do
  grep -q '^    "git fetch origin main": allow$' "$root/agents/$route.md"
  grep -q '^    "git rev-parse origin/main": allow$' "$root/agents/$route.md"
done

agent_builder="$root/agents/agent-builder.md"
grep -q '^    "/code/\*\*": allow$' "$agent_builder"
grep -q '^    "/code/\.opencode/\*\*": deny$' "$agent_builder"
grep -q '^    issue-worktree-validation: allow$' "$agent_builder"
grep -q '^    git-change-baseline: allow$' "$agent_builder"
grep -q '^    git-auto-commit: allow$' "$agent_builder"
grep -q '^    "git commit --only \*": allow$' "$agent_builder"
grep -q '^  - id: issue-worktree$' "$agent_builder"
grep -q '^  - id: commit-baseline$' "$agent_builder"
grep -q '^  - id: commit$' "$agent_builder"

grep -q 'under `/code/specification/`' "$root/agents/reverse-engineer-app-spec.md"
grep -q '/project/.opencode/scripts/retrieve-knowledge.py' "$root/skills/okf-reader/SKILL.md"
if grep -R -q '/code/scripts/retrieve-knowledge.py' "$root/agents" "$root/skills"; then
  printf '%s\n' 'retrieval workflow still uses the application code mount' >&2
  exit 1
fi
