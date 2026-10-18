---
name: principles-data
description: Data correctness, migrations, retries and consistency guidance. Use for persistent state, background work, events, caches or query changes.
---

Follow [principles-design](../principles-design/SKILL.md) for applicability and precedence.

## Safeguards
1. Define duplicate execution and partial-failure behavior for side effects. Use idempotency keys, constraints, transactions or state checks as appropriate; do not blindly retry unsafe operations.
2. Identify the source of truth and how derived copies recover. State the consistency model when it affects behavior.
3. Preserve data and compatibility during migrations. Validate the versions that must coexist during the actual rollout and recovery window.

## Defaults
4. Store instants consistently, normally UTC; preserve timezone and civil-time semantics for recurring schedules or date-only domain values. Do not use untrusted client timestamps as authoritative ordering.
5. Choose indexes from access patterns and inspect query plans for meaningful query changes using representative data. Do not invent performance measurements.
6. Batch long backfills, make them resumable, and bound transaction duration. Assess database-specific locking; do not promise that no locks occur.

## Conditional patterns
7. Use an outbox or equivalent durable publication mechanism when committed state must reliably produce external messages. In-process notifications and best-effort telemetry do not automatically require an outbox. Document delivery guarantees and consumer deduplication when applicable.
8. Use expand/backfill/contract across deployments when old/new application versions must coexist. A safe additive migration does not require unnecessary release stages; destructive changes need an explicit recovery decision.

## Review
What happens on duplicate execution or a crash between steps? Can required versions coexist? Can a failed backfill resume? What evidence supports query and locking expectations?
