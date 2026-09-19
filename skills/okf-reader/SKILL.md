---
name: okf-reader
description: Read and answer questions from OKF knowledge bundles using indexes, concept frontmatter, markdown links, and citations.
opencode_permission:
  authoritative: agent permissions are authoritative; this grants none.
  direct_agent_callers:
    - agent: app-spec-architect
      source: /code/agents/app-spec-architect.md
      allowed_skill: okf-reader
    - agent: bug-fixer
      source: /code/agents/bug-fixer.md
      allowed_skill: okf-reader
    - agent: code-implementor
      source: /code/agents/code-implementor.md
      allowed_skill: okf-reader
    - agent: code-spec-engineer
      source: /code/agents/code-spec-engineer.md
      allowed_skill: okf-reader
    - agent: prd-strategist
      source: /code/agents/prd-strategist.md
      allowed_skill: okf-reader
    - agent: spec-gap-detector
      source: /code/agents/spec-gap-detector.md
      allowed_skill: okf-reader
    - agent: todo-planner
      source: /code/agents/todo-planner.md
      allowed_skill: okf-reader
inputs:
  - question
  - accessible OKF bundle root
---

# OKF reader

Use for questions answered from an OKF Markdown bundle. Read the smallest relevant subset.

## Core workflow

1. Identify the bundle root and read its `index.md` when present.
2. For a narrow lookup in a large bundle, when available, run `python3 /project/.opencode/scripts/retrieve-knowledge.py --root <bundle-root> --max-sections <bounded-limit> <query...>`. It returns ranked section locators, not document bodies.
3. Use indexes and returned paths, headings, and line ranges for progressive disclosure. Read the selected section and necessary heading ancestry only.
4. Use filenames, paths, titles, descriptions, types, tags, and resources to identify candidates when retrieval is unavailable or insufficient.
5. Follow Markdown links only when likely to clarify the answer. Use `log.md` only for history, freshness, or evolution questions.
6. Cite or name the concept paths used; distinguish stated information from inference.

Load [`reference.md`](reference.md) only for format or frontmatter questions, relationship/schema/example/history lookup playbooks, or bundle-wide navigation.

Writing or materially revising a bundle is a separate, caller-owned procedure outside this reading workflow.
