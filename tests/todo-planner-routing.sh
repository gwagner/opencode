#!/bin/sh
set -eu

planner=/code/agents/todo-planner.md
resolver=/code/skills/blocked-todo-resolution/SKILL.md
capture=/code/skills/todo-capture/SKILL.md
upkeep=/code/skills/todo-upkeep/SKILL.md

grep -q '^  question: allow$' "$planner"
grep -q '^    "/code/todo.md": allow$' "$planner"
grep -q '^    "/code/blocked-todos.md": allow$' "$planner"
grep -q '^    blocked-todo-resolution: allow$' "$planner"
grep -q 'Classify the request before choosing a delegated Task agent' "$planner"
grep -q 'delegate to `prd-strategist`' "$planner"
grep -q 'delegate to `code-spec-engineer`' "$planner"
grep -q 'ensure every needed authoritative requirements or specification update has been completed' "$planner"
grep -q 'capture the work in `/code/blocked-todos.md`' "$planner"
grep -q '`Branch:`, `Scope:`, `Why:`, `Actions:`, `Evidence:`, and `Acceptance:`' "$planner"
grep -q 'Blocked entries do not receive `Branch:` until promotion' "$planner"
grep -q 'Every blocked entry must use `Blocked by:`' "$planner"

if grep -q 'never implement todo work or auto-run downstream documentation/implementation agents' "$planner"; then
  printf '%s\n' 'planner still prohibits required clarification delegation' >&2
  exit 1
fi

if grep -q 'Clarification delegations are read-only investigations' "$planner"; then
  printf '%s\n' 'planner still prevents authoritative document updates' >&2
  exit 1
fi

if grep -q '^    "\*": deny$' "$planner"; then
  printf '%s\n' 'planner blanket edit denial prevents todo revisions' >&2
  exit 1
fi

test -f "$resolver"
grep -q '^name: blocked-todo-resolution$' "$resolver"
grep -q 'Load `grillme` and run a focused clarification session' "$resolver"
grep -q 'delegate to `prd-strategist`' "$resolver"
grep -q 'delegate to `code-spec-engineer`' "$resolver"
grep -q 'Remove the promoted entry from `/code/blocked-todos.md` only after' "$resolver"
grep -q 'Blocked entries use `Blocked by:` and `Required to unblock:` instead' "$resolver"

grep -q 'exactly one nonempty `Branch:`' "$capture"
grep -q 'exactly one nonempty `Branch:`' "$upkeep"
grep -q 'exactly one nonempty `Branch:`' "$resolver"
grep -q '`Required to unblock:`' "$capture"
grep -q '`Required to unblock:`' "$upkeep"
