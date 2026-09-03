---
name: htmx
description: Implements HTMX server-fragment requests, form actions, errors, loading states, and safe swap ownership.
---

# HTMX

Use for server-rendered HTML interactions.

1. Define each request method, URL, request fields, response fragment, target, and swap mode.
2. Keep validation, authorization, mutations, and resulting server state backend-authoritative.
3. Define loading and error rendering for each request; return fragments compatible with the declared target.
4. Give every swappable region one owner. Do not target, replace, or morph DOM inside a client-component-owned root.
5. Pass server data to client components only through declared inputs; consume component events at a boundary outside the component.
