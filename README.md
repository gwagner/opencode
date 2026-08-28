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
| blocked-todo-resolution | Resolves self-contained blocked todos without code access, coordinates authoritative updates, and promotes resolved work. |
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
| todo-capture | Captures detailed deferred work in `/code/todo.md` or unresolved work in `/code/blocked-todos.md`. |
| todo-upkeep | Captures detailed loop follow-ups or blockers for later iterations. |
| spec-driven-implementation | Implements authoritative specifications. |
| specification-quality-gate | Reviews specification readiness. |
| specification-reconciliation | Compares code-derived and authoritative specifications. |
| vault-ingestion | Ingests web content into a vault. |
| workflow-state-modeling | Models workflow states and transitions. |

## Graphify

Code-oriented agents may load `graphify` only when `graphify-out/graph.json` exists. The skill selects focused graph queries before broad reports or raw source search, and updates the graph after relevant code changes.

## Container note

`/code/containers/golang/Dockerfile` pre-installs Playwright's bundled `ffmpeg` into `PLAYWRIGHT_BROWSERS_PATH=/ms-playwright` so container runs do not need to fetch it at runtime.

## Loop runner

Run unchecked `todo.md` tasks through OpenCode until each task reports a loop sentinel.

```sh
./loop <project> <agent>
./loop --test <project> <agent>
```

| Item | Behavior |
| --- | --- |
| Project mounts | `run` and `loop` source their sibling `project-mounts.sh`; the selected project is the single source of truth for host documentation/code mounts and container image. |
| Todo source | As an outer host script, `loop` reads unchecked markdown tasks (`- [ ] task`) from the selected project's `CODE_MOUNT/todo.md`. Every implementation-ready entry requires exactly one nonempty, Git-valid `Branch:` metadata value. Indented metadata immediately below the selected task travels with that task in the loop prompt. |
| Runner call | Resolves sibling `run` from the script directory and calls `opencode run "<prompt>" --agent "<agent>"`. |
| Progress UI | Prints colored status at startup and during progress: project, agent, repo, todo file, counts, max loops, current line/task, attempt, loop start timestamp, and loop duration. |
| Dry run | `--test` prints detected tasks, commands, prompts, and summary without OpenCode runs or file edits. |

### Task outcomes

| Sentinel | Result |
| --- | --- |
| `<task>DONE</task>` | Requires validated iteration work, creates a task-branch safety checkpoint if changes remain, marks and commits todo progress, then squash-merges the task branch into one commit on local `main` and deletes the completed task branch. |
| `<task>CONTINUE</task>` | Checkpoints any remaining iteration work and repeats the same todo from a clean task branch. Host file operations use `DOCS_MOUNT/handoff.md`; container-facing prompts retain literal `/project/handoff.md`. If the handoff is absent, the loop invokes its sibling `run` helper with the same project and agent to determine next steps from the selected todo and write a recovery handoff before retrying. If `MAX_LOOPS` is exhausted, the task follows the BLOCKED flow with an exhaustion reason. |
| `<task>BLOCKED</task>` | Appends the task to `CODE_MOUNT/blocked-todos.md` with `Blocked by:` and `Required to unblock:` metadata, removes routing-only `Handoff:` metadata, then removes it from `todo.md`. Partial work is committed on the task branch; the runner clears the host handoff, switches to local `main` without merging, and continues. `todo.md` and `blocked-todos.md` must remain ignored/untracked so their edits persist across that switch. Final output reports the blocked count. |
| Missing token | Refuses the retry and exits nonzero instead of guessing continuation state. A failed or empty missing-handoff recovery also exits nonzero. |
| Ctrl+C | Lets the active OpenCode run finish, processes its result, then exits `130` before another retry or todo starts. |

### Git safety

- A missing task branch starts from current local `main`: the runner switches to `main`, then creates the validated metadata branch.
- If a task branch already exists at fresh task start, the runner resumes it automatically. Worktree changes on another branch still prevent switching.
- Local `main` and exactly one nonempty Git-valid branch value are required. Successfully committed DONE branches are deleted automatically; unmerged BLOCKED branches remain.
- Todo-loop prompts require `todo-upkeep` for discovered follow-ups and `git-auto-commit` before the first edit. Each validated iteration must commit before CONTINUE or DONE; the loop creates a task-branch safety checkpoint when work remains uncommitted.
- Completed task branches are squash-merged so local `main` receives one commit per todo, then deleted. BLOCKED branches retain their checkpoint history and remain unmerged.

### Output safety

Runner output is captured through a temporary file. NUL bytes are stripped before printing and sentinel detection to avoid shell command-substitution warnings from binary or malformed subprocess output.

Successful squash merges suppress Git's raw informational chatter; loop status remains visible, and merge errors still surface.
