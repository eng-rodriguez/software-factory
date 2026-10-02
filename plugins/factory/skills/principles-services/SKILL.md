---
name: principles-services
description: Service boundary rules from Building Microservices. Use when deciding whether to extract a service, designing cross-context communication, contracts, deployables, or reviewing infra and pipeline changes that add services.
---

## Rules
1. Default to a modular monolith. Extract a service only for independent deployability, scaling, or team ownership; record the reason in an ADR.
2. A service owns its data. No shared databases, no reading another service's tables.
3. Prefer asynchronous events for cross-context notifications; use synchronous calls only when the caller needs the answer now, with timeouts and retries.
4. Each deployable has its own pipeline, image, health checks and dashboards.
5. Contracts are versioned; consumers never break on deploy (expand, migrate, contract).
6. Every synchronous call has a timeout, bounded retries with backoff, and a defined fallback.
7. Services are observable from day one: structured logs, request IDs propagated across calls, metrics for latency, errors and saturation.
8. Configuration comes from the environment; the same image runs in every environment.

## Review questions
- Which driver (deployability, scaling, ownership) justifies a new service, and which ADR records it?
- Does any component read or write data it does not own?
- What happens to callers when this dependency is slow or down?
- Can this change deploy without coordinating a release with another deployable?

## Precedence
See principles-design → Precedence when a rule here conflicts with another book.
