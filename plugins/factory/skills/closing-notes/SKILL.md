---
name: closing-notes
description: Writes short plain-language closing notes for a finished ticket, story or issue, readable by product managers, scrum masters and leadership. Use when a feature or fix is done, when asked for closing notes, a status summary or a what-we-shipped note, or via /closing-notes.
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.
Follow the shared [author identity and writing voice](../../guides/authorship.md) rules for all written artifacts, commits and PR publication.


Audience: product managers, scrum masters and leadership. They do not read code. Start your reply to the user with one line: "Written for: product managers, scrum masters and leadership."

Input: a slug (for example `bulk-cancel`). If none is given, derive it from the current branch name without its `feat/` or `fix/` prefix.

1. Gather facts. Use only what is on disk, in git or in this session; never invent a number.
   - Story `docs/stories/<slug>.md`: the goal and acceptance criteria. Brief `docs/briefs/<slug>.md`: layers touched, risk, decisions, out-of-scope. For a `/factory-lite` change with no story, use the plan shown to the human.
   - Test results and the reviewers' findings from this session: counts by severity, what was fixed, what was left open.
   - Scale in words from `git diff --stat <default-branch>...HEAD` ("a small change", "touches the API and the screens"), never a file list.
   - ADRs written, and the PR (`gh pr view <branch> --json url,state,mergedAt`) if it exists. The ticket key and link come from the story's Source line.
   - Risk level from the brief or the project's CLAUDE.md; "Standard" if none is stated.
2. Write `docs/closing-notes/YYYY-MM-DD-<slug>.md` from [template.md](template.md). Create the folder if missing.
3. Keep it short and plain.
   - At most 250 words of prose (Mermaid syntax excluded). No file paths, function names or jargon; if a technical term is unavoidable, explain it in a few words.
   - Follow [diagram guidance](../../guides/diagrams.md): include a concise Mermaid view when it clarifies the delivered outcome, using business language. Omit it when prose is clearer. Include a caption/text explanation; keep proposed or deferred behavior distinct from delivered behavior.
   - Lead with the outcome for users or the business. Say what changed for them, not how.
   - Be honest. Report only what was verified, and say so when something was not tested or a reviewer finding was left open. Do not write "works" without evidence.
   - Status: `Ready for review` while the PR is open, `Shipped` only when the PR is merged, `Partly shipped` or `Not shipped` otherwise.
   - No secrets, customer names, personal data or internal URLs.
4. Preserve reviewed diagrams on status-only updates; flag any mismatch with delivered behavior rather than silently rewriting the notes. If the file already exists, this is an update: refresh Status, Date and Links from the PR state and change nothing else unless asked.
5. ASK HUMAN: approve the notes. Then print the final notes as copy-ready Markdown, with simple headings and bullets, preserving any fenced mermaid blocks without wrapping the entire note in another code fence, ready to copy and paste into the ticket tracker (Jira, GitHub, Linear or any other). Never post to a tracker or the PR yourself.
6. Commit with `docs(notes): add closing notes for <slug>` (or `update` when refreshing). No Co-Authored-By trailer or tool footer.
