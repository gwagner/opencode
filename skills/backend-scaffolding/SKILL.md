---
name: backend-scaffolding
description: Scaffolds reachable backend routes, services, data access, contracts, and useful placeholders from approved requirements and specifications.
---

# Backend scaffolding

1. Inspect existing language, framework, structure, conventions, and validation commands.
2. Use `okf-reader` to load only the relevant feature, workflow, API, data, validation, authorization, and error requirements.
3. Map the required public contract to the smallest coherent route, service, persistence, and wiring changes.
4. Follow existing patterns. Load `interface-boundaries` before defining or changing a route, use case, persistence, integration, or job dependency.
5. Keep routes thin: validate input, invoke the workflow, map errors, and return a structured response.
6. Make incomplete scaffolding honest: define the contract, validate available input, return a typed unavailable error, and add a requirement-linked TODO. Never fake success, credentials, integrations, or persistence.
7. Run the narrowest available formatter, build, and focused tests.

Do not add speculative abstractions, migrations, or unrelated refactors. New routes must be reachable or explicitly marked for registration.
