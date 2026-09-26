# OpenCode configuration

## Asset tree model

`/code` is the source of truth for this OpenCode configuration bundle.

| Path | Role |
| --- | --- |
| `/code` | Canonical, editable asset tree for agents, skills, scripts, plugins, docs, and tests. |
| `/project/.opencode` | Active runtime tree that OpenCode reads. It mirrors `/code` through shared links. |

Edit assets in `/code` first. The mirrored `.opencode/` tree should reflect those files through links, so runtime behavior stays aligned with the canonical copy. After changing agents, skills, plugins, commands, or config-time files, restart OpenCode so the running process reloads the mirrored configuration.

## Agents

| Agent | Purpose |
| --- | --- |
| api-integration-tester | Builds API integration tests. |
| app-spec-architect | Defines cross-feature architecture and shared workflows from requirements. |
| bug-fixer | Reproduces, diagnoses, and fixes defects with regression coverage. |
| code-implementor | Implements approved, focused code changes. |
| code-spec-engineer | Produces bounded implementation-ready feature contracts. |
| prd-strategist | Creates and refines OKF requirements. |
| reverse-engineer-app-spec | Recovers an evidence-backed specification from code. |
| spec-gap-detector | Finds implemented capabilities missing authoritative documentation and queues evidence-backed owner handoffs. |
| todo-planner | Researches work, coordinates authoritative document updates, and captures detailed executable or blocked todos. |
| url-to-vault | Ingests URLs into an OKF or Obsidian vault. |

## Skills

| Skill | Purpose |
| --- | --- |
| api-auth-testing | Tests API authentication and authorization. |
| api-discovery | Discovers API contracts and implementation. |
| api-integration-modeling | Models HTTP APIs and integrations. |
| api-integration-testing | Implements API integration tests. |
| api-test-reporting | Reports API test coverage and findings. |
| application-specification | Defines specification conventions. |
| backend-scaffolding | Scaffolds reachable backend layers. |
| browser-visual-capture | Captures baseline/post-change Chromium screenshots for URL-based UI validation. |
| code-comments | Adds code comments. |
| codebase-reverse-engineering | Recovers behavior and architecture from code. |
| data-persistence-modeling | Models data persistence and PostgreSQL schemas. |
| evidence-traceability | Adds evidence and traceability to specifications. |
| frontmatter-fixer | Repairs Markdown frontmatter. |
| frontend-reference-examples | Progressively loads matching HTML, CSS, JavaScript, accessibility, and illustrative data references for frontend components. |
| htmx | Implements server-fragment requests and safe swap ownership. |
| gap-risk-analysis | Identifies gaps, risks, and assumptions. |
| git-auto-commit | Creates an explicit-request commit for validated agent-owned changes. |
| go-code-standards | Applies focused Go standards. |
| graphify | Efficiently queries and updates an existing code knowledge graph. |
| grillme | Clarifies open design questions. |
| implement-stubs | Safely implements unfinished functions. |
| okf-formatter | Formats content as OKF. |
| okf-reader | Reads OKF knowledge bundles. |
| okf-reorganizer | Reorganizes an OKF bundle. |
| postgres-migration | Creates forward-only PostgreSQL migrations. |
| postgres-schema-designer | Designs PostgreSQL schema specification documents. |
| project-validation | Discovers and runs focused project-native validation. |
| product-modeling | Models product objectives and workflows. |
| requirements-analysis | Analyzes product requirements. |
| safe-code-change | Performs focused, collaborative-safe code changes. |
| security-operations | Reviews security and operational behavior. |
| tailwind | Configures standalone Tailwind CLI builds and static output. |
| spec-driven-implementation | Implements authoritative specifications. |
| specification-quality-gate | Reviews specification readiness. |
| specification-gap-handoff | Classifies code-to-authority documentation gaps and defines durable owner handoffs. |
| specification-reconciliation | Compares code-derived and authoritative specifications. |
| vault-ingestion | Ingests web content into a vault. |
| workflow-state-modeling | Models workflow states and transitions. |

## Graphify

Code-oriented agents may load `graphify` only when `graphify-out/graph.json` exists. The skill selects focused graph queries before broad reports or raw source search, and updates the graph after relevant code changes.

## Repository validation

Audit README catalog entries and architecture-test asset references from any checkout location:

```sh
python3 scripts/audit-asset-references.py
```

## Workflow ownership

- Requirements route to `prd-strategist`, shared architecture and cross-feature decisions to `app-spec-architect`, bounded feature contracts to `code-spec-engineer`, defects to `bug-fixer`, and other implementation to `code-implementor`.
- `spec-gap-detector` compares implemented capabilities with requirements and approved specifications, writes only `/code/specification-gaps.md`, and queues one-owner documentation handoffs. Documentation owners report their changes; the detector alone verifies and closes gaps.
- Todo skills share `todo-entry-contract`; implementation-ready entries require a single `Handoff:`, while blocked entries have no branch, dependency, or handoff metadata.
- Code-writing agents load `safe-code-change` before edits and `project-validation` before validation. Unsupported project-native validation commands require confirmation instead of being silently unavailable.
- Browser-capture commands and comparison behavior live in `browser-visual-capture`; agents only decide when the skill applies.
- Frontend component examples live behind `frontend-reference-examples`: agents read its catalog, then only a matching component document. References never override approved requirements, specifications, or repository conventions.

## Container note

`/code/containers/golang/Dockerfile` pre-installs Playwright's bundled `ffmpeg` into `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` so container runs do not need to fetch it at runtime.

## Container runner

`run` sources its sibling `project-mounts.sh`; the selected project is the single source of truth for host documentation/code mounts and container image.

| Item | Behavior |
| --- | --- |
| Project environment | A project may set newline-delimited `CONTAINER_ENV` entries in `project-mounts.sh`. Use `NAME` to inherit an exported host value (recommended for secrets) or `NAME=value` for a literal value; `run` forwards each entry with `docker run --env`. |
| Partner containers | A project may set `CONTAINER_NETWORK` and override `start_project_partners`. Call `ensure_container <name> <image> [docker options...]` there to create a missing named partner, start an existing stopped partner, or restart an existing running partner. `run` creates the network when needed and attaches its primary container. |

## Read-only knowledge retrieval

Search Markdown sections without returning full documents or modifying the bundle:

```sh
python3 scripts/retrieve-knowledge.py --root /path/to/bundle [--max-sections 10] [--json] <query...>
```

Results contain relative paths, line ranges, heading context, deterministic scores, and bounded excerpts. Navigation indexes influence ranking but are not returned; `log.md` and `.reorganization/` content are excluded.
