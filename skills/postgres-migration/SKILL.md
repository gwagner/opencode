---
name: postgres-migration
description: Create safe, forward-only PostgreSQL schema migrations in /code/migrations. Use when adding, changing, or removing PostgreSQL tables, columns, indexes, constraints, types, functions, triggers, policies, or other schema objects. Existing migration files are immutable: never edit, rename, delete, replace, or reuse a migration after it has been written; create a new migration file for every subsequent change or correction.
compatibility: opencode
metadata:
  database: postgresql
  migration-directory: /code/migrations
  strategy: forward-only
---

# PostgreSQL schema migrations

Create PostgreSQL schema migrations as immutable, forward-only SQL files in:

`/code/migrations/*.sql`

## Non-negotiable rules

1. Never modify an existing migration file.
2. Never rename, delete, truncate, overwrite, or replace an existing migration file.
3. Never reuse an existing migration filename.
4. If an existing migration is incorrect, create a new migration that corrects or reverses it.
5. Before writing a migration, list and inspect `/code/migrations` to understand the current migration history.
6. Treat a migration as immutable immediately after its file is created.
7. Write only schema-migration SQL to `/code/migrations`. Do not place application code or generated artifacts there.
8. Do not execute migrations against a database unless the user explicitly asks you to do so.

If a requested task would require changing an existing migration, refuse that specific edit and create a new corrective migration instead.

## Workflow

### 1. Inspect the repository

Before designing the migration:

- List all existing files in `/code/migrations`.
- Read relevant existing migrations.
- Inspect the current schema definitions, database access code, and migration tooling when available.
- Determine the repository's established filename and SQL conventions.
- Check whether the requested schema change already exists.

Do not infer the current schema from one file when later migrations may have changed it.

### 2. Choose a unique filename

Prefer the repository's existing naming convention.

When no convention exists, use:

`YYYYMMDDHHMMSS_<descriptive_snake_case>.sql`

Use a UTC timestamp and a concise description, for example:

`20260801153000_add_customer_status.sql`

Before creating the file, verify that the filename does not already exist. If it exists, generate a new timestamp; never overwrite it.

### 3. Design a safe migration

The migration must:

- Target PostgreSQL syntax.
- Contain only the requested change and directly required supporting changes.
- Be deterministic and reviewable.
- Qualify schema names when the repository uses multiple schemas or ambiguity is possible.
- Use explicit constraint and index names.
- Preserve existing data unless destructive behavior is explicitly requested and clearly documented.
- Account for locks, table size, and deployment safety when altering populated tables.
- Avoid broad cleanup or unrelated refactoring.
- Match the project's transaction conventions.

Prefer additive, backward-compatible changes for rolling deployments.

For risky changes, use staged migrations. Examples include:

- Add a nullable column, backfill separately, then add `NOT NULL`.
- Add a new constraint with `NOT VALID`, then validate it in a later migration when appropriate.
- Create large indexes with `CREATE INDEX CONCURRENTLY` when supported by the migration runner.
- Replace a column through add, dual-write/backfill, cutover, and later removal.
- Separate enum-value additions or other operations that have transaction restrictions from incompatible statements.

### 4. Transaction handling

If every statement is safe inside a transaction, wrap the migration in:

```sql
BEGIN;

-- statements

COMMIT;
```

Do not use a transaction wrapper when the migration contains PostgreSQL operations that cannot run in a transaction block, such as `CREATE INDEX CONCURRENTLY`.

When omitting a transaction, add a short SQL comment explaining why.

Do not mix transactional and non-transactional operations in one file when splitting them into separate migrations is safer.

### 5. Write the migration once

Create the new file without replacing an existing path.

After the file is created:

- Re-read it to verify the contents.
- Do not edit it again.
- If verification reveals a problem, create another migration that corrects it.
- Report the exact path created.

The immutability rule applies even during the same task: once written, the migration file is final.

### 6. Validate

Validate as much as the repository permits without mutating a real database:

- Check SQL syntax with the project's migration or lint tooling when available.
- Check that referenced schemas, tables, columns, types, indexes, and constraints match the migration history.
- Check statement ordering and dependencies.
- Check for duplicate object names.
- Check rollback or correction implications.
- Review lock and data-loss risks.
- Confirm no existing migration file changed.

Do not claim a migration was executed or validated against PostgreSQL unless it actually was.

## SQL guidelines

- Use snake_case unless the existing schema uses another convention.
- Avoid quoted identifiers unless required by the existing schema.
- Give indexes and constraints stable, descriptive names.
- Use `IF EXISTS` or `IF NOT EXISTS` only when it supports the project's migration policy; do not use it to hide an unexpected schema state.
- Do not use `CASCADE` unless explicitly required and its impact is understood.
- Do not drop columns, tables, types, or constraints without identifying the data-loss or dependency risk.
- Keep data backfills separate from schema changes when they may be large, slow, or operationally risky.
- Add comments for non-obvious safety decisions, not for self-evident SQL.
- Do not include secrets, credentials, or environment-specific connection details.

## Correcting a prior migration

When a prior migration has a defect:

1. Leave the original file untouched.
2. Determine the schema state produced by the original migration.
3. Create a new migration that moves that state to the desired state.
4. Make the corrective migration safe for environments where the original migration has already run.
5. Explain the relationship between the original and corrective migrations in SQL comments when useful.

Never rewrite migration history to make it appear that the defect did not happen.

## Output expectations

After creating a migration, report:

- The new migration path.
- A concise summary of the schema change.
- Important locking, compatibility, or data-loss considerations.
- Validation performed.
- Any follow-up migration or application deployment step that is required.

Do not paste unrelated files or modify application code unless the user requested those changes.
