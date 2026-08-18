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

Run unchecked `todo.md` tasks through OpenCode until each task reports a loop sentinel.

```sh
./loop <project> <agent> [git-repo]
./loop --test <project> <agent> [git-repo]
```

| Item | Behavior |
| --- | --- |
| Todo source | Reads unchecked markdown tasks (`- [ ] task`) from `[git-repo]/todo.md`; default repo is `/code`. |
| Runner call | Resolves sibling `run` from the script directory and calls `opencode run "<prompt>" --agent "<agent>"`. |
| Progress UI | Prints colored status at startup and during progress: project, agent, repo, todo file, counts, max loops, current line/task, and attempt. |
| Dry run | `--test` prints detected tasks, commands, prompts, and summary without OpenCode runs or file edits. |

### Task outcomes

| Sentinel | Result |
| --- | --- |
| `<task>DONE</task>` | Opens a commit session if worktree changes remain, marks the todo complete, commits todo progress when Git is available, then moves to the next todo. |
| `<task>BLOCKED</task>` | Leaves the todo unchecked, reverts task-owned changes with `git reset --hard` and `git clean -fd`, then exits `2`. |
| No sentinel | Repeats the same todo until `MAX_LOOPS`; the prompt requires the agent to write `/project/handoff.md` before continuing. |
| Ctrl+C | Lets the active OpenCode run finish, processes its result, then exits `130` before another retry or todo starts. |

### Git safety

- Preflight prompts for a `code-implementor` commit session when tracked changes already exist.
- The loop requires a clean worktree before task execution so BLOCKED can safely revert task-owned changes.
- Dirty worktrees between completed todos are stashed with the completed todo line number in the stash message.
- Todo-loop prompts require `todo-upkeep` for discovered follow-ups, `git-auto-commit` before DONE, and `/project/handoff.md` for continuation.

### Output safety

Runner output is captured through a temporary file. NUL bytes are stripped before printing and sentinel detection to avoid shell command-substitution warnings from binary or malformed subprocess output.
