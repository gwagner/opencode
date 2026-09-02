---
name: okf-formatter
description: Formats new or updated knowledge as focused, linked Open Knowledge Format Markdown concepts and indexes.
---

# OKF formatter

Use when writing or materially revising an Open Knowledge Format bundle.

## Canonical format

An OKF bundle is a UTF-8 Markdown directory tree. `index.md` provides progressive disclosure and `log.md` records optional date-grouped history; neither is a concept document. Every other Markdown file is one concept and must contain parseable YAML frontmatter with a nonempty `type`.

Optional concept fields are `title`, `description`, `resource`, `tags`, and an ISO-8601 `timestamp`. Preserve unknown fields. Use standard Markdown links; prefer stable bundle-relative links. Broken links, missing optional fields, unknown types, and missing indexes do not make a bundle invalid.

The bundle-root `index.md` alone may use frontmatter to declare `okf_version: "0.1"`. Other indexes contain grouped links and concise descriptions. When present, `log.md` uses newest-first `YYYY-MM-DD` headings.

## Writing workflow

1. Identify the bundle root and read relevant indexes before opening many concepts.
2. Write one coherent topic per concept. Split content with independent type, resource, ownership, lifecycle, or reuse.
3. Preserve source meaning, provenance, citations, useful examples, unknown metadata, and existing links.
4. Add links between related concepts and update every affected index.
5. Use structured headings, lists, tables, and fenced code where they improve retrieval.
6. Use `# Citations` for sources supporting material claims.
7. Load `frontmatter-fixer` to validate changed concept frontmatter.
8. Use `okf-reorganizer` only for purposeful structural changes and `okf-reader` for retrieval.

## Validation

Confirm each changed concept has delimited, parseable YAML and a nonempty `type`; affected indexes resolve to the intended concepts; unknown fields remain intact; and structural changes preserve useful links and provenance. Report changed paths and unresolved link or source limitations.
