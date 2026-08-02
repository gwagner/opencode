# OpenCode configuration

OpenCode assets are loaded from `.opencode/`. Root `agents/` and `skills/` mirror that tree for repository maintenance.

## Agents

| Agent | Purpose |
| --- | --- |
| api-integration-tester | Builds API integration tests. |
| app-spec-architect | Defines cross-feature architecture and shared workflows from requirements. |
| backend-scaffolder | Scaffolds specified backend features. |
| bug-fixer | Reproduces, diagnoses, and fixes defects with regression coverage. |
| code-implementor | Implements approved, focused code changes. |
| code-spec-engineer | Produces bounded implementation-ready feature contracts. |
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
| gap-risk-analysis | Identifies gaps, risks, and assumptions. |
| git-auto-commit | Automatically commits agent-owned, validated Git changes with a verbose rationale. |
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
| spec-driven-implementation | Implements authoritative specifications. |
| specification-quality-gate | Reviews specification readiness. |
| specification-reconciliation | Compares code-derived and authoritative specifications. |
| vault-ingestion | Ingests web content into a vault. |
| workflow-state-modeling | Models workflow states and transitions. |

## Graphify

Code-oriented agents may load `graphify` only when `graphify-out/graph.json` exists. The skill selects focused graph queries before broad reports or raw source search, and updates the graph after relevant code changes.
