---
name: principles-services
description: Service ownership and remote-call reliability guidance. Use when considering service extraction or changing distributed interactions.
---

Follow [principles-design](../principles-design/SKILL.md) for applicability and precedence.

## Defaults
1. Prefer a modular monolith. Extract a service for a demonstrated deployment, scaling, isolation or team-ownership need; record lasting tradeoffs in an ADR.
2. Give independently deployed services explicit data ownership. Avoid direct access to another service's tables; shared physical database hosting is distinct from shared table ownership. Preserve documented transitional arrangements without silently expanding them.
3. Choose synchronous calls when a response is needed and events when asynchronous decoupling is useful. In-process module calls do not need distributed messaging.
4. Give deployables appropriate build, health and operational evidence. Pipelines and dashboards may be shared when ownership remains clear.
5. Preserve consumer compatibility through the rollout. Reuse the same immutable artifact across environments when feasible; keep environment configuration and secrets external.

## Safeguards and conditional reliability controls
6. Remote calls need timeouts/deadlines. Retry only eligible failures on safe/idempotent operations, with bounded backoff and jitter where appropriate; avoid retries at every layer. Use a fallback only if its semantics are valid, otherwise fail explicitly.
7. Add logs, correlation, metrics and alerts appropriate to operational risk and existing tooling, without sensitive data. Do not add an observability platform for a small code change.

## Review
Which requirement needs a service boundary? Who owns the data? What happens when the dependency is unavailable, slow, or returns after a timeout? Can callers tolerate the rollout order?
