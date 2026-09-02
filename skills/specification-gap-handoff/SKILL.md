---
name: specification-gap-handoff
description: Classifies code-to-authority documentation gaps and creates durable, evidence-backed handoffs for the correct requirements or specification owner.
---

# Specification gap handoff

Use when implemented behavior may lack authoritative requirements or specifications. This skill records and routes documentation work; it never approves observed code behavior or changes production code.

## Classify each capability

- `specified-aligned`: authoritative requirements and specifications cover the material observed contract.
- `requirement-exists-spec-missing`: product intent exists, but delivery or feature contracts are absent or incomplete.
- `implemented-without-authority`: externally meaningful behavior exists without supporting requirements or approved specification.
- `specification-conflict`: requirements or approved specifications are contradictory or insufficient to determine intent.
- `implementation-divergence`: authority is clear but code differs; report outside the documentation handoff queue.
- `internal-detail`: implementation choice does not materially affect public behavior, data meaning, security, operations, or shared architecture and needs no authoritative specification.

Do not create gaps for every function, type, helper, or package. Create one gap per independently resolvable capability or contract.

## Select one owner

- `prd-strategist`: missing product intent, business rules, user-visible behavior, scope, or acceptance policy.
- `app-spec-architect`: missing shared architecture, cross-feature workflow, system boundary, or technology decision.
- `code-spec-engineer`: missing bounded feature, API, data, validation, error, permission, or security contract when product intent and architecture are sufficient.

If multiple layers are missing, assign the earliest authoritative owner and state downstream documentation dependencies in `Required follow-up:`. Never route undocumented behavior directly to implementation agents.

## Gap entry contract

Create or update a non-duplicate entry only for `requirement-exists-spec-missing`, `implemented-without-authority`, or `specification-conflict`. Report `implementation-divergence` separately and omit `internal-detail`. Every queued entry therefore requires one documentation owner.

Write queued entries in `/code/specification-gaps.md`:

```markdown
## GAP-<DOMAIN>-<NNN>: <concise capability>

- Status: open | delegated | blocked | resolved
- Classification: <classification>
- Owner: prd-strategist | app-spec-architect | code-spec-engineer
- Capability: <externally meaningful behavior or contract>
- Code evidence:
  - `<repository-relative path>#<symbol>` — <observed behavior>
- Existing authority:
  - `<requirement/spec path>#<section>` — <what is established>
- Missing:
  - <decision or contract element>
- Why authoritative: <why this belongs in requirements/specification rather than code comments>
- Constraints: Observed code is evidence, not product authority.
- Required follow-up: <downstream owner or none>
- Acceptance: <authoritative document and concrete coverage required>
- Resolution: <document links and verification, or pending>
```

Use stable IDs and path/symbol evidence. Preserve unresolved differences as questions or constraints; do not infer approval from tests, comments, names, or deployed behavior.

## Sending the handoff

Persist the entry and name its owner. The user or an orchestrating planner invokes that owner with only the bounded gap, relevant authority, code evidence, missing decisions, constraints, and acceptance criteria. The detector never delegates directly because task permissions cannot safely restrict delegation to documentation owners.

The documentation owner writes authoritative documents but does not close the gap. Re-read reported documents and set `Status: resolved` only when acceptance is met; otherwise keep the entry open or blocked and record the remaining requirement.
