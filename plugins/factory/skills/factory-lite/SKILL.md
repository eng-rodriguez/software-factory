---
name: factory-lite
description: Lightweight chain for bug fixes and small changes. Use for fix, tweak, small change, or when the user says "lite".
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.

Use the change-scope skill throughout. Pass the approved plan and pre-implementation commit to the builder and reviewers.

1. factory:codebase-researcher on the area. Show the map and a 3–5 line plan including the scope boundary. ASK HUMAN: go?
2. The builder that owns the layer (django, react, infra or pipeline). For bugs, write the failing test first.
3. In parallel: factory:implementation-validator (against the plan) and factory:security-reviewer. Supply both with the current implementation diff and check results, including scope evidence for failures.
4. Classify failed checks and findings using change-scope. Fix only in-scope test failures and Critical findings, in one repair round total, then rerun the affected checks and reviews. Defer unrelated findings; uncertain findings or dependencies that prevent verification pause for a scope decision. If in-scope failures or Critical findings remain after the repair round, stop and report them; new findings do not restart the loop.
5. Show actual check results and deferred findings, 3–5 short manual "How to verify" steps with expected results, and offer to open a PR written with the pr-format skill. Offer the closing-notes skill when the change is user-visible or the human asks.
