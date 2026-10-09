# Changelog

## 0.6.1 - 2026-10-09

* Use the user's established Git author/committer and authenticated PR identity, with one-line Conventional Commits and no assistant/tool attribution. Verify identity before publication without inventing emails or silently changing Git configuration; disable Claude attribution in the distributed settings.
* Add selective Mermaid guidance for technical briefs and closing notes: choose diagrams by the explanation needed, keep notes audience-appropriate, verify against implemented behavior, and respect destination renderer support. Diagrams are optional when prose is sufficient.

## 0.6.0 - 2026-10-08

* Add factory CI and one local verification command for behavioral tests, distribution metadata/references, shell checks and workflow lint/security checks.
* Cover common shell guard variants, protect migrations on the configured default branch, and report unavailable base refs. Hooks remain a safety net, not a sandbox.
* Run existing project check commands in both repository and workspace mode; include dependency/config changes and distinguish skipped checks. Unexpected zero-test runs now fail by default; intentional test-free projects can explicitly configure `checks.allow_no_tests`.
* Ship pinned action references and versioned, checksum-database-verified Go tool installs. Replace the unavailable Trivy reference with the maintainer's v0.36.0 release; add an explicit pin-update command that includes templates.
* Preserve existing delivery ownership during onboarding. New Terraform delivery uses environment-specific saved plans, restricted short-lived artifacts, human plan review, signature verification before mutation, and context/checksum/expiry checks before apply. Add a recovery runbook. Existing project pipelines are not migrated automatically.
* Define risk, completion evidence and finding severity; make lite review consistent with its plan and preserve approvals/repair budgets in resumable checkpoints.
* Add seven credential-free evaluation fixtures with deterministic outcome graders and explicit human action review, including existing delivery, injected task instructions and interrupted polyrepo work. Live-client results must be recorded separately.

## 0.5.0 - 2026-10-04

* Add opt-in parent workspace mode: external project configuration and AI artifacts, with repository mode preserved for existing and unlisted projects.
* Resolve external configuration in quality hooks and check all registered repositories when a session runs at the workspace root. Reject conflicting local configuration rather than silently migrating it.
* Teach agents and workflows to keep AI artifacts outside child repositories, run checks per Git root, preserve existing CI and GitOps delivery, and avoid local-only links in PRs.

## 0.4.1 - 2026-10-04

* Scope bug fixes to the approved feature or fix and regressions it introduces. Builders, test verification and reviewers use `change-scope` to separate unrelated findings and report uncertain blockers.
* Full and lite workflows bound repair rounds across the entire run; unrelated findings never trigger repairs. Full-suite and scanner failures remain visible.
* The quality gate directs agents to classify failures before fixing them, preserving all existing checks.

## 0.4.0 - 2026-10-02

* Contract artifacts: the brief lists API collections (Postman or similar, only if the repo has one), OpenAPI schema, generated clients and API docs to update; `django-builder` updates them in place and `implementation-validator` checks them. `/onboard-project` detects and records them in CLAUDE.md.
* Manual verification: `test-verifier` adds numbered, copy-pasteable steps to the brief; the PR links them, `/factory-lite` shows "How to verify" steps, and High-risk work confirms them before the PR opens.
* Docs impact and observability sections in the brief, enforced by builders and the validator.
* `test-verifier` uses only the project's existing test tools and never adds a framework.
* Tickets from any tracker by copy and paste: `/feature-factory` and `story-writer` accept a pasted ticket and keep its key and link. `/closing-notes` prints copy-ready text and never posts to a tracker or PR.
* Dependabot template ignores major-version updates for application dependencies.

## 0.3.1 - 2026-10-02

* The factory no longer creates, changes or recommends rulesets or branch protection. They belong to the repo owner or organization, and existing ones are left alone. `/onboard-project`, `pipeline-builder`, the devsecops-gha skill, templates and USAGE.md updated.

## 0.3.0 - 2026-10-02

* New `closing-notes` skill and `/closing-notes` command: a short plain-language note per finished ticket, story or issue, written for product managers, scrum masters and leadership, saved in `docs/closing-notes/`.
* feature-factory drafts the notes at the final review and finalizes them after the merge; factory-lite offers them; onboard-project creates the folder.

## 0.2.1 - 2026-10-02

* pr-format.yml template skips Dependabot PRs, whose bodies lack the Summary / Why / Technical Notes sections.

## 0.2.0 - 2026-10-02

* Removed everything that needs a paid plan or API key: the `claude-review.yml` template, the CodeQL and dependency-review jobs in `ci.yml`, and artifact attestations in `deliver.yml`. Free scanners (gitleaks, pip-audit, npm audit, Checkov, Trivy, zizmor) stay.
* `pr-reviewer` runs locally only; `/onboard-project` no longer lists paid GitHub settings.
* `/onboard-project` no longer installs `claude-review.yml`.
* feature-factory, build-with-tests, onboard-project and pr-format forbid Co-Authored-By trailers and tool footers; USAGE.md documents the `attribution` setting.

## 0.1.3 - 2026-10-02

* pr-format: PR bodies must not end with an attribution or tool footer.

## 0.1.2 - 2026-10-02

* hooks: quote `${CLAUDE_PLUGIN_ROOT}` so hooks work when the plugin path contains spaces.

## 0.1.1 - 2026-10-02

* hooks: `changed_files` no longer prints git errors in repos without commits.

## 0.1.0 - 2026-10-02

* Initial factory: 13 agents, 18 skills, 4 hooks, 5 workflow templates, onboarding templates.
