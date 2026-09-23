---
name: implement-stubs
description: Find and safely implement unfinished functions in the current repository.
classification: technical
opencode_permission:
  read: allow
  glob: allow
  grep: allow
  edit: allow
  skill:
    project-validation: allow
inputs:
  - one bounded unfinished function or selection evidence
  - repository context
  - caller-provided permitted source and test paths
---

# Implement unfinished functions

## Inputs

Require one bounded unfinished function or selection evidence, repository context, and caller-provided permitted source and test paths.

Do not use this procedure when the unfinished function participates in a state-changing backend command, job, or worker workflow. The caller must select the dedicated backend workflow procedure.

## Dead-code rule

Within the selected function's source and directly affected tests, remove unused functions and modules, commented-out code, and logic kept only for reference. Use Git history for reference; do not retain it in source. Preserve potentially live behavior and report uncertainty rather than guessing.

## Deterministic workflow

```yaml
request: "One safely implemented unfinished function"
workflow:
  - id: "validate-project"
    when: "After all selected post-change stages."
    skill: "project-validation"
    report:
      - "passed"
      - "failed"
      - "skipped"
      - "blocked"
```

Work on exactly one unfinished function per invocation.

## Discovery

Search tracked source files for high-confidence unfinished implementation markers:

- `TODO` or `FIXME` mentioning implementation
- `NotImplementedError`
- `UnsupportedOperationException`
- `todo!()`
- `unimplemented!()`
- panic messages containing "not implemented"
- placeholder comments such as `IMPLEMENT ME`

Ignore:

- generated files
- vendor directories
- dependency directories
- build output
- test fixtures unless they are directly relevant
- intentionally empty interface methods or hooks

## Candidate selection

Choose the highest-confidence candidate whose intended behavior can be inferred from:

1. interfaces and type definitions
2. callers
3. adjacent implementations
4. documentation
5. existing tests

Do not implement behavior that is materially ambiguous.

## Before editing

- Inspect the working tree and preserve changes you did not make.
- Identify the enclosing function.
- Read the complete source file.
- Find callers and references.
- Find related tests.
- Determine the repository's formatting, build, and test commands.
- State which function you selected and why.

## Implementation constraints

- Make the smallest complete change.
- Preserve existing public APIs.
- Do not add dependencies without explicit approval.
- Do not edit generated files, vendored code, lock files, CI configuration,
  credentials, authentication code, or database migrations.
- Do not weaken or delete tests.
- Add focused tests when expected behavior is clear.
- Do not refactor unrelated code.

## Validation

After editing:

1. Use `project-validation` to run the appropriate formatter.
2. Use it to run the narrowest relevant tests.
3. Use it to run the package or repository build.
4. Use it to run the broader test suite when practical.
5. Report changed paths and summarize the change and validation results.

If validation fails:

- attempt a focused correction;
- do not make unrelated changes;
- leave the focused change in place and report the validation failure; do not revert collaborative work.

Never commit, push, or open a pull request. The calling agent owns any separately authorized commit after all post-change checks and final project validation pass.
