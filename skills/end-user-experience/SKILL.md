---
name: end-user-experience
description: Keeps planning, design, implementation, and testing focused on successful, clear, recoverable end-user outcomes.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: end-user-experience
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: end-user-experience
    - agent: prd-strategist
      source: /code/agents/prd-strategist.md
      allowed_skill: end-user-experience
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: end-user-experience
    - agent: todo-planner
      source: /code/agents/todo-planner.md
      allowed_skill: end-user-experience
inputs:
  - affected actor
  - task
  - authority or observed evidence
---

# End-user experience

Apply this lens without overriding authoritative requirements or inventing scope.

1. Identify the affected actor, task, and intended result.
2. Prefer choices that reduce avoidable effort, make status and next actions clear, and let users recover from expected errors; assess accessibility when an interactive surface is affected.
3. State the relevant user-observable success, failure, and recovery outcomes as acceptance criteria or test expectations.
4. Label a material UX decision as an assumption or open question when the authority does not decide it.

For reverse engineering, report observed user friction as evidence-backed improvement opportunities; do not present recommendations as observed behavior.
