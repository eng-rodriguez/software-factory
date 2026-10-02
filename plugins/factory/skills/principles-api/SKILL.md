---
name: principles-api
description: HTTP API rules from API Design Patterns, applied to DRF and generated React clients. Use when designing or reviewing endpoints, serializers, errors, pagination, versioning, or frontend API usage.
---

## Rules
1. Resource-oriented URLs with standard methods; custom actions only as `POST /resource/{id}:action`-style verbs when CRUD doesn't fit.
2. Cursor pagination on every list endpoint, with a max page size.
3. One error shape everywhere: `{"error": {"code", "message", "details"}}`.
4. Idempotency keys on POSTs that create or charge.
5. Partial updates via PATCH with explicit field masks or serializer partial mode.
6. Versioning policy documented; additive changes only within a version.
7. The OpenAPI schema (drf-spectacular) is the contract; frontend types are generated from it.
8. Permissions are part of the contract: document who may call each endpoint and what a denied caller sees (403 vs 404).

## Review questions
- Is every new list endpoint paginated with a capped page size?
- Do all errors follow the single error shape, with stable machine-readable codes?
- Is this change additive, or does it break an existing client?
- Was the frontend client regenerated from the updated schema?

## Precedence
See principles-design → Precedence when a rule here conflicts with another book.
