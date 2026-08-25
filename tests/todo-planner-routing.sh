#!/bin/sh
set -eu

planner=/code/agents/todo-planner.md

grep -q '^  question: allow$' "$planner"
grep -q '^    "/code/todo.md": allow$' "$planner"
grep -q 'Classify the request before choosing a delegated Task agent' "$planner"
grep -q 'must delegate to `prd-strategist` before capturing' "$planner"
grep -q 'must delegate to `code-spec-engineer` before capturing' "$planner"
grep -q 'Clarification delegations are read-only investigations' "$planner"

if grep -q 'never implement todo work or auto-run downstream documentation/implementation agents' "$planner"; then
  printf '%s\n' 'planner still prohibits required clarification delegation' >&2
  exit 1
fi

if grep -q 'update them through `prd-strategist`.*no edits' "$planner"; then
  printf '%s\n' 'planner still combines document updates with no-edit delegation' >&2
  exit 1
fi

if grep -q '^    "\*": deny$' "$planner"; then
  printf '%s\n' 'planner blanket edit denial prevents todo revisions' >&2
  exit 1
fi
