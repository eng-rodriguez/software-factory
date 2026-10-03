---
name: build-with-tests
description: Use when implementing or extending a feature. Reads CLAUDE.md and the brief, matches existing patterns, writes code with tests alongside, runs the project's quality commands. Triggers on build, implement, add, extend, fix.
---
1. Read CLAUDE.md and the approved brief. Stay inside the brief's "Files that will change".
2. Find 2–3 similar features; copy their layout, naming, error handling and test style.
3. Work in small steps: production code → test → run that test.
4. Cover success, validation failure, permission failure, and one edge case per behavior.
5. Update the docs and contract artifacts the brief lists, and add the logging it asks for.
6. Finish with the full quality commands from CLAUDE.md (lint, typecheck, tests, security lint).
7. Return: files changed, patterns reused, docs and contract artifacts updated, commands run with pass/fail, suggested CLAUDE.md rules.
Commit messages are Conventional Commits with no Co-Authored-By trailer or tool footer.
Rules: no unrelated refactors, no new dependencies without approval, stop and report on conflict.
