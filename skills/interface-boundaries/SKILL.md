---
name: interface-boundaries
description: Designs deep, focused module interfaces and adapter seams. Use when changing public contracts, external dependencies, persistence access, or cross-layer calls.
---

# Interface boundaries

Use only when the change crosses a module, process, framework, persistence, or external-service boundary.

## Vocabulary

- **Module**: anything with an interface and implementation.
- **Interface**: all facts callers need: types, invariants, ordering, errors, configuration, and performance characteristics.
- **Seam**: where behavior can change without changing callers; where an interface lives.
- **Adapter**: a concrete implementation of an interface at a seam.
- **Depth**: capability hidden behind a small interface. It creates caller leverage and maintainer locality.

## Workflow

1. Identify the consumer, owned behavior, inputs, outputs, failure modes, and composition root.
2. Define the smallest consumer-owned interface that hides the owned complexity. Reduce methods and parameters before exposing details.
3. Add a seam only for a real variation, test need, or established convention. One adapter is usually hypothetical; two adapters establish a real seam. Do not add speculative abstractions.
4. Keep transport, framework, ORM, and vendor types in adapters; expose application/domain types at the boundary where practical.
5. Inject dependencies at composition boundaries. Keep transactions and state-transition ownership explicit.
6. Test through the same interface callers use: focused fakes for owned ports; observable contract or integration tests for adapters when relevant.

## Checks

- Apply the deletion test: if deleting the module merely moves its complexity into callers, it earns its keep; if it disappears, it is a pass-through.
- Keep implementation seams private unless callers genuinely need the variation.
- Do not test past the interface to reach implementation details; reshape the module if that is necessary.
