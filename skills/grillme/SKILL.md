---
name: grillme
description: Asks concise, sequential clarifying questions only when ambiguity blocks a safe design or change.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: frontend-reference-builder
      source: /code/agents/frontend-reference-builder.md
      allowed_skill: grillme
    - agent: opencode-optimizer
      source: /code/agents/opencode-optimizer.md
      allowed_skill: grillme
    - agent: sdlc-orchestrator
      source: /code/agents/sdlc-orchestrator.md
      allowed_skill: grillme
    - agent: todo-planner
      source: /code/agents/todo-planner.md
      allowed_skill: grillme
inputs:
  - one execution-blocking ambiguity
  - established context
---

Ask one concise question at a time only for ambiguity that blocks a safe design or change. Record or label non-blocking uncertainty rather than delaying work indefinitely.
