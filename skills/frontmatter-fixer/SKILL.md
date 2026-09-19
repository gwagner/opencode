---
name: frontmatter-fixer
description: Validates and repairs YAML frontmatter, including required OKF concept fields when applicable.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: frontmatter-fixer
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: frontmatter-fixer
    - agent: prd-strategist
      source: /code/agents/prd-strategist.md
      allowed_skill: frontmatter-fixer
    - agent: reverse-engineer-app-spec
      source: /code/agents/reverse-engineer-app-spec.md
      allowed_skill: frontmatter-fixer
inputs:
  - Markdown paths
  - applicable frontmatter contract
---

# Frontmatter validation

Use when creating or repairing Markdown frontmatter.

1. Confirm opening and closing `---` delimiters and parseable YAML.
2. Preserve unknown keys and existing field types unless correcting invalid YAML.
3. Quote values when YAML syntax requires it; do not use forbidden multiline indicators when repository policy forbids them.
4. Keep descriptions single-line, complete, informative, and front-loaded.
5. For an OKF concept, require a non-empty `type`; do not require `type` for agent, skill, config, index, or log files.
6. Report repaired fields and any unresolved invalid value.
