---
name: vault-ingestion
description: Ingests a URL into an Obsidian or OKF vault as a durable, searchable note. Use when saving web pages, articles, documentation, or research references.
---

# Vault ingestion

1. Validate and fetch the URL.
2. Extract the readable main content and available canonical metadata.
3. Ask only when the vault path, destination, or capture depth cannot be safely inferred.
4. Create an OKF note with source URL, capture date, title, and relevant searchable metadata.
5. Prefer cleaned content over page chrome. Preserve documentation hierarchy and code samples.
6. Avoid duplicate notes: update or warn when a matching source already exists.
7. Report the stored path and any access or extraction limitation.

Do not invent unavailable metadata or remove files without confirmation.
