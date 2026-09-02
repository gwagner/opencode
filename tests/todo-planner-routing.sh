#!/bin/sh
# shellcheck disable=SC2016 # Backticks are literal Markdown assertions.
set -eu

planner=/code/agents/todo-planner.md
resolver=/code/skills/blocked-todo-resolution/SKILL.md
capture=/code/skills/todo-capture/SKILL.md
upkeep=/code/skills/todo-upkeep/SKILL.md
contract=/code/skills/todo-entry-contract/SKILL.md

grep -q '^  question: allow$' "$planner"
grep -q '^    "/code/todo.md": allow$' "$planner"
grep -q '^    "/code/blocked-todos.md": allow$' "$planner"
grep -q '^    blocked-todo-resolution: allow$' "$planner"
grep -q 'Classify the request before choosing delegated Task agents' "$planner"
grep -q 'delegate to `prd-strategist`' "$planner"
grep -q 'delegate to `app-spec-architect`' "$planner"
grep -q 'delegate to `code-spec-engineer`' "$planner"
grep -q 'Before writing an implementation-ready todo, ensure every needed authoritative update has been completed' "$planner"
grep -q 'record that update in `Required to unblock:`' "$planner"
grep -q 'capture the work in `/code/blocked-todos.md`' "$planner"
grep -q 'Load `todo-entry-contract` before writing or promoting entries' "$planner"
grep -q 'Every implementation-ready todo requires one routing `Handoff:`' "$planner"
grep -q 'Every blocked entry must use `Blocked by:`' "$planner"
grep -q 'Use optional `Depends on:` exactly once only when' "$contract"

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
grep -q 'delegate to `app-spec-architect`' "$resolver"
grep -q 'delegate to `code-spec-engineer`' "$resolver"
grep -q 'Remove the promoted entry from `/code/blocked-todos.md` only after' "$resolver"
grep -q 'Apply `todo-entry-contract` to every changed or promoted entry' "$resolver"
grep -q 'Do not require a code checkout, restore code, inspect code' "$resolver"
grep -q 'the blocked entry is the sole prerequisite input' "$resolver"

if grep -q 'Read relevant requirements, specifications, and code evidence' "$resolver"; then
  printf '%s\n' 'blocked todo resolution still requires repository research' >&2
  exit 1
fi

test -f "$contract"
grep -q '^name: todo-entry-contract$' "$contract"
grep -q 'Require exactly one nonempty value for each label' "$contract"
grep -q '`Handoff:` — exactly `bug-fixer`' "$contract"
grep -q 'Blocked entries never use `Branch:`, `Depends on:`, or `Handoff:`' "$contract"
grep -q 'Load and apply `todo-entry-contract`' "$capture"
grep -q 'Load and apply `todo-entry-contract`' "$upkeep"
grep -q 'load `todo-entry-contract`' "$resolver"

if grep -q 'with at least one delegation' "$planner"; then
  printf '%s\n' 'planner still requires unnecessary delegation' >&2
  exit 1
fi
