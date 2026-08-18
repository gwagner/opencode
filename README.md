# OpenCode configuration

`/code` is the canonical asset tree; the active `.opencode/` tree mirrors it through shared links.

## Agents

| Agent | Purpose |
| --- | --- |
| api-integration-tester | Builds API integration tests. |
| app-spec-architect | Defines cross-feature architecture and shared workflows from requirements. |
| backend-scaffolder | Scaffolds specified backend features. |
| bug-fixer | Reproduces, diagnoses, and fixes defects with regression coverage. |
| code-implementor | Implements approved, focused code changes. |
| code-spec-engineer | Produces bounded implementation-ready feature contracts. |
| frontend-scaffolder | Scaffolds TypeScript, Lit, HTMX, and Tailwind frontend code. |
| opencode-optimizer | Audits OpenCode agents and skills. |
| prd-strategist | Creates and refines OKF requirements. |
| reconcile-spec-to-code | Reconciles specifications with implementation. |
| reverse-engineer-app-spec | Recovers an evidence-backed specification from code. |
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
| code-comments | Adds code comments. |
| codebase-reverse-engineering | Recovers behavior and architecture from code. |
| data-persistence-modeling | Models data persistence and PostgreSQL schemas. |
| evidence-traceability | Adds evidence and traceability to specifications. |
| frontmatter-fixer | Repairs Markdown frontmatter. |
| htmx | Implements server-fragment requests and safe swap ownership. |
| gap-risk-analysis | Identifies gaps, risks, and assumptions. |
| git-auto-commit | Creates an explicit-request commit for validated agent-owned changes. |
| go-code-standards | Applies focused Go standards. |
| graphify | Efficiently queries and updates an existing code knowledge graph. |
| grillme | Clarifies open design questions. |
| implement-stubs | Safely implements unfinished functions. |
| lit-components | Implements accessible Lit interaction components. |
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
| todo-capture | Captures deferred non-loop coding todos and unfixed bugs in `/code/todo.md`. |
| todo-upkeep | Appends loop-discovered follow-up tasks to `/code/todo.md` for later iterations. |
| spec-driven-implementation | Implements authoritative specifications. |
| specification-quality-gate | Reviews specification readiness. |
| specification-reconciliation | Compares code-derived and authoritative specifications. |
| vault-ingestion | Ingests web content into a vault. |
| workflow-state-modeling | Models workflow states and transitions. |

## Graphify

Code-oriented agents may load `graphify` only when `graphify-out/graph.json` exists. The skill selects focused graph queries before broad reports or raw source search, and updates the graph after relevant code changes.

## Loop runner

`./loop <project> <agent> [git-repo]` checks for `todo.md` at the target Git repository root, reads unchecked markdown tasks (`- [ ] task`), runs OpenCode on the next task until it returns `<task>DONE</task>`, marks that task complete, then continues. The default repo is `/code`. Use `./loop --test <project> <agent> [git-repo]` to print detected tasks, commands, prompts, and a summary without running OpenCode or editing the todo file. Todo-loop prompts instruct agents to use `todo-upkeep` when they discover required follow-up tasks for `/code/todo.md`.

Before running tasks, `./loop` checks the target Git repository for tracked uncommitted Git changes. If found, it prompts to open an OpenCode `code-implementor` session for the selected project to choose a commit message and commit only tracked changes. Untracked files alone do not trigger this prompt.

## Frontend build model

Frontend source is under `/code/src/frontend/`. TypeScript compiles without a bundler; the Tailwind standalone CLI generates CSS scanned from TypeScript and server templates. The backend serves compiled JavaScript and CSS as static assets. Lit owns presentation-only interaction islands; HTMX owns forms, requests, server fragments, and swaps outside Lit-owned DOM.

## Specification gaps

`/code/specification-gaps.md` is append-only. `code-spec-engineer` owns entries and status updates; forward-design agents resolve authoritative gaps in their permitted specification scope, while reverse and reconciliation agents classify and route gaps. Requirements override conflicting specifications.
