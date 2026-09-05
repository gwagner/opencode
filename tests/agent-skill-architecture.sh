#!/bin/sh
# shellcheck disable=SC2016 # Backticks are literal Markdown assertions.
set -eu

for file in /code/agents/*.md; do
  expected=$(basename "$file" .md)
  grep -q "^name: $expected$" "$file"
done

for file in /code/skills/*/SKILL.md; do
  expected=$(basename "$(dirname "$file")")
  grep -q "^name: $expected$" "$file"
done

for agent in backend-scaffolder api-integration-tester; do
  file="/code/agents/$agent.md"
  grep -q '^    safe-code-change: allow$' "$file"
  grep -q 'Load `safe-code-change`' "$file"
done

for agent in api-integration-tester backend-scaffolder frontend-scaffolder bug-fixer code-implementor; do
  file="/code/agents/$agent.md"
  grep -q 'deterministic local mock service' "$file"
  grep -q 'provider-sandbox integration test does not replace this requirement' "$file"
done

for agent in code-implementor bug-fixer frontend-scaffolder; do
  file="/code/agents/$agent.md"
  grep -q '^    "node \*capture-screenshots\.mjs \*": allow$' "$file"
  grep -q '^    frontend-reference-examples: allow$' "$file"
  grep -q '`frontend-reference-examples` only when' "$file"
  if grep -q '/project/.opencode/skills/browser-visual-capture/scripts' "$file"; then
    printf '%s\n' "$agent duplicates the browser-capture executable path" >&2
    exit 1
  fi
done

reference_skill=/code/skills/frontend-reference-examples
grep -q '^name: frontend-reference-examples$' "$reference_skill/SKILL.md"
grep -q '\[Data table\](references/data-table.md)' "$reference_skill/index.md"
test -f "$reference_skill/references/data-table.md"
test ! -e "$reference_skill/monitor-check-history-table.md"
grep -q 'not an authoritative endpoint' "$reference_skill/references/data-table.md"
grep -q 'does not fetch' "$reference_skill/references/data-table.md"
grep -q '^## GoHTML template$' "$reference_skill/references/data-table.md"
grep -q '^type DataTableView struct {$' "$reference_skill/references/data-table.md"
grep -q 'data-table:activate' "$reference_skill/references/data-table.md"
grep -q 'data-table:page-activate' "$reference_skill/references/data-table.md"

grep -q 'node /code/skills/browser-visual-capture/scripts/capture-screenshots.mjs' /code/skills/browser-visual-capture/SKILL.md
if grep -q '/project/.opencode/skills/browser-visual-capture/scripts' /code/skills/browser-visual-capture/SKILL.md; then
  printf '%s\n' 'browser-capture skill still depends on the runtime mirror path' >&2
  exit 1
fi

grep -q 'only when approved requirements or an explicit architecture decision establishes it' /code/skills/frontend-component-modeling/SKILL.md
for agent in reverse-engineer-app-spec spec-gap-detector; do
  file="/code/agents/$agent.md"
  grep -q '^    "/project/context.md": allow$' "$file"
  grep -q '^    "/project/handoff.md": allow$' "$file"
done

detector=/code/agents/spec-gap-detector.md
handoff=/code/skills/specification-gap-handoff/SKILL.md
test ! -e /code/agents/reconcile-spec-to-code.md
grep -q '^  task: deny$' "$detector"
grep -q '^    "\*": deny$' "$detector"
grep -q '^    "/code/specification-gaps.md": allow$' "$detector"
grep -q 'Your only code-analysis artifact is `/code/specification-gaps.md`' "$detector"
grep -q 'Use durable report-and-queue handoffs; never delegate directly' "$detector"
grep -q '^name: specification-gap-handoff$' "$handoff"
grep -q '`implemented-without-authority`' "$handoff"
grep -q 'assign the earliest authoritative owner' "$handoff"
grep -q 'Report `implementation-divergence` separately and omit `internal-detail`' "$handoff"

for owner in prd-strategist app-spec-architect code-spec-engineer; do
  file="/code/agents/$owner.md"
  grep -q 'edit or close' "$file"
done

grep -q 'under `/code/specification/`' /code/agents/reverse-engineer-app-spec.md
grep -q '^  bash: deny$' /code/agents/app-spec-architect.md
