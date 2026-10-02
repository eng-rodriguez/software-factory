---
name: principles-domain
description: Domain modeling rules from DDD and Architecture Patterns with Python, adapted to Django. Use when designing models, aggregates, bounded contexts, services, or when reviewing where business logic lives.
---

## Rules
1. One Django app = one bounded context. Name it in the ubiquitous language.
2. No cross-context model imports. Contexts call each other's service functions or consume events.
3. Business rules live in services.py (writes) or model methods that guard invariants. Never in views, serializers or React.
4. Reads that span tables go in selectors.py and return plain data, not querysets leaked to views.
5. An aggregate is the unit of consistency: one transaction changes one aggregate. Cross-aggregate updates go through events.
6. Repository + Unit of Work only in core domains whose logic is complex enough to unit-test without the database.
7. Value objects (money, email, date ranges) are immutable dataclasses with validation.
8. Name things from the domain glossary in docs/domain.md; add new terms there first.

## Review questions
- Which bounded context owns this change? Does it reach into another one?
- Which invariant does each aggregate protect, and where is it enforced?
- Could a new developer find this rule by reading services.py?

## Precedence
See principles-design → Precedence when a rule here conflicts with another book.
