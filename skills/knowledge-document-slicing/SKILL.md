---
name: knowledge-document-slicing
description: Produces a bounded OKF concept and index plan before writing or revising knowledge documents.
classification: non-technical
opencode_permission:
  read: allow
inputs:
  - bounded writing scope
  - existing relevant indexes and concepts
  - permitted OKF destination
  - 800-word default concept body limit
---

# Knowledge document slicing

## Inputs

Require a bounded writing scope, relevant existing indexes and concepts, a permitted OKF destination, and the 800-word default concept body limit. Do not begin drafting until every input is available or its absence is explicitly reported as a blocker.

## Procedure

1. Identify one independently retrievable concept per proposed file. Split when content has independent reuse, resource, owner, lifecycle, actor, workflow, interface, or decision.
2. Plan each non-index concept body for no more than 800 words. Split an over-limit concept by its strongest independent boundary; do not compress unrelated content into one file.
3. Permit an over-limit concept only when an indivisible external contract or generated artifact cannot be split without changing meaning. Record the reason and add a concise index description that identifies the relevant sections.
4. Create or update one `index.md` for each directory containing multiple concepts or subdirectories. Each index groups children and gives each link a one-sentence retrieval description.
5. Link every new or split concept from its parent index and link only directly relevant sibling concepts from the body.
6. Return the planned paths, purpose, parent index, expected body size, and any permitted exception. The caller owns drafting and index updates.

## Completion

Report `passed` only when each planned concept is independently retrievable, each non-exception body is planned at 800 words or fewer, and every planned file has an index route. Otherwise report `blocked` with the missing boundary or destination.
