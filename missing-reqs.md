# Code-Quality Rules Missing From Agents And Skills

## Scope And Conclusion

Re-analysis focused on reusable implementation quality, not feature completeness. Authoritative requirements and approved specifications under `/project/` were compared with relevant definitions under `/code/agents/` and `/code/skills/`. Requirements override specifications.

The current catalog has strong foundations for interface seams, Go idioms, immutable migrations, explicit frontend ownership, focused validation, and final project validation. Its largest quality gap is between those foundations: no deterministic implementation procedure forces backend mutations, reads, persistence, API projections, async work, and runtime wiring through the project’s recurring correctness invariants.

No agent or skill was modified. Findings below are recommendations for a later approved refactor.

## Architecture To Retain

- Keep `interface-boundaries` as the owner of consumer-owned ports, adapter isolation, composition-root injection, domain-shaped contracts, and explicit transaction ownership (`skills/interface-boundaries/SKILL.md:30-43`).
- Keep `go-code-standards` focused on language-level Go quality; do not overload it with project-specific product rules (`skills/go-code-standards/SKILL.md:29-63`).
- Keep `postgres-migration` as the immutable forward-only migration owner (`skills/postgres-migration/SKILL.md:49-184`).
- Keep specification procedures separate from implementation procedures. `data-persistence-modeling`, `workflow-state-modeling`, and `api-integration-modeling` already capture useful design inputs (`skills/data-persistence-modeling/SKILL.md:24-87`; `skills/workflow-state-modeling/SKILL.md:23-60`; `skills/api-integration-modeling/SKILL.md:21-87`).
- Keep `project-validation` as the final completion dependency after implementation and selected post-change checks (`agents/code-implementor.md:174-181`; `agents/bug-fixer.md:161-168`).
- Create no new agent. Every recommended rule fits an existing entry point plus focused skills.

## Verified Findings

### P0 — Backend business changes lack one deterministic correctness procedure

**Authority:** `/project/requirements/account-signup.md:23-39`; `/project/requirements/alerting.md:68-87`; `/project/requirements/monitoring-agents.md:25-30,45-56`; `/project/requirements/email-alert-delivery-ses.md:59-78`; `/project/specification/architecture/shared-workflows.md:40-64,79-104,127-149,158-217`.

**Current gap:** `safe-code-change` asks for the smallest complete change but has no applicability analysis for atomicity, idempotency, concurrency, durable claims, immutable event-time snapshots, audit coupling, or crash recovery (`skills/safe-code-change/SKILL.md:44-51`). `backend-scaffolding` is intentionally a scaffold procedure (`skills/backend-scaffolding/SKILL.md:52-60`). `interface-boundaries` makes transaction ownership explicit but does not implement a use case (`skills/interface-boundaries/SKILL.md:30-37`). `code-implementor` therefore falls back to a generic change procedure for most completed backend workflows (`agents/code-implementor.md:136-149`).

**Code-quality rule:** every state-changing use case must explicitly identify one application transaction owner; all action-owned state, audit, event, queue, snapshot, and session effects commit together or roll back. Concurrent/retryable work must define durable ownership, an opaque claim/version token, lease or stale-owner behavior, deterministic idempotency identity, duplicate-completion behavior, and crash recovery. Delayed work must consume immutable event-time snapshots rather than mutable current configuration.

**Recommended owner:** create one cohesive **technical** skill, tentatively `backend-workflow-implementation`, for implementing a completed backend use case. Inputs: approved use-case contract, affected service/repository/adapter paths, transaction and side-effect contract, and concurrency/idempotency contract. Wire it as the implementation branch in `code-implementor` and `bug-fixer` when a state-changing backend workflow is affected. Reuse `interface-boundaries`; do not duplicate that skill’s port-design procedure.

**Audit criterion:** a changed backend command is nonconforming if transaction ownership, rollback behavior, concurrency guard, duplicate behavior, snapshot timing, or recovery is applicable but absent from code and tests.

### P0 — Tenant isolation is tested too shallowly

**Authority:** `/project/requirements/account-signup.md:15-18,35-39`; `/project/requirements/alert-destinations.md:50-55,63-68`; `/project/requirements/customer-incident-detail-activity.md:35-45,62-66`; `/project/requirements/email-delivery-result-detail.md:39-43`; `/project/requirements/webhook-delivery-result-detail.md:36-40`.

**Current gap:** `security-verification` tests wrong-owner and wrong-tenant denials but does not require tenant scope to be derived from the authenticated principal, parent/child ownership to be verified before projection, equivalent non-disclosing outcomes, zero unauthorized store over-read, or zero side effects (`skills/security-verification/SKILL.md:44-52`). `api-auth-testing` asks for one cross-tenant denial but not linked-resource mismatch or disclosure equivalence (`skills/api-auth-testing/SKILL.md:34-40`).

**Code-quality rule:** derive tenant identity only from the authenticated session or membership. Scope the initial repository query by tenant. Validate every nested parent, child, subtype, and channel relationship before projection. Unknown, mismatched, wrong-channel, unaffiliated, and cross-account identifiers must produce the same safe absence result without counts, ownership hints, partial data, extra reads, or mutations.

**Recommended owner:** strengthen `security-verification` as the general implementation check and `api-auth-testing` as the API matrix. `api-discovery` should record tenant-source and nested-ownership rules. No new skill or agent is needed.

**Audit criterion:** every changed tenant-owned endpoint or repository operation has authorized success plus unknown, wrong-tenant, mismatched-parent/child, and wrong-subtype tests proving equivalent safe output and no unintended effects.

### P0 — Browser-impact completion still bypasses the approved quality gate

**Authority:** `/project/requirements/frontend-browser-validation.md:21-43`; `/project/specification/architecture/frontend-impact-validation.md:25-128`; `/project/specification/features/frontend-impact-validation-orchestrator.md:48-203`.

**Current gap:** `browser-visual-capture` captures arbitrary URLs and temporary screenshots (`skills/browser-visual-capture/SKILL.md:19-102`). `browser-visual-compare` allows percentage thresholds and ignored rectangles (`skills/browser-visual-compare/SKILL.md:74-89`). `frontend-scaffolding`, `code-implementor`, and `bug-fixer` treat these generic tools as the visual completion path (`skills/frontend-scaffolding/SKILL.md:56-78`; `agents/code-implementor.md:130-161`; `agents/bug-fixer.md:137-157`). This does not prove dependency-closure classification, production-shaped state, fresh baseline/post-change targets, accessibility behavior, teardown, secret safety, or zero unexplained regressions.

**Code-quality rule:** browser impact follows dependency closure, not file location. Every affected actor/route/state requires production routes, compiled assets, exact deterministic scenarios, fresh baseline and post-change `NPDF-CAP-v1` runs, behavior and nonvisual accessibility assertions, zero unexplained/protected pixel differences, confirmed teardown, and pass-only publication. Missing or non-comparable evidence is `inconclusive`, never passed.

**Recommended owner:** when the specified executable orchestrator exists, expose it through one cohesive **technical** frontend-impact-validation skill. Keep capture and comparison as adapter/diagnostic skills, not completion authorities. Replace the three code-editing workflows’ capture/compare completion stages with the gate; generic capture/compare may remain an internal recursive edge. Until executable support exists, affected completion is `blocked` or `inconclusive`.

**Audit criterion:** no direct or indirect browser-impact change may report passed from screenshots, selectors, source assets, static fixtures, or generic pixel thresholds alone.

### P0 — Database-backed integration quality can bypass the sole safe fixture lifecycle

**Authority:** `/project/requirements/non-production-database-fixtures.md:21-53`; `/project/specification/architecture/non-production-database-fixtures.md:28-58,81-148`.

**Current gap:** `backend-integration-testing` accepts generic project-native containers or isolated services (`skills/backend-integration-testing/SKILL.md:49-57`). `postgres-migration-integration-testing` permits project-native provision/reset behavior (`skills/postgres-migration-integration-testing/SKILL.md:45-54`). `project-validation` allows a generic project provisioner after configuration checks (`skills/project-validation/SKILL.md:55-64`). None distinguishes ordinary migration verification from deterministic feature-fixture state through the required shared capability.

**Code-quality rule:** any integration or browser test requiring deterministic application database state must extend `NPDF-CAP-v1`; it must not create its own allocation, migration, seed, clock, identity, cleanup, or safety path. Verify explicit non-production mode and lease-bound fresh whole-database ownership before mutation; use current migrations and production interfaces; deny all reachable external effects; destroy only the attested target or quarantine uncertainty; retries use wholly new target/session identities.

**Recommended owner:** create one cohesive **technical** `non-production-database-fixture` execution skill only when the executable capability is available. `backend-integration-testing`, `api-integration-testing`, `postgres-migration-integration-testing`, frontend-impact validation, and `project-validation` should select it only when deterministic feature state is required. Preserve a separate narrow path for migration tests that do not require feature fixture composition.

**Audit criterion:** every database-backed feature test names its lifecycle owner and proves it is not using ad hoc URL construction, reset, truncation, shared state, or feature-owned cleanup.

### P1 — Persistence modeling does not require race-proof invariants or stable total ordering

**Authority:** `/project/specification/schema/internal-monitoring-coordination.md:42-70,146-170`; `/project/specification/schema/monitoring.md:72-90,150`; `/project/specification/architecture/runtime-and-operations.md:66-77`; `/project/requirements/customer-incident-detail-activity.md:26-35,50-55`; `/project/requirements/customer-incident-detail.md:24-35,61-65`.

**Current gap:** `data-persistence-modeling` names constraints, indexes, tenancy, concurrency, and transactions but does not require each persistent invariant to map to both service enforcement and an appropriate database constraint, nor every paginated/latest query to define one persisted unique tie-breaker (`skills/data-persistence-modeling/SKILL.md:41-53,71-87`). Migration integration tests likewise do not explicitly require race or page-boundary evidence (`skills/postgres-migration-integration-testing/SKILL.md:45-54`).

**Code-quality rule:** enforce concurrency-sensitive invariants in both application transitions and PostgreSQL constraints/guarded updates. Every paginated, timeline, history, and “latest” query must define a total persisted order: authoritative business timestamp/state followed by a unique persisted identifier, applied before slicing and reused across refresh/retry/page traversal.

**Recommended owner:** revise `data-persistence-modeling`, `postgres-schema-designer`, `backend-integration-testing`, and `postgres-migration-integration-testing`. Do not put these project/database rules into `go-code-standards`.

**Audit criterion:** each changed invariant identifies service guard, database guard, transaction owner, race test, and failure behavior; each ordered read identifies the complete `ORDER BY` and page-boundary test.

### P1 — Read paths are not required to be observational

**Authority:** `/project/requirements/alert-destinations.md:50-55,72-77`; `/project/requirements/email-delivery-result-detail.md:39-46`; `/project/requirements/webhook-delivery-result-detail.md:36-43`; `/project/requirements/customer-incident-detail.md:52-56,83-88`.

**Current gap:** API and backend testing verify expected effects but do not establish that GETs, fragments, polling, SSE, modal detail, retry reads, and diagnostics have zero domain/provider/audit/session/retention effects (`skills/api-integration-testing/SKILL.md:55-70`; `skills/backend-integration-testing/SKILL.md:49-57`).

**Code-quality rule:** reads and refreshes are side-effect free unless authority explicitly defines a write. They must not call providers, resend/replay, allocate attempts, refresh sessions, append audits, extend retention, change health/retry state, or lock rows as commands. Repeated reads must preserve domain state and outbound-call count.

**Recommended owner:** add read-versus-command classification to `api-integration-modeling`, `api-discovery`, `api-integration-testing`, and `backend-integration-testing`. No new skill is needed.

**Audit criterion:** every changed read endpoint has state-before/state-after and zero-external-call evidence; any intentional read-side write cites explicit authority.

### P1 — API projection and error quality is underspecified in implementation checks

**Authority:** `/project/specification/api/internal-monitoring-api.md:36-44,275-300`; `/project/requirements/alert-destinations.md:53-55,66-68,89`; `/project/requirements/email-delivery-result-detail.md:39-43`; `/project/requirements/webhook-delivery-result-detail.md:36-40`; `/project/specification/schema/email-alert-delivery-ses.md:143-152`.

**Current gap:** API conformance tests cover fields, nullability, statuses, and errors only when explicitly listed (`skills/api-contract-conformance-testing/SKILL.md:49-57`). Security checks assert sensitive-data absence but do not require response allowlists, pre-boundary error redaction, stable provider error classes, bounded excerpts, or semantic distinction among null, unavailable, zero, empty, accepted, delivered, and failed (`skills/security-verification/SKILL.md:44-52`).

**Code-quality rule:** construct explicit transport/read-model allowlists instead of serializing persistence entities. Redact provider and secret-bearing errors before they enter transport, logs, metrics, audits, or diagnostics. Use stable machine error codes and safe status mappings. Preserve domain truth: never turn absent/unavailable into zero, success, empty, or fabricated values; acceptance is not delivery.

**Recommended owner:** revise `api-integration-modeling`, `api-contract-conformance-testing`, `security-verification`, and `backend-integration-testing`. Keep feature-specific fields in authority; backport only the projection/error discipline.

**Audit criterion:** every changed boundary has an explicit field allowlist, safe typed error mapping, null/unavailable semantics, and tests against accidental persistence/provider-field leakage.

### P1 — External integration quality omits ambient-credential rejection and immutable retry snapshots

**Authority:** `/project/requirements/email-alert-delivery-ses.md:15-20,24-31,33-49,59-78`; `/project/requirements/alert-destinations.md:43-46,72-77`; `/project/requirements/alerting.md:68-74`.

**Current gap:** `api-integration-modeling` covers retries/idempotency and adapter seams but does not require explicit credential-source policy or event-time snapshots (`skills/api-integration-modeling/SKILL.md:43-87`). `api-resilience-testing` checks retry behavior but not rejection of environment/default-chain/metadata fallback or preservation of frozen configuration across retries (`skills/api-resilience-testing/SKILL.md:49-57`).

**Code-quality rule:** external adapters receive explicit authorized configuration and credentials; ambient environment, profile, role, metadata, or transport fallbacks are disabled when authority requires persisted configuration. Delayed/retried work uses immutable event-time payload, destination, recipient, signing/config revision, and event identity snapshots; retries never mix later edits into earlier work.

**Recommended owner:** revise `api-integration-modeling`, `interface-boundaries`, `api-resilience-testing`, and `security-verification`.

**Audit criterion:** every changed external adapter identifies credential provenance, disabled fallback paths, snapshot creation point, stable retry identity, and tests proving later configuration edits do not alter queued work.

### P1 — Frontend implementation omits several source-quality invariants

**Authority:** `/project/requirements/backend-platform.md:22-23`; `/project/requirements/compiled-frontend-delivery.md:13-28`; `/project/specification/frontend/foundation/frontend-stack.md:10-20`; `/project/specification/frontend/migrations/semantic-color-token-adoption.md:16-25,39-48`; `/project/specification/features/compiled-frontend-delivery.md:48-137`.

**Current gap:** `frontend-scaffolding` is restricted to `/code/src/frontend/`, although approved browser work may require standalone `.gohtml`, the Go embed owner, route serving, and generated-output synchronization (`skills/frontend-scaffolding/SKILL.md:72-79`). It does not prohibit direct repair of generated `dist`/embedded outputs or require source → generated → embedded → served parity. `tailwind` preserves generated output but does not say regeneration is the only valid update path (`skills/tailwind/SKILL.md:24-49`). `release-readiness-validation` is generic (`skills/release-readiness-validation/SKILL.md:44-56`).

**Code-quality rule:** server HTML and fragments remain standalone `.gohtml`; browser JS enhances presentation but does not own domain state. Handwritten source is edited, generated outputs are regenerated, and one embed owner supplies production/test/browser validation. Required assets are same-origin, self-hosted, CWD-independent, and current before packaging. Generated or embedded outputs must never be independently patched.

**Recommended owner:** broaden `frontend-scaffolding` inputs/permissions or split it into source-component implementation and compiled-delivery integration; revise `tailwind` and `release-readiness-validation`. Preserve `htmx` as the request/swap owner.

**Audit criterion:** browser-file changes identify the handwritten source, regeneration command, generated output, embed owner, serving route, and parity validation; direct generated-output-only edits fail review.

### P1 — Frontend state quality is incomplete despite good ownership rules

**Authority:** `/project/requirements/background-refresh-ux.md:13-23`; `/project/specification/frontend/foundation/common-design-language.md:49-57,108-131`; `/project/specification/frontend/patterns/loading-empty-error-detail-surfaces.md:11-27`; `/project/requirements/reusable-frontend-tables.md:20-50`.

**Current gap:** `frontend-scaffolding` correctly defines component roots and HTMX/client ownership, but does not require explicit initial-loading, populated, empty, error, pending, and recovery states; last-known-good preservation; stable hooks; design-system reuse; native semantics beyond the root; or preservation of input, page/filter/range/modal/focus/scroll during refresh (`skills/frontend-scaffolding/SKILL.md:74-79`). `frontend-behavior-testing` has a useful matrix but does not enumerate these shared invariants (`skills/frontend-behavior-testing/SKILL.md:49-57`).

**Code-quality rule:** each async region owns explicit local states and recovery. Empty is not error. Post-load failure retains valid content and unaffected siblings. Refresh swaps only the owning boundary and preserves applicable drafts, selection, pagination, range, modal identity, focus, and scroll. Prefer native semantics, shared components/tokens, stable `data-*` hooks, visible focus, and one accessible action path.

**Recommended owner:** revise `frontend-component-modeling`, `frontend-scaffolding`, `frontend-behavior-testing`, `accessibility-testing`, and `server-driven-component-contract`. Keep feature-specific transport adoption out of generic skills; SSE remains opt-in.

**Audit criterion:** every changed async surface has a complete state matrix, ownership boundary, preservation matrix, accessible status/focus behavior, and focused behavior tests.

### P1 — Startup, probe, and test-capability exclusion checks are too generic

**Authority:** `/project/requirements/backend-platform.md:24-27`; `/project/requirements/development-default-accounts.md:15-27`; `/project/requirements/development-observability.md:15-18,29-34`; `/project/specification/api/operations-api.md:22-66`; `/project/specification/architecture/non-production-database-fixtures.md:120-126`.

**Current gap:** `release-readiness-validation` checks startup order and health/readiness generally, but not fail-closed prerequisite barriers, constant-time snapshot-only probes, minimal public responses, no dependency work per probe, or structural absence of test/development capabilities from production artifacts and routes (`skills/release-readiness-validation/SKILL.md:44-56`).

**Code-quality rule:** complete migrations and mandatory initialization before serving or worker execution. Initial failure exits nonzero. Readiness is conjunctive and remains false through recovery barriers while liveness may remain true. Public probes return fixed minimal no-store snapshots and trigger no database, migration, listener, retry, or recovery work. Test-only registries, brokers, seeders, session bootstrap, error-ingest routes, and destructive code are absent from production composition roots, routes, binaries/images, and startup commands.

**Recommended owner:** strengthen `release-readiness-validation` and its trigger in `code-implementor`; add relevant security assertions to `security-verification`. No new agent is needed.

**Audit criterion:** applicable changes include startup-failure tests, readiness transition tests, per-probe zero-dependency-call tests, minimal-disclosure assertions, and production dependency/artifact/route/startup inspection.

### P1 — Integration tests do not consistently test at the invariant-owning boundary

**Authority:** `/project/specification/features/internal-monitoring-coordination.md:328-360,373-382`; `/project/specification/api/operations-api.md:64-66`; `/project/specification/features/customer-incident-action-alert-materialization.md:116-125`.

**Current gap:** `backend-integration-testing` selects the narrowest harness and only tests rollback, authorization, idempotency, and retry “where authority requires it” (`skills/backend-integration-testing/SKILL.md:51-57`). The project authority repeatedly requires real PostgreSQL proof for constraints, ordering, leases, races, and rollback, while fakes are appropriate for handler/service mapping and providers.

**Code-quality rule:** test each invariant at the boundary that owns it. Use fakes through production ports for orchestration, clocks, and provider failures. Use disposable PostgreSQL for constraints, ownership joins, transaction rollback, migration behavior, total ordering, lease races, stale owners, duplicate completion, and concurrent workers. Include injected mid-transaction failure and duplicate/restart paths when applicable.

**Recommended owner:** strengthen `backend-integration-testing`, `postgres-migration-integration-testing`, and API resilience/auth testing matrices. The code-editing agent already selects these stages; improve their trigger wording to include invariant signals rather than only file categories.

**Audit criterion:** every claimed invariant has a test whose execution boundary can actually falsify it; mock-only evidence cannot prove database atomicity or concurrency.

### P2 — Observability quality needs a reusable safe-evidence checklist

**Authority:** `/project/requirements/development-observability.md:19-27`; `/project/requirements/admin-checks-queue-observability.md:26-35`; `/project/requirements/monitoring-agents.md:27-33,51-56`; `/project/specification/architecture/runtime-and-operations.md:121-147`.

**Current gap:** `security-operations` inventories logging and metrics but does not require stable classifications, bounded samples, truncation indicators, expected-control-flow distinction, cardinality limits, or recursion/spam prevention (`skills/security-operations/SKILL.md:44-70`). `release-readiness-validation` only checks configured fields against requirements (`skills/release-readiness-validation/SKILL.md:46-56`).

**Code-quality rule:** logs and metrics use stable classifications/outcomes, safe correlation fields, bounded samples, explicit truncation, and low-cardinality labels. Expected no-work is distinct from anomalies. Raw payloads/errors and secret-adjacent values are redacted before emission. Error-reporting failure cannot recurse or spam.

**Recommended owner:** revise `security-operations`, `backend-integration-testing`, `security-verification`, and `release-readiness-validation`. Create a dedicated technical observability-testing skill only if recurring implementation work cannot remain cohesive inside backend integration testing.

**Audit criterion:** changed diagnostics have a field allowlist, secret/cardinality review, bounded-output behavior, expected-versus-anomalous classification tests, and recorder-failure tests where applicable.

## Prioritized Approved-Revision Plan

1. Add `backend-workflow-implementation`; wire it into `code-implementor` and `bug-fixer` for state-changing backend workflows.
2. Strengthen tenant isolation across `security-verification`, `api-auth-testing`, `api-discovery`, and API integration reporting.
3. Add executable frontend-impact and non-production-database-fixture skills only when their specified commands/capabilities exist; replace generic completion wiring, not the underlying adapters.
4. Add invariant/order/read-side quality rules to persistence, API, backend integration, and migration integration skills.
5. Add frontend source/output parity and async-state preservation rules to frontend implementation/testing skills.
6. Strengthen release readiness for startup barriers, probes, compiled delivery, and structural production exclusion.
7. Add observability evidence rules last; prefer extending existing skills before creating another skill.

## Technology-Rule Alignment Criteria

Apply these criteria only in future relevant audits/revisions:

| Rule family | Applicability signal | Smallest owner | Required evidence |
|---|---|---|---|
| Transactional workflow | Multi-record mutation, audit/event/queue effect, worker completion | `backend-workflow-implementation` | One transaction owner, rollback test, concurrency/idempotency behavior |
| Tenant isolation | Customer-owned identifier or nested resource | `security-verification` / `api-auth-testing` | Auth-derived tenant scope, mismatch matrix, nondisclosure, zero side effects |
| Persistence invariant | Concurrently enforceable state or ordered collection | `data-persistence-modeling` / integration testing | Service and DB guards, total order, race/page-boundary tests |
| Read purity | GET, fragment, poll, SSE, modal detail, diagnostic read | API/backend integration testing | State equality and zero outbound/provider calls |
| External integration | Provider adapter, delayed/retried delivery | API modeling/resilience/security | Explicit credential provenance, immutable snapshot, stable retry identity |
| Frontend source quality | Template, CSS/TS, embed, asset route, generated output | `frontend-scaffolding` / release readiness | Source-to-generated-to-embedded-to-served parity |
| Async frontend quality | Loading, refresh, mutation, stream, modal | Frontend modeling/implementation/testing | State and preservation matrices, accessible recovery |
| Runtime safety | Startup, readiness, probes, dev/test helper | Release readiness/security | Fail-closed startup, snapshot-only probe, production exclusion inspection |
| Browser impact | Direct or dependency-closure browser effect | Future frontend-impact-validation skill | Production-shaped fresh two-phase gate evidence |
| Database fixture | Deterministic database-backed feature state | Future fixture execution skill | Broker-attested lifecycle, denial adapters, exact teardown/quarantine |

## Audit Checks

- **Classification:** recommended new procedures are `technical`; reviewed modeling/documentation skills remain `non-technical` because their primary output is specification or supporting knowledge.
- **Role boundaries:** no new agent is warranted. Existing `code-implementor`, `bug-fixer`, and `api-integration-tester` remain the user-facing entry points.
- **Skill cohesion:** recommendations separate backend workflow implementation, browser-impact validation, and database-fixture execution because each performs one distinct reusable task.
- **Duplication:** retained `interface-boundaries`, migration, HTMX, and project-validation ownership; recommendations reference rather than duplicate them.
- **Tree wiring:** future code-editing flows must retain final `project-validation` after all selected post-change checks and report `passed`, `failed`, `skipped`, or `blocked`.
- **Permissions:** no contracts changed. Any approved revision must update each skill’s minimum `opencode_permission` and every calling agent’s exact skill, command, and path coverage.
- **YAML:** no agent/skill frontmatter or fenced YAML changed; flow-collection validation is not applicable to this report.
