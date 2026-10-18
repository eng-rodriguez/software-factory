---
name: principles-domain
description: Domain ownership and invariant guidance across languages and frameworks. Use when designing business models, module boundaries or cross-context interactions.
---

Follow [principles-design](../principles-design/SKILL.md) for applicability and precedence.

## Safeguards
1. Name the owner of authoritative business rules and enforce them at the trusted boundary. Client-side validation can improve feedback but cannot replace authorization or server-side invariant checks.
2. Keep cross-context access explicit through the project's agreed interfaces. Do not bypass ownership or tenant isolation for convenience.

## Defaults
3. Model bounded contexts by business language and ownership, not framework package counts. A context may span multiple modules/apps; map it to existing code before proposing a new boundary.
4. Put meaningful use cases and invariants in discoverable domain/application code. Preserve simple framework CRUD where it is sufficient; services and selectors are conventions, not mandatory pass-through layers.
5. Keep domain terms consistent with the existing glossary; update it when introducing a substantive new concept.

## Conditional patterns
6. Aggregates identify consistency boundaries. Prefer local atomic transactions when they safely meet requirements; a cross-aggregate update does not automatically require asynchronous events. Explain coordination and failure semantics when boundaries are distributed.
7. Introduce repository/unit-of-work abstractions when a real domain/testing boundary benefits; do not wrap an ORM mechanically.
8. Use immutable validated value types when their semantics warrant them, using the language's idioms rather than requiring Python dataclasses.

## Review
Who owns the rule? Where is it enforced? What prevents invalid intermediate state? Does the change introduce a boundary or abstraction without a concrete benefit?
