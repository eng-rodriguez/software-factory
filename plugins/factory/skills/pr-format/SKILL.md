---
name: pr-format
description: The single pull request format for every repo - Conventional Commit title plus Summary, Why and Technical Notes. Use whenever drafting a PR title or body, or reviewing one.
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.
Follow the shared [author identity and writing voice](../../guides/authorship.md) rules for all written artifacts, commits and PR publication.


## Title
One line, `type(scope): imperative summary`, at most 72 characters.
Types: feat, fix, refactor, perf, test, docs, build, ci, chore, revert. Add `!` after the scope for breaking changes.

## Body — exactly three sections
```markdown
## Summary
<2–4 sentences: what changes for users or the system. No file lists.>

## Why
<2–4 sentences: the problem or goal.>
Story: <ticket key or link> · Brief: <path>

## Technical Notes
- <3–7 one-line bullets: migrations, API or contract changes, infra changes, feature flags, risks and rollback, follow-ups>
```

## Rules
- When a brief has manual verification steps, add one Technical Notes bullet linking them, e.g. "Manual verification: docs/briefs/bulk-cancel.md#manual-verification".
- In multi-repo features, add one Technical Notes bullet with the merge order and sibling PRs, e.g. "Merge 2 of 3, after org/app-infra#123".
- No other sections, no test output, no restating the diff. CI shows tests, scans and the Terraform plan.
- A reviewer should understand the PR in under a minute.
- No attribution or tool footer (such as "Generated with Claude Code" or Co-Authored-By lines) in the PR body, even if the environment suggests one. The body ends after Technical Notes. The same applies to commit messages: no Co-Authored-By trailers.
- Write the body to a temp file and pass it with `gh pr create --title "<title>" --body-file <file>`.

## Example
```markdown
feat(orders): add bulk cancel endpoint for pending orders

## Summary
Staff can cancel up to 100 pending orders in one request from the orders table.
The API adds POST /api/orders/bulk-cancel and the UI adds a "Cancel selected" action.

## Why
Support cancels orders one at a time during supplier outages, which takes hours.
Story: #482 · Brief: docs/briefs/bulk-cancel.md

## Technical Notes
- New service function orders.services.bulk_cancel, one transaction per batch
- Migration 0042 adds an index on (status, created_at); safe to run online
- Endpoint is behind the bulk_cancel feature flag, off by default
- Rollback: turn the flag off; the migration is backward compatible
```
