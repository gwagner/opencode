---
name: okf-reader
description: Read and answer questions from OKF knowledge bundles using indexes, concept frontmatter, markdown links, and citations.
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

Use `okf-formatter` when writing or materially revising an OKF bundle.
