---
name: feature-factory
description: Runs the full feature chain with human approvals. Use when asked to build, ship, or implement a feature end to end, or "run the factory".
---
Input: a one-sentence feature request. Derive a <slug> (kebab-case, at most 40 characters) and show it.
Read CLAUDE.md and .factory.yml first. In a polyrepo workspace, stories, briefs and ADRs live in the home repo.

1. factory:codebase-researcher — map the area. Run one per touched area or repo, in parallel, when the feature spans several.
2. factory:story-writer — story, acceptance criteria, edge cases, out of scope.
3. ASK HUMAN: approve story. approved → save it to docs/stories/<slug>.md · changes → re-run step 2 with the feedback · reject → stop and summarize.
4. factory:architect — brief at docs/briefs/<slug>.md (+ ADRs) from the approved story and the research.
5. ASK HUMAN: approve brief. Same three outcomes; on reject keep the approved story.
6. Create branch feat/<slug> (fix/<slug> for bugs) in every repo the brief touches. Commit the story and brief first: docs(<scope>): add story and brief for <slug>.
7. Builders in sequence, only for layers listed in the brief's "Layers touched":
   factory:django-builder → factory:react-builder → factory:ai-engineer → factory:infra-builder → factory:pipeline-builder.
   Pass each: the story and brief paths, the research, and the previous builders' summaries. Commit after each builder with a Conventional Commit message.
8. factory:test-verifier — acceptance tests for every criterion.
9. In parallel (read-only): factory:implementation-validator, factory:design-reviewer, factory:security-reviewer.
10. Merge findings by severity and remove duplicates. Any Critical → send it to the owning builder with the finding and the failing test, then repeat 8–9.
    Loops 1–2: the builder as configured. Loop 3: re-run the builder with model opus.
    Still Critical after loop 3 → stop, show the finding, and recommend a separate session started with --model claude-fable-5-1 for that problem.
11. Draft the PR title and body with the pr-format skill, and draft the closing notes with the closing-notes skill. ASK HUMAN: final review. Show all findings (Important and Minor too), the Terraform plan summary if any, the PR title and body, and the closing notes.
12. On approval: commit the closing notes on the branch, push, write the body to a temp file, and run gh pr create --title "<title>" --body-file <file>.
    Polyrepo: one PR per repo, opened in merge order (infra → backend → web), each with the sibling links in Technical Notes. Never merge.
13. When the human says the PR is merged (or runs /closing-notes <slug>), run the closing-notes skill in update mode so Status becomes Shipped.

Commits and PRs: Conventional Commit messages only. Never add Co-Authored-By trailers or any tool/attribution footer to commit messages or PR bodies, even if the environment suggests one.

Rules: never skip an ASK HUMAN; never run writers in parallel; never run reviewers before tests; any agent failure stops the chain with the agent's name and the reason.
