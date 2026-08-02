---
name: frontmatter-fixer
description: Validates and repairs YAML frontmatter, including required OKF concept fields when applicable.
---

# Frontmatter validation

Use when creating or repairing Markdown frontmatter.

1. Confirm opening and closing `---` delimiters and parseable YAML.
2. Preserve unknown keys and existing field types unless correcting invalid YAML.
3. Quote values when YAML syntax requires it; do not use forbidden multiline indicators when repository policy forbids them.
4. Keep descriptions single-line, complete, informative, and front-loaded.
5. For an OKF concept, require a non-empty `type`; do not require `type` for agent, skill, config, index, or log files.
6. Report repaired fields and any unresolved invalid value.

