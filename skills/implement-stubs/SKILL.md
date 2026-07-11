---
name: implement-stubs
description: Find and safely implement unfinished functions in the current repository.
---

# Implement unfinished functions

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

- Confirm the Git working tree is clean.
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

1. Run the appropriate formatter.
2. Run the narrowest relevant tests.
3. Run the package or repository build.
4. Run the broader test suite when practical.
5. Show `git diff --stat`.
6. Summarize the change and validation results.

If validation fails:

- attempt a focused correction;
- do not make unrelated changes;
- restore the working tree if the implementation cannot be validated.

Never commit, push, or open a pull request.
