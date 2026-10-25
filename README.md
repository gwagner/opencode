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
| agent-builder | Audits and creates deterministic technical or non-technical OpenCode agents and skills. |
| api-integration-tester | Builds API integration tests from specifications and application code, including authentication and authorization behavior. |
| app-spec-architect | Designs implementation-ready application specifications from product requirements. Use for architecture, workflows, data, APIs, UI, and delivery design. |
| bug-fixer | Diagnoses and fixes reported defects with focused code and regression tests. |
| code-implementor | Implements one approved, bounded code change in an existing feature worktree. |
| code-spec-engineer | Translates approved product requirements and application architecture into implementation-ready feature specifications. Use before production implementation when code-level contracts remain undefined. |
| frontend-reference-builder | Builds and maintains reusable frontend component references in the frontend-reference-examples catalog. |
| github-issue-manager | Researches and manages GitHub issues through creation, updates, comments, state changes, explicit deletion, and ready-execution routing to sdlc-orchestrator. |
| prd-strategist | Creates, refines, and reconciles product requirements as focused OKF documents. |
| reverse-engineer-app-spec | Reverse-engineers an existing codebase into an evidence-backed application specification. |
| sdlc-orchestrator | Orchestrates one CLI-, OpenChamber-, or GitHub-issue-originated change through an exact-head user decision on a validated pull request. |
| spec-gap-detector | Finds implemented capabilities lacking authoritative requirements or specifications and creates evidence-backed handoffs to the correct documentation owner. |
| url-to-vault | Ingests a web page into an Obsidian or OKF vault as a structured, durable, searchable note. |


## Skills

| Skill | Purpose |
| --- | --- |
| accessibility-testing | Implements focused accessibility checks for changed rendered frontend behavior. |
| agent-skill-authoring-contract | Applies shared preservation, authority, boundary, and self-review rules to one OpenCode agent or skill definition. |
| api-auth-testing | Designs and implements API authentication, authorization, ownership, and tenant-boundary test matrices. |
| api-contract-conformance-testing | Implements focused conformance tests for approved API request, response, error, and compatibility contracts. |
| api-discovery | Discovers intended API contracts, implemented routes, access control, mismatches, and reusable test infrastructure before API integration testing. |
| api-integration-modeling | Designs or recovers HTTP APIs, handlers, contracts, authentication, errors, external integrations, webhooks, retries, and idempotency. |
| api-integration-testing | Builds maintainable API integration tests using existing project infrastructure for contracts, access control, validation, CRUD flows, and isolation. |
| api-resilience-testing | Implements focused tests for approved API idempotency, retry, timeout, webhook, duplicate-delivery, and upstream-failure behavior. |
| api-test-reporting | Reports API integration-test coverage, execution, contract and access-control findings, blockers, and prioritized remaining work. |
| application-specification | Defines the common structure, rigor, terminology, and output rules for implementation-ready application specifications. |
| backend-integration-testing | Implements focused tests for changed backend use cases, persistence, adapters, jobs, and error mapping. |
| backend-scaffolding | Scaffolds reachable backend routes, services, data access, contracts, and useful placeholders from approved requirements and specifications. |
| backend-workflow-implementation | Implements one approved state-changing backend workflow with explicit atomicity, concurrency, idempotency, snapshot, and recovery behavior. |
| browser-visual-capture | Captures deterministic baseline and post-change Chromium screenshots for one URL or URL set as diagnostic artifacts. |
| browser-visual-compare | Compares caller-supplied deterministic baseline/post-change screenshot pairs as diagnostic evidence against structured visual expectations. |
| code-comments | Adds concise native-language documentation for public contracts and non-obvious invariants. |
| codebase-reverse-engineering | Reverse-engineers product behavior and architecture from source code, migrations, tests, configuration, interfaces, frontend code, and runtime wiring. |
| data-persistence-modeling | Designs or reconstructs application entities, PostgreSQL schemas, relationships, constraints, indexing, transactions, tenancy, and audit history. |
| deterministic-skill-tree-authoring | Designs concise, recursive skill and agent workflows with explicit ordering, choices, and completion gates. |
| end-user-experience | Keeps planning, design, implementation, and testing focused on successful, clear, recoverable end-user outcomes. |
| evidence-traceability | Adds stable source citations, confidence, status classification, and traceability matrices to application specifications. |
| feature-branch-setup | Creates one clean local policy-selected feature branch before a bounded SDLC change. |
| frontend-behavior-testing | Implements focused tests for approved frontend interaction, state, validation, error, and recovery behavior. |
| frontend-component-modeling | Designs or reconstructs frontend routes, screens, TypeScript components, Tailwind conventions, states, events, validation, accessibility, and backend dependencies. |
| frontend-impact-validation | Evaluates complete production-shaped browser-impact evidence using existing project runtime and browser-testing infrastructure. |
| frontend-reference-examples | Loads one selected frontend catalog entry as non-authoritative implementation guidance without adapting code. |
| frontend-reference-lookup | Selects a matching frontend reference catalog entry for a bounded component or route without adapting code. |
| frontend-scaffolding | Implements a bounded rendered frontend surface from an approved contract using the project's established templates, components, assets, and delivery path. |
| frontmatter-fixer | Validates and repairs YAML frontmatter, including required OKF concept fields when applicable. |
| gap-risk-analysis | Identifies contradictions, missing behavior, incomplete scaffolding, implementation divergence, assumptions, risks, and unresolved product questions. |
| git-change-baseline | Records a safe ownership baseline before task-owned editing begins. |
| git-delegated-change-commit | Reviews and commits one validated delegate-owned change batch from an established clean ownership baseline. |
| github-blocked-issue-resolution | Reconciles one GitHub work issue's blocked state and safely promotes it when every execution blocker is resolved. |
| github-issue-capture | Creates or deduplicates one contract-validated ready or policy-authorized blocked GitHub work issue in the current checkout's repository. |
| github-issue-close | Closes one existing GitHub issue and verifies its closed state. |
| github-issue-comment | Posts one verified progress or completion comment to an existing GitHub issue. |
| github-issue-deletion | Permanently deletes one GitHub issue only after explicit issue-specific confirmation. |
| github-issue-reopen | Reopens one closed GitHub issue and verifies its open state. |
| github-issue-update | Applies one requested reversible title, body, or label update to an existing GitHub issue. |
| github-pr-approved-merge | Verifies that a user manually squash-merged one exact approved GitHub pull request without performing the merge. |
| github-pr-check-validation | Deterministically classifies and boundedly rechecks required checks for one unchanged open pull request. |
| github-pr-lifecycle-recovery | Selects the resumable branch or pull-request state for one CLI- or OpenChamber-originated non-issue lifecycle without mutating it. |
| github-pr-publication | Idempotently publishes one validated committed head to a unique draft pull request for a supported SDLC entry point. |
| github-pr-ready | Marks one checked draft pull request ready, or verifies an already-ready pull request, for an exact-head user decision. |
| github-pr-rejection | Verifies that one exact user-rejected pull request remains open and unchanged without mutating GitHub. |
| github-pr-remote-branch-cleanup | Deletes one verified merged pull request's unchanged remote branch and confirms its absence. |
| github-sdlc-lifecycle-recovery | Selects the safe resumable state for an issue-originated pull-request lifecycle without mutating it. |
| github-work-issue-contract | Validates lifecycle-aware canonical GitHub work-issue contracts without publishing or changing authority. |
| go-code-standards | Use when adding or modifying Go to apply focused idiomatic Go code standards. |
| graphify | Investigates a codebase efficiently with graphify. Use when answering codebase questions, tracing code relationships, or updating an existing knowledge graph after code changes. |
| grillme | Asks concise, sequential clarifying questions only when ambiguity blocks a safe design or change. |
| htmx | Implements HTMX server-fragment requests, form actions, errors, loading states, and safe swap ownership. |
| implement-stubs | Find and safely implement unfinished functions in the current repository. |
| interface-boundaries | Designs deep, focused module interfaces and adapter seams. Use when changing public contracts, external dependencies, persistence access, or cross-layer calls. |
| issue-worktree-validation | Adds issue readiness and dependency gates to deterministic OpenChamber worktree validation. |
| knowledge-document-slicing | Produces a bounded OKF concept and index plan before writing or revising knowledge documents. |
| non-production-database-fixture | Verifies and executes one deterministic database-backed test through an existing project-native isolated fixture lifecycle. |
| non-technical-agent-skill-builder | Creates or revises one deterministic non-technical OpenCode agent or skill. |
| okf-formatter | Formats new or updated knowledge as focused, linked Open Knowledge Format Markdown concepts and indexes. |
| okf-reader | Read and answer questions from OKF knowledge bundles using indexes, concept frontmatter, markdown links, and citations. |
| okf-reorganizer | Reorganizes an OKF bundle while preserving concepts, links, metadata, and history. |
| openchamber-worktree-validation | Classifies and safely prepares one existing OpenChamber-linked worktree for fresh or resumed SDLC execution. |
| postgres-migration | Creates safe, forward-only PostgreSQL schema migrations in the caller-permitted project migration directory. Existing migration files are immutable; every later change or correction uses a new migration. |
| postgres-migration-integration-testing | Validates changed PostgreSQL migrations and schema-dependent behavior against an isolated project-native test target. |
| postgres-schema-designer | Designs PostgreSQL schema specification documents. Use with specification work involving entities, constraints, keys, indexes, relationships, or transaction rules. |
| product-modeling | Recovers or defines product objectives, actors, business terminology, use cases, permissions, and end-to-end workflows from requirements or code evidence. |
| project-validation | Discovers and runs the narrowest project-native formatting, build, lint, and test validation for a focused change. |
| release-readiness-validation | Validates changed delivery artifacts, runtime configuration, migration ordering, health checks, and observability wiring. |
| requirements-analysis | Analyzes raw product requirements into explicit requirements, implications, assumptions, constraints, ambiguities, and traceable specification inputs. |
| root-cause-analysis | Establishes the evidenced causal mechanism of one reported software defect before a corrective change is selected. |
| safe-code-change | Implements a focused code change safely in a collaborative repository. Use for bug fixes, stub completion, or small specification-driven implementation tasks. |
| security-operations | Reviews or specifies authentication, authorization, tenancy, privacy, audit, secrets, observability, deployment, migration, and operational behavior. |
| security-verification | Implements focused security verification for changed access control, sensitive-data, request-protection, and secret-handling behavior. |
| server-driven-component-contract | Defines explicit backend contracts for independently server-driven frontend components using HTMX or Server-Sent Events. |
| spec-driven-implementation | Implements code changes aligning a codebase with requirements and consistent approved specifications, including tests, migrations, validation, and regenerated documentation. |
| specification-gap-handoff | Classifies code-to-authority documentation gaps and creates durable, evidence-backed handoffs for the correct requirements or specification owner. |
| specification-quality-gate | Performs a final completeness, consistency, evidence, stack, workflow, API, data, frontend, security, and implementation-readiness review. |
| specification-reconciliation | Compares requirements and consistent approved specifications with code-derived behavior to create a traceable reconciliation plan. |
| tailwind | Configures Tailwind standalone CLI input, content scanning, generated CSS output, and backend static-file serving. |
| technical-agent-skill-builder | Creates or revises one deterministic technical OpenCode agent or skill. |
| technology-rule-alignment | Routes one sourced technology or stack rule to the smallest existing agent or skill surface and defines future audit criteria. |
| vault-ingestion | Ingests a URL into an Obsidian or OKF vault as a durable, searchable note. Use when saving web pages, articles, documentation, or research references. |
| workflow-state-modeling | Designs or recovers explicit business workflows, lifecycle states, transition rules, funnels, audit events, and edge cases. |


## Graphify

Code-oriented agents may load `graphify` only when `graphify-out/graph.json` exists. The skill selects focused graph queries before broad reports or raw source search, and updates the graph after relevant code changes.

## Workflow ownership

- An optional `/tmp/opencode/lifecycle-policy.json` supplies a validated version-1 lifecycle override: base, feature prefix, sources, remote, evidence IDs, check and visual allowlists, and delegate hints. It cannot relax exact-head/provenance, explicit authorization, validation, authenticated-actor, manual-squash/no-auto-merge, rejection-open, sequential-commit, or fail-closed recovery invariants.
- `sdlc-orchestrator` is the sole code-change lifecycle owner for explicit `cli`, `openchamber`, and `github-issue` entry points. Every successful run publishes one pull request and ends with a verified user-performed manual squash merge or exact-head rejection.
- CLI preparation creates a clean `feature/*` branch and can recover a current non-base CLI branch. Direct OpenChamber preparation validates or recovers its existing linked worktree and branch. Issue preparation additionally recovers GitHub state and verifies issue readiness, route, and dependencies.
- Requirements route to `prd-strategist`, shared architecture and cross-feature decisions to `app-spec-architect`, bounded feature contracts to `code-spec-engineer`, defects to `bug-fixer`, and other implementation to `code-implementor`.
- Implementation delegates edit and validate only. The orchestrator owns baselines, reviewed commits, idempotent pull-request publication, required checks, correction loops, user decisions, manual-merge verification, and remote-branch cleanup. Agents never merge pull requests automatically.
- The orchestrator owns the ordered user-decision ask and selection directly; `github-pr-approved-merge` and `github-pr-rejection` remain separate leaf procedures. GitHub lifecycle scripts share `/code/skills/github_pr_lifecycle_common.py` for fail-closed identity and version-1 result-envelope primitives.
- A rejected pull request and branch remain open without mutation. Pending or unavailable hosted checks return a resumable waiting state rather than a terminal failure.
- `github-issue-manager` manages issue intake and routes ready execution to `sdlc-orchestrator` with entry point `github-issue`. Current-head lifecycle evidence is posted after required checks pass; the completion comment and issue closure occur only after a verified user-performed manual squash merge and verified remote-branch cleanup.
- Direct `agent-builder` use is audit-only. Agent or skill edits require orchestrator delegation and return changed paths plus validation without staging, committing, or pushing.
- Code-writing delegates end with `project-validation`. Unsupported project-native validation commands require confirmation instead of being silently unavailable.
- Browser-capture commands and comparison behavior live in `browser-visual-capture`; agents only decide when the skill applies.
- Frontend component examples live behind `frontend-reference-examples`: agents read its catalog, then only a matching component document. References never override approved requirements, specifications, or repository conventions.

### Lifecycle policy overrides

Every lifecycle script accepts `--policy /tmp/opencode/lifecycle-policy.json`. Omit it for the documented defaults. The JSON object is versioned (`version: 1`), rejects unknown keys, and records its effective value in lifecycle evidence.

| Section | Policy fields | Rule |
| --- | --- | --- |
| Repository | `base_branch`, `feature_branch_prefix`, `provenance`, `remote` | Selects the repository-local lifecycle names and permitted entry sources. |
| Authorization | `authorization.commit`, `publication`, `cleanup`, `comment`, `closure` | Declares the required gate; unsafe substitutions are rejected. |
| Evidence | `evidence.current_id`, `completion_id`, `require_authenticated_actor`, `actor_transfer` | Allows named evidence IDs while requiring one authenticated actor for current and completion evidence. |
| Decision/recovery | `manual_merge`, `pull_request`, `recovery` | Manual squash, ready/rejection-open, exact head, and block-on-ambiguity remain required. |
| Validation | `validation.required_check_allowlist`, `visual_scenarios` | When nonempty, blocks unallowlisted checks or visual scenarios. |
| Delegation/intake | `delegates.hints`, `commit_strategy`, `blocked_issue_creation` | Carries delegate hints; commits remain sequential/reviewed and blocked issue creation remains forbidden. |

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
