---
name: agent-skill-authoring-contract
description: Applies shared preservation, authority, boundary, and self-review rules to one OpenCode agent or skill definition.
classification: technical
opencode_permission:
  read: allow
inputs:
  - one caller-permitted target agent or skill Markdown path
  - approved change scope
  - applicable authoritative sources and their precedence
  - authoring phase
---

# Agent and skill authoring contract

## Purpose

Apply one shared behavioral-authoring contract to one target definition during the specified authoring phase.

## Inputs

Require one caller-permitted target agent or skill Markdown path, approved change scope, applicable authoritative sources and their precedence, and an authoring phase of `pre-change` or `final-review`.

## Boundaries

MUST read the complete target definition. MUST report missing inputs, conflicting authority, invalid paths, or unsupported operations. MUST NOT modify files, invent requirements, resolve ungoverned authority conflicts, or expand the approved scope.

## Authoring invariants

- MUST preserve existing intent, behavior, constraints, established terminology, and file or tool contracts unless the approved scope explicitly changes them.
- MUST make the smallest coherent change. MUST NOT rewrite, reorganize, rename, remove, weaken, broaden, reinterpret, or refactor unrelated content.
- MUST NOT invent business rules, product behavior, requirements, acceptance criteria, architecture constraints, paths, schemas, APIs, tool capabilities, permissions, or dependencies.
- MUST use explicit, concise, actionable, scoped, and testable instructions. MUST use `MUST`, `MUST NOT`, `SHOULD`, `SHOULD NOT`, and `MAY` only with their defined normative meanings.
- MUST define operational boundaries and decision authority when they are material to the target. MUST identify what may be read, created, modified, deleted, and what must not change.
- MUST state source precedence when multiple authorities govern the target. When no stated precedence resolves a conflict, MUST report it.
- MUST identify rules that always remain true as invariants. Changes to an invariant require explicit authorization.
- MUST use observable workflow actions, explicit failure behavior, proportional validation, and completion criteria when applicable.
- MUST NOT let examples create behavior absent from normative rules. Normative rules control conflicts with examples.
- MUST consolidate identical duplicate rules only when meaning remains unchanged. MUST remove obsolete instructions replaced by the approved change.

## Procedure

1. Read the complete target and identify the exact approved behavior change and affected rules.
2. Compare the target with applicable authorities in declared precedence order.
3. Identify the smallest compliant change and report any missing authority or conflict.
4. During `final-review`, check the complete resulting definition for contradictions, duplicate or obsolete rules, undefined terms, ambiguous verbs, missing boundaries or precedence, scope expansion, broken references, invented requirements, invalid examples, and unverifiable rules.
5. Report preserved behavior, changed behavior, unresolved blockers, and final-review findings.
