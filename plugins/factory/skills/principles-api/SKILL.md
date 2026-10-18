---
name: principles-api
description: API contract, authorization and compatibility guidance independent of backend or frontend framework. Use for HTTP endpoint or client contract changes.
---

Follow [principles-design](../principles-design/SKILL.md) for applicability and precedence.

## Safeguards
1. Document and test authorization, tenant scoping, and denied responses; preserve intentional 403/404 information-disclosure behavior.
2. Maintain the authoritative API contract and consumers affected by a change. Preserve compatibility within the project's versioning policy; coordinate breaking changes explicitly.
3. Bound collection/resource consumption. Define duplicate-request behavior for consequential operations such as payments or retryable creation.

## Defaults
4. Follow existing resource URLs, methods, action routes and error representations. For a new API choose a consistent error shape with stable machine-readable codes; do not introduce a second style or rewrite existing routes without a requirement.
5. Use PATCH for partial updates where supported and define omission/null semantics.
6. Prefer an authoritative machine-readable contract and generated types where the project supports them. Use the existing generator and regenerate when the contract changes or output is stale, not for unrelated UI work.

## Conditional patterns
7. Choose cursor, offset or page pagination based on ordering, navigation and scale. Preserve existing client expectations; cap page sizes. A small bounded enumeration need not acquire artificial pagination.
8. Use idempotency keys, uniqueness or state transitions where needed to make retries safe. Define conflict, retention and replay behavior rather than adding keys without semantics.

## Review
Can existing clients still work? Are resource limits and denied paths tested? Did changed contracts, collections and generated consumers receive the required updates?
