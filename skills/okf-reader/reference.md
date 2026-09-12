# OKF reader reference

Load this reference only for detailed format questions or the named lookup playbooks.

## Format and metadata

An OKF bundle is a UTF-8 Markdown directory tree. `index.md` is an optional directory listing and `log.md` is optional chronological history; neither is a concept document. Every other Markdown file is a concept document with delimited YAML frontmatter and a nonempty `type`.

Recommended concept fields are `title`, `description`, `resource`, `tags`, and ISO-8601 `timestamp`. Preserve unknown frontmatter keys when editing. The bundle-root `index.md` alone may declare `okf_version: "0.1"`. Broken links, missing optional fields, unknown types, and missing indexes do not make a bundle invalid.

Prefer stable bundle-relative links beginning with `/`; relative Markdown links are also supported. Links are directed and untyped: infer their meaning from surrounding prose.

## Lookup playbooks

- **Relationship:** read the source concept, then follow relevant links and explain their surrounding context.
- **Schema:** prefer `# Schema`, then tables, lists, and fenced code blocks.
- **Examples or usage:** prefer `# Examples`, then fenced code blocks and nearby prose.
- **Provenance:** prefer `# Citations`, then `resource` frontmatter.
- **Freshness/history:** inspect `timestamp` and relevant `log.md`; prefer newer entries when comparing changes.
- **Bundle overview:** start at the root index, then child indexes; summarize by directory, concept type, or tag.

For validation questions, use the canonical rules in `okf-formatter`; this reader reports observed bundle state and adds no independent validity rules.
