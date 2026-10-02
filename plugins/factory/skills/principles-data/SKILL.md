---
name: principles-data
description: Data system rules from Designing Data-Intensive Applications. Use when touching models, migrations, side-effecting endpoints, background jobs, events, caches, indexes, or when reviewing consistency and idempotency.
---

## Rules
1. Every side-effecting endpoint and job is idempotent: idempotency key, unique constraint, or state check.
2. Publish events with the transactional outbox pattern, never "save then publish".
3. Migrations are backward compatible: add nullable → backfill → enforce → remove old, across separate deploys.
4. State the consistency model of each feature (strong, read-your-writes, eventual) in the brief.
5. Name the source of truth for each piece of data; caches and search indexes are derived.
6. Time is UTC in storage; convert at the edges. Never trust client clocks for ordering.
7. Know the access pattern before adding an index; check query plans for new list endpoints.
8. Long backfills run in batches outside the request path, are resumable, and never hold a table lock.

## Review questions
- What happens if this request or job runs twice? If it crashes halfway?
- Can the old version of the code run against the new schema, and the new code against the old one?
- Where is the source of truth, and how do derived copies catch up?
- Which query plan does the new list endpoint produce at 100× today's rows?

## Precedence
See principles-design → Precedence when a rule here conflicts with another book.
