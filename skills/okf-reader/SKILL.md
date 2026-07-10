---
name: okf-reader
description: Read and answer questions from OKF knowledge bundles using indexes, concept frontmatter, markdown links, and citations.
---

## Purpose

Use this skill when working with an OKF knowledge bundle: a directory tree of UTF-8 markdown files with YAML frontmatter representing concepts, metadata, context, and curated knowledge.

The goal is to answer user questions by reading the smallest relevant subset of the bundle.

## OKF Basics

An OKF bundle is a directory tree of markdown files.

Reserved filenames:

- `index.md`: optional directory listing for progressive disclosure.
- `log.md`: optional chronological update history.

Reserved files are not concept documents.

Every other `.md` file is a concept document.

A concept document has:

1. YAML frontmatter delimited by `---`.
2. A markdown body.

Required concept frontmatter:

- `type`: non-empty concept kind.

Recommended concept frontmatter:

- `title`: display name.
- `description`: one-line summary.
- `resource`: canonical URI for the underlying asset, if any.
- `tags`: YAML list of short categorization strings.
- `timestamp`: ISO 8601 last meaningful change time.

Unknown frontmatter keys are allowed and should be preserved if editing.

## Reading Strategy

When answering a question from an OKF bundle:

1. Identify the bundle root.
2. Read the root `index.md` if present.
3. Use `index.md` files for progressive disclosure before opening many concept files.
4. Use filenames, paths, titles, descriptions, types, tags, and resources to identify candidate concepts.
5. Read only the most relevant concept documents first.
6. Follow markdown links only when they are likely to clarify the answer.
7. Prefer absolute bundle-relative links beginning with `/`.
8. Support relative markdown links.
9. Treat links as directed, untyped relationships.
10. Infer relationship meaning from surrounding prose.
11. Tolerate broken links; they may represent incomplete knowledge.
12. Use `log.md` only when the user asks about history, freshness, recent changes, or evolution of the bundle.

## Answering Rules

When answering:

- Cite or name the concept paths used.
- Prefer the concept `title` when available, but include the path when useful.
- Mention `type`, `resource`, `tags`, or `timestamp` when relevant.
- Use `# Citations` sections in concept bodies as supporting sources when present.
- Distinguish between information stated in OKF content and inferences you make.
- Do not reject concepts because of unknown `type` values or extra frontmatter keys.
- Do not assume missing optional fields are errors.
- Do not read the whole bundle unless necessary.

## Traversal Heuristics

For lookup questions:

- Search `title`, `description`, `tags`, `resource`, and filename.
- Then read the matching concept body.

For relationship questions:

- Read the source concept.
- Follow relevant markdown links.
- Use surrounding prose to explain relationship semantics.

For schema questions:

- Prefer sections named `# Schema`.
- Also inspect tables, lists, and fenced code blocks.

For examples or usage questions:

- Prefer sections named `# Examples`.
- Also inspect fenced code blocks and nearby explanatory prose.

For provenance questions:

- Prefer sections named `# Citations`.
- Also inspect `resource` frontmatter.

For freshness or change-history questions:

- Check `timestamp` in frontmatter.
- Check relevant `log.md` files if present.
- Prefer newer entries when comparing changes.

For bundle overview questions:

- Start with root `index.md`.
- Then read child `index.md` files.
- Summarize by directory, concept type, or tag.

For validation questions:

A bundle conforms to OKF v0.1 if:

1. Every non-reserved `.md` file has parseable YAML frontmatter.
2. Every concept frontmatter block has a non-empty `type`.
3. Every `index.md` and `log.md`, when present, follows OKF structure.

Treat all other guidance as soft.

Do not fail validation for:

- Missing optional fields.
- Unknown `type` values.
- Unknown additional frontmatter keys.
- Broken cross-links.
- Missing `index.md`.

## Editing Rules

Use the okf-formatter skill
