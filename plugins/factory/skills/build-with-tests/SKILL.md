---
name: build-with-tests
description: Use when implementing or extending a feature. Reads CLAUDE.md and the brief, matches existing patterns, writes code with tests alongside, runs the project's quality commands. Triggers on build, implement, add, extend, fix.
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.
Follow the shared [author identity and writing voice](../../guides/authorship.md) rules for all written artifacts, commits and PR publication.


1. Read CLAUDE.md, the approved brief (or approved /factory-lite plan), and the change-scope skill. Stay inside the agreed scope and file boundaries; report necessary additions before expanding them.
2. Find 2–3 similar features; copy their layout, naming, error handling and test style.
3. Work in small, testable increments. For bugs establish a failing regression first when feasible; report when reproduction is unavailable. For new behavior add relevant tests alongside implementation. For infrastructure/pipelines use [artifact-specific evidence](../../guides/verification.md), not artificial application tests.
4. Cover meaningful success/failure boundaries for the change, including authorization where applicable. Avoid adding unrelated tests or tests that only restate configuration.
5. Update the docs and contract artifacts the brief lists, and add the logging it asks for.
6. Finish with the full quality commands from CLAUDE.md (lint, typecheck, tests, security lint). Classify failures with change-scope before fixing them; report unrelated failures separately without repairing them.
7. Return: files changed, patterns reused, docs and contract artifacts updated, commands run with pass/fail, suggested CLAUDE.md rules.
Commit messages are Conventional Commits with no Co-Authored-By trailer or tool footer.
Rules: no unrelated refactors, no new dependencies without approval, stop and report on conflict.
