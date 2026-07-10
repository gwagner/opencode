---
name: okf-reogranizer
description: reorganize an OKF bundle
---

# What I Do


## Reorganizing as the OKF Bundle Grows

Use these rules when an OKF bundle becomes large, redundant, hard to navigate, or poorly grouped.

### Goals

Reorganization should improve:

* Discoverability through clearer directories and `index.md` files.
* Concept cohesion: one concept per file.
* Link quality between related concepts.
* Progressive disclosure: users and agents should understand a directory before opening every file.
* Long-term maintainability without losing history, context, or provenance.

Do not reorganize merely for aesthetic reasons. Prefer minimal, purposeful changes.

### Preserve Concept Meaning

When moving, splitting, merging, or renaming files:

* Preserve the original concept’s meaning.
* Preserve all useful frontmatter.
* Preserve unknown frontmatter keys.
* Preserve citations, links, examples, schema sections, and important prose.
* Preserve `resource` URIs unless the underlying asset has changed.
* Preserve or update `timestamp` according to the last meaningful content change.
* Do not discard context unless it is clearly duplicated or obsolete.

### Directory Organization

As the bundle grows, group concepts by the most useful browsing dimension for the expected user or agent.

Common grouping strategies:

* By asset type: `tables/`, `apis/`, `metrics/`, `playbooks/`, `dashboards/`.
* By domain: `sales/`, `finance/`, `support/`, `growth/`.
* By system: `bigquery/`, `stripe/`, `salesforce/`, `dataplex/`.
* By workflow: `onboarding/`, `incident-response/`, `data-quality/`.

Use one primary hierarchy. Represent cross-cutting categories with `tags`, not duplicate directory trees.

Avoid deeply nested paths unless each level adds useful meaning.

### Concept Boundaries

A concept document should represent one coherent unit of knowledge.

Split a file when:

* It covers multiple independently useful concepts.
* Different sections have different `type`, `resource`, ownership, or lifecycle.
* One section is frequently referenced on its own.
* The file is too large for efficient agent retrieval.

Merge files when:

* Separate files describe the same concept.
* One file is only a fragment with no independent meaning.
* Multiple files must always be read together to be useful.

When splitting, preserve links between the new concepts.

When merging, redirect or update links that pointed to the old files.

### Concept IDs and Paths

A concept ID is the file path relative to the bundle root without `.md`.

Renaming or moving a file changes its concept ID, so do this carefully.

Before changing paths:

1. Search for links to the old path.
2. Update all internal links.
3. Add a log entry explaining the move.
4. Preserve enough title, description, and tags for the concept to remain discoverable.

Prefer stable, descriptive paths.

Good examples:

* `tables/orders.md`
* `metrics/monthly-recurring-revenue.md`
* `playbooks/data-freshness-alert.md`

Avoid vague paths:

* `misc/info.md`
* `new/file1.md`
* `docs/data.md`

### Index Files

Add or update `index.md` when a directory contains multiple concepts or subdirectories.

Use indexes for progressive disclosure.

Each `index.md` should:

* Group related concepts under headings.
* Link to child concepts or subdirectories.
* Include short descriptions, preferably from concept frontmatter.
* Help a human or agent decide what to open next.

Do not put concept frontmatter in `index.md`, except that the bundle-root `index.md` may declare `okf_version`.

### Log Files

Use `log.md` to record meaningful structural changes.

Add log entries when:

* Files are moved or renamed.
* Concepts are split or merged.
* Major directories are introduced.
* Important concepts are deprecated.
* A resource binding changes.
* A large generated update changes many concepts.

Log entries should be newest first and grouped by `YYYY-MM-DD`.

Example:
```markdown
## 2026-07-06
* **Reorganization**: Moved order-related tables from `/tables/` to `/sales/tables/` and updated internal links.
* **Split**: Split `/metrics/revenue.md` into `/metrics/gross-revenue.md` and `/metrics/net-revenue.md`.
```

### Links During Reorganization

Internal links are relationships. Preserve them.

When moving content:

* Update absolute bundle-relative links beginning with `/`.
* Update relative links affected by the move.
* Keep relationship meaning in surrounding prose.
* Do not remove broken links unless you know they are obsolete.
* If a target does not exist yet, a broken link may represent planned knowledge and is allowed.

Prefer absolute bundle-relative links for stability.

Example:

```markdown
See [customers](/tables/customers.md).
```

### Tags During Reorganization

Use tags for cross-cutting categories that should not define the main directory structure.

Good tag uses:

* Business domain: `sales`, `finance`, `support`.
* Lifecycle: `deprecated`, `draft`, `production`.
* Workflow: `oncall`, `incident`, `data-quality`.
* System: `bigquery`, `stripe`, `salesforce`.

Do not create duplicate files just to support multiple browsing views. Generate tag views by scanning frontmatter.

### Duplicates and Conflicts

When duplicate concepts exist:

1. Compare `resource`, `title`, `description`, `type`, and body content.
2. Prefer the concept with the clearest resource binding, newest meaningful timestamp, strongest citations, and best links.
3. Merge useful content into the surviving concept.
4. Update inbound links to point to the surviving concept.
5. Record the merge in `log.md`.

When concepts conflict:

* Do not silently choose one unless the correct source is obvious.
* Preserve citations and timestamps.
* Mark uncertainty in the body.
* Prefer sourced claims over unsourced claims.
* Prefer newer content only when it represents a meaningful update, not merely a newer file modification time.

### Generated Reorganizations

When an agent reorganizes OKF content:

* Make the smallest set of changes needed.
* Preserve unknown fields.
* Preserve markdown structure where possible.
* Keep examples and citations close to the claims they support.
* Update affected indexes.
* Update affected links.
* Add or update log entries.
* Report what changed, including moved, split, merged, created, or deleted files.

### Validation After Reorganization

After reorganizing, check:

1. Every non-reserved `.md` file has parseable YAML frontmatter.
2. Every concept has a non-empty `type`.
3. Reserved filenames are only `index.md` or `log.md`.
4. `index.md` files follow index structure.
5. `log.md` files use date headings in `YYYY-MM-DD`.
6. Internal links affected by moves were updated.
7. No useful frontmatter, citations, examples, schema, or resource bindings were lost.

Do not reject the bundle for missing optional fields, unknown types, unknown frontmatter keys, broken links, or missing indexes.

### User-Facing Summary

After reorganizing, summarize the work in terms of user impact:

* What moved.
* What was split or merged.
* What indexes were added or updated.
* What links were updated.
* What uncertainty or unresolved cleanup remains.

Avoid low-level noise unless the user asks for a detailed diff.
