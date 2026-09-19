---
name: gap-risk-analysis
description: Identifies contradictions, missing behavior, incomplete scaffolding, implementation divergence, assumptions, risks, and unresolved product questions.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: gap-risk-analysis
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: gap-risk-analysis
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: gap-risk-analysis
    - agent: spec-gap-detector
      source: /code/agents/spec-gap-detector.md
      allowed_skill: gap-risk-analysis
inputs:
  - bounded scope
  - authoritative and observed evidence
compatibility: opencode
metadata:
  domain: specification-analysis
---

# Gap, risk, and ambiguity analysis

## Categories

Identify:

- Missing but necessary behavior
- Partially implemented capability
- Declared but unwired capability
- Requirement not implemented
- Implementation not described by requirements
- Conflicting sources
- Orphaned tables or models
- Unreachable routes
- Unused state values
- Mock-only integrations
- Missing authorization
- Missing validation
- Missing recovery behavior
- UI without backend support
- Backend without user-facing surface
- Operational gaps
- Security and privacy gaps

## Gap table

| Capability | Status | Existing evidence | Missing elements | Product impact | Recommended clarification |
|---|---|---|---|---|---|

## Assumptions

Use the narrowest assumption that allows progress.

For each assumption include:

- Assumption
- Why it is necessary
- Supporting evidence
- Consequence if wrong
- Confidence

## Open questions

| ID | Question | Why it matters | Ambiguity source | Current assumption | Blocking |
|---|---|---|---|---|---|

Ask the user only when a question is materially blocking and cannot be isolated. Otherwise document it and continue.

## Recommendations

Recommendations must be visibly separate from current requirements or implementation.

Do not turn gap analysis into an unsolicited redesign.
