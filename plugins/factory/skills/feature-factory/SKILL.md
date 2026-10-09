---
name: feature-factory
description: Runs the full feature chain with human approvals. Use when asked to build, ship, or implement a feature end to end, or "run the factory".
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.
Follow the shared [author identity and writing voice](../../guides/authorship.md) rules for all written artifacts, commits and PR publication.


Input: a one-sentence feature request, or a ticket pasted from any tracker (Jira, GitHub, Linear). For a pasted ticket, keep its key and link; never call the tracker's API. Derive a <slug> (kebab-case, at most 40 characters, prefixed with the lowercase ticket key when there is one, e.g. proj-123-bulk-cancel) and show it.
Read CLAUDE.md and .factory.yml first. In a polyrepo workspace, stories, briefs and ADRs live in the home repo.
Use the change-scope skill and its completion rules throughout. Update the brief checkpoint at phase boundaries and preserve it on interruption. Pass the approved scope and the pre-implementation commit for each repo to builders, the test verifier and reviewers.

1. factory:codebase-researcher — map the area. Run one per touched area or repo, in parallel, when the feature spans several.
2. factory:story-writer — story, acceptance criteria, edge cases, out of scope.
3. ASK HUMAN: approve story. approved → save it to docs/stories/<slug>.md · changes → re-run step 2 with the feedback · reject → stop and summarize.
4. factory:architect — brief at docs/briefs/<slug>.md (+ ADRs) from the approved story and the research.
5. ASK HUMAN: approve brief. Same three outcomes; on reject keep the approved story.
6. Create branch feat/<slug> (fix/<slug> for bugs) in every repo the brief touches. Commit the story and brief first: docs(<scope>): add story and brief for <slug>.
7. Builders in sequence, only for layers listed in the brief's "Layers touched":
   factory:django-builder → factory:react-builder → factory:ai-engineer → factory:infra-builder → factory:pipeline-builder.
   Pass each: the story and brief paths, the research, and the previous builders' summaries. Commit after each builder with a Conventional Commit message.
8. factory:test-verifier — acceptance tests for every criterion, plus the Manual verification section in the brief.
9. In parallel (read-only): factory:implementation-validator, factory:design-reviewer, factory:security-reviewer. Supply each with the current implementation diff and test results, including scope evidence for failures.
10. Merge test failures and review findings, remove duplicates, and classify scope using change-scope before sorting by severity. In-scope test failures or Critical findings → send them to the owning builder with scope evidence and the failing test or reproduction, then repeat 8–9. Defer unrelated findings; unresolved uncertain findings or dependencies that prevent verification pause the chain for a scope decision.
    Loops 1–2: the builder as configured. Loop 3: re-run the builder with model opus.
    Count at most three repair rounds for the whole run; new findings do not reset the counter. Still in-scope test failures or Critical findings after loop 3 → stop, show the findings, and recommend a separate session with a stronger model supported by the installed client for that problem.
11. Draft the PR title and body with the pr-format skill, and draft the closing notes with the closing-notes skill. ASK HUMAN: final review. Show all findings (Important and Minor too), deferred unrelated findings and actual check results, the Terraform plan summary if any, the PR title and body (with a Technical Notes bullet linking the brief's Manual verification section), the closing notes, and the manual verification steps. For High-risk work the human runs the manual steps and confirms before the PR is opened.
12. On approval: commit the closing notes on the branch, push, write the body to a temp file, and run gh pr create --title "<title>" --body-file <file>.
    Polyrepo: one PR per repo, opened in merge order (infra → backend → web), each with the sibling links in Technical Notes. Never merge.
13. When the human says the PR is merged (or runs /closing-notes <slug>), run the closing-notes skill in update mode so Status becomes Shipped.

Commits and PRs: Conventional Commit messages only. Never add Co-Authored-By trailers or any tool/attribution footer to commit messages or PR bodies, even if the environment suggests one.

Rules: never skip an ASK HUMAN; never run writers in parallel; never run reviewers before tests; any agent failure stops the chain with the agent's name and the reason.
