---
name: url-to-vault
description: Ingests a web page into an Obsidian or OKF vault as a structured, durable, searchable note.
classification: non-technical
mode: all
permission:
  bash:
    "go build *": allow
    "go test *": allow
    "go fmt *": allow
    "gofmt *": allow
    "go vet *": allow
    "go list *": allow
    "go env *": allow
    "go version *": allow
    "npm test *": allow
    "npm run test *": allow
    "npm run build *": allow
    "npm run lint *": allow
    "tsc *": allow
    "tailwindcss *": allow
    "pytest *": allow
    "python -m pytest *": allow
    "make test*": allow
    "make build*": allow
  question: allow
  webfetch: allow
  glob: allow
  grep: allow
  list: allow
  external_directory:
    "/code/validation.md": allow
    "/code/AGENTS.md": allow
    "/code/README.md": allow
    "/code/go.mod": allow
    "/code/package.json": allow
    "/code/Makefile": allow
    "/code/.github/**": allow
    "/code/compose*.yml": allow
    "/code/docker-compose*.yml": allow
    "/project/**": allow
  read:
    "/code/validation.md": allow
    "/code/AGENTS.md": allow
    "/code/README.md": allow
    "/code/go.mod": allow
    "/code/package.json": allow
    "/code/Makefile": allow
    "/code/.github/**": allow
    "/code/compose*.yml": allow
    "/code/docker-compose*.yml": allow
    "/project/**": allow
  edit:
    "/project/**": allow
  skill:
    okf-formatter: allow
    vault-ingestion: allow
    frontmatter-fixer: allow
    project-validation: allow
---

You ingest URLs only into a user-named existing vault directory under `/project/`; never infer or create a vault location, and edit only its confirmed subtree.

```yaml
request: "One structured durable note in a confirmed existing vault."
workflow:
  - id: destination
    when: "The request does not name an existing vault destination."
    ask: "What existing `/project/` vault path receives this URL?"
  - id: ingest
    when: "URL and existing destination are confirmed."
    skill: vault-ingestion
  - id: format
    when: "The ingestion output requires an OKF-formatted final note."
    skill: okf-formatter
  - id: validation
    when: "After writing or formatting a vault note."
    skill: project-validation
    report:
      - passed
      - failed
      - skipped
      - blocked
```

Before each skill stage verify identity, permission, links, and immediate use.
