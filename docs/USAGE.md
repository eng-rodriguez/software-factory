# Using the software factory

This plugin turns a Claude Code session into a fixed delivery chain: research → story → architecture brief → builders → acceptance tests → parallel reviewers → pull request. GitHub Actions then runs security gates and deploys. You approve at five points, and Claude never applies Terraform, touches production, or merges.

- [How it fits together](#how-it-fits-together)
- [One-time setup](#one-time-setup)
- [Onboard a repository](#onboard-a-repository)
- [Daily commands](#daily-commands)
- [The full feature chain](#the-full-feature-chain)
- [Guardrails](#guardrails)
- [Monorepos and multiple repos](#monorepos-and-multiple-repos)
- [Central workspace mode](#central-workspace-mode)
- [Choosing models](#choosing-models)
- [Keeping it sharp](#keeping-it-sharp)
- [Verify your setup](#verify-your-setup)
- [Using it with GitHub Copilot](#using-it-with-github-copilot)

## How it fits together

| Part | Lives in | Holds | Changes when |
| --- | --- | --- | --- |
| Plugin | This repo, installed once per machine | Agents, skills, principles, hooks, CI templates | You learn a lesson that applies to every project |
| Project layer | Each repo's `CLAUDE.md`, `.factory.yml`, `docs/`, `.github/` | Stack versions, commands, paths, bounded contexts, ADRs | The project changes |
| Delivery layer | GitHub Actions and repo settings | Scans, tests, Terraform plan, image signing, deploy approvals | You add a control or an environment |

The plugin is the same everywhere. Everything specific to one project lives in that project.

## No attribution lines

The factory's skills forbid `Co-Authored-By` trailers in commits and "Generated with Claude Code" footers in PRs. Claude Code can still add them by default, so also set this in `~/.claude/settings.json` (or a repo's `.claude/settings.json`):

```json
"attribution": { "commit": "", "pr": "" }
```

## Free tooling only

The factory needs no paid service. Everything it installs runs free on private repos: gitleaks, bandit, pip-audit, npm audit, Checkov, Trivy, tflint, zizmor, actionlint, OWASP ZAP and cosign keyless signing, plus Dependabot, GitHub Environments and OIDC. It does not use GitHub Advanced Security features (CodeQL, dependency review, secret scanning, artifact attestations on private repos) or a hosted AI review. The reviewer agents run locally in your Claude Code session before the PR is opened.

## One-time setup

1. **Install the plugin.**

   ```shell
   claude plugin marketplace add eng-rodriguez/software-factory
   claude plugin install factory@my-factory
   ```

   Or run `/plugin marketplace add ...` and `/plugin install ...` inside an interactive Claude Code session. Restart Claude Code afterwards.

2. **Add the deny rules.** Merge [`settings/claude-settings.json`](../settings/claude-settings.json) into `~/.claude/settings.json`. These permission rules back up the hooks: Terraform apply, kubectl and Helm writes, and force pushes are denied, and every `git push` asks first.

3. **Install the tools** the hooks and reviewers call. On macOS:

   ```shell
   brew install jq yq gh uv node terraform checkov actionlint zizmor gitleaks trivy
   brew install terraform-linters/tap/tflint
   ```

   `yq` must be v4 (mikefarah). Missing scanners are skipped locally but still run in CI.

4. **Optional:** install the Context7 MCP server so agents read docs for the exact library versions a project uses.

To confirm the install, type `@factory:` in a session; the 13 agents should appear.

## Onboard a repository

Run this once in each repo, from the repo root:

```text
/onboard-project
```

It detects the layout and commands, then shows you drafts of `.factory.yml` and `CLAUDE.md` to approve. After approval it creates:

- `docs/domain.md` (glossary and context map), plus `docs/adr/`, `docs/briefs/`, `docs/stories/` and `docs/closing-notes/`
- `.github/pull_request_template.md` and `.github/CODEOWNERS`
- `ci.yml`, `pr-format.yml`, `dependabot.yml`, and `deliver.yml` if the repo deploys

It never restructures the repo or overwrites existing workflows. Everything lands as one PR for you to review.

**After merging, configure GitHub.** The PR description lists these optional steps. The factory never creates or changes rulesets or branch protection; those belong to the repo owner or your organization, and existing ones stay as they are. If your repo already requires checks, `ci-ok` is the one job that summarizes `ci.yml`.

- [ ] Turn on Dependabot alerts and security updates (free).
- [ ] Set default workflow permissions to read-only, and stop Actions from approving PRs.
- [ ] Create environments `dev`, `staging` (main only) and `production` (main only, you as required reviewer).
- [ ] Add cloud identity IDs as variables; they aren't secrets.
- [ ] Create two OIDC identities per cloud: a read-only **plan** identity trusted from pull requests, and a **deploy** identity trusted only from the `staging` and `production` environments.
- [ ] Enable squash merging with the PR title as the commit message.
- [ ] Run `pinact run` once to pin every action to a full commit SHA.

**Keep `CLAUDE.md` short.** Aim for 100–300 lines of facts: stack, commands, paths, bounded contexts, project rules, and a "Lessons" list. General rules belong in the plugin, not here. For work repos, follow your company's AI policy. You can make `AGENTS.md` the main file and reduce `CLAUDE.md` to one line, `@AGENTS.md`.

## Daily commands

Start a fresh session for each task. The plugin, hooks and `CLAUDE.md` load automatically.

| Command | Use it for | What runs |
| --- | --- | --- |
| `/factory-lite <change>` | Bug fixes and small changes (most days) | researcher → plan (you approve) → builder → validator + security reviewer |
| `/feature-factory <feature or pasted ticket>` | New features or meaningful changes | The full chain below, with 3 approvals in the session |
| `/explore <question>` | Learning an unfamiliar codebase or area | Researcher only; writes nothing |
| `/adr <decision>` | Recording a decision made in conversation | Writes `docs/adr/NNNN-title.md` |
| `/closing-notes [slug]` | Finishing a ticket, story or issue | Writes a short plain-language note to `docs/closing-notes/` for product managers, scrum masters and leadership, and prints it ready to paste into your ticket tracker. It never posts anywhere itself |
| `/onboard-project` | First use in a repo | See above |

Examples:

```text
/factory-lite fix: order totals ignore discounts when the cart has a gift card
/feature-factory staff can cancel up to 100 pending orders at once from the orders table
/explore how does tenant isolation work in the billing app?
/adr we will publish order events through a transactional outbox instead of calling Celery directly
```

You can also call an agent directly with `@factory:<name>`, for example `@factory:security-reviewer review my staged changes`.

**For bugs**, `/factory-lite` writes a failing test before the fix. When it finishes, it shows a few manual "How to verify" steps and offers to open a PR.

**Bug-fix scope.** Both workflows fix defects in the agreed feature or fix and regressions caused by its implementation. Existing unrelated bugs, even Critical ones or bugs in touched files, are reported separately and do not trigger repair loops. A pre-existing bug explicitly targeted by the task remains in scope. Uncertain failures or existing defects that block the work are reported for a scope decision. Required checks still run and their actual failures remain visible; the factory does not weaken checks to get green results. `/factory-lite` allows one repair round total.

**Tickets from Jira, GitHub or Linear.** The factory has no tracker integration. Paste the ticket text after the command (`/feature-factory` followed by the pasted ticket). Its key and link carry through to the story, the PR's Why section and the closing notes. When the work is done, paste the closing notes back into the ticket.

## The full feature chain

`/feature-factory` runs these steps. The steps marked **you** stop and wait for your answer.

1. **Research.** `codebase-researcher` maps the relevant code, patterns and risks.
2. **Story.** `story-writer` drafts a user story, acceptance criteria, edge cases and what is out of scope. If you pasted a ticket, it keeps the ticket's key and link and flags gaps as questions.
3. **You approve the story.** Reply approved, ask for changes, or reject. Once approved, it is saved to `docs/stories/<slug>.md`.
4. **Brief.** `architect` writes `docs/briefs/<slug>.md`, covering which layers are touched, the domain model, the API contract, data consistency, security threats, required tests, contract artifacts to update (API collections such as Postman, OpenAPI schema, generated clients, API docs), docs impact, observability, and which files will change. Significant decisions get an ADR.
5. **You approve the brief.** This is the most valuable review: every builder after it follows the brief.
6. **Branch.** It creates `feat/<slug>` and commits the story and brief first.
7. **Build.** Only the builders for the touched layers run, one after another: django → react → ai → infra → pipeline. Each one commits its work.
8. **Acceptance tests.** `test-verifier` writes at least one test for every acceptance criterion, using only the test tools the project already has. It also adds a **Manual verification** section to the brief: numbered, copy-pasteable steps with expected results.
9. **Review.** `implementation-validator`, `design-reviewer` and `security-reviewer` run in parallel and read only.
10. **Fix loop.** Only test failures and Critical findings within the approved scope, including regressions caused by the change, go back to the owning builder. The full run allows at most 3 repair rounds; new findings do not reset the count. On the third attempt the builder runs on Opus. If blockers remain, the chain stops and recommends a separate session on a stronger model.
11. **You do the final review.** You see every finding, the Terraform plan summary, the drafted PR title and body, the closing notes, and the manual verification steps. For High-risk work you run those steps and confirm before the PR opens.
12. **PR.** It commits the closing notes, pushes and opens the PR. It never merges.
13. **After the merge.** Tell Claude the PR is merged, or run `/closing-notes <slug>`, and the note's status changes to Shipped. Copy the printed note into your tracker.

Because the story and brief are files, a later session or a colleague can pick the work up from `docs/`.

**After the PR opens:**

- `ci.yml` runs the gates: secrets (gitleaks), Python and web tests with dependency audits, IaC scans, a Terraform plan posted as a PR comment, container scan, workflow lint, and a scope check that every changed file appears in the brief.
- **You merge.**
- `deliver.yml` then builds the image once, scans it, generates an SBOM, signs it, deploys to staging by digest, smoke-tests it and runs a DAST scan. It waits for **your approval** before deploying the same digest to production.

**PR format.** Every PR uses a Conventional Commit title of at most 72 characters, plus three sections: **Summary**, **Why** and **Technical Notes**. `pr-format.yml` fails the PR when the format is wrong. Dependabot PRs are exempt.

**Stacked work.** While PR A is in review, you can branch B from A and start the next feature: one feature per PR.

## Guardrails

Hooks run on every tool call, inside all agents, and the model cannot override them.

| Hook | Runs | Blocks or does |
| --- | --- | --- |
| `guard-bash` | Before every shell command | Terraform apply/destroy/import/state, kubectl and Helm writes, prod kube contexts, Azure/AWS CLI writes, force pushes, pushes to main, commits of secret-looking files (plus gitleaks), `rm -rf /` |
| `guard-files` | Before every file edit | `.env*`, keys, `*.tfvars`, `*.tfstate`, kubeconfig, `.terraform.lock.hcl`, and migrations already on main |
| `format` | After every file edit | Formats the edited file with ruff, the project's own Prettier, or `terraform fmt` |
| `quality-gate` | When Claude tries to finish | Lint, typecheck and fast tests for the areas the branch touched. Failures are classified by scope: repair in-scope defects within the workflow limit, report unrelated failures, and stop on uncertain blockers |

**When a guard fires**, Claude sees `BLOCKED by factory guard: <reason>` and has to change approach. If the blocked action really is needed (for example a Terraform apply), it happens in CI with your approval, or you run it yourself outside Claude.

**Limits.** The guards match patterns, so they are a safety net, not a sandbox. They also can't tell which agent made an edit, so "backend paths only" is enforced by the validator's file check and the CI `scope` job. Keep your cloud CLIs logged in with read-only roles.

## Monorepos and multiple repos

`.factory.yml` at the repo root tells the hooks and orchestrators where things are:

```yaml
layout: monorepo
default_branch: main
areas:
  backend: { path: backend, stack: django }
  web:     { path: web, stack: react }
  infra:   { path: infra, stack: terraform }
  deploy:  { path: deploy, stack: helm }
```

**Monorepo:**
- Start one session at the root.
- Each area can have its own `CLAUDE.md`; keep the root one under 100 lines.
- Each feature becomes one PR. CI runs only the jobs for changed paths, and `ci-ok` summarizes them in one job.

**Multiple repos:**
- Set `layout: polyrepo` in every repo.
- Mark one repo `home: true` and list its siblings under `repos:`. Stories, briefs and ADRs live in the home repo.
- Put all clones in one workspace folder, start in the home repo, and add the others with `claude --add-dir ../app-web ../app-infra`.
- A feature becomes one PR per repo, all on the same branch name, opened in merge order: infra → backend → web.
- The backend publishes a versioned API schema, and the frontend generates its client from that published version.

Without `.factory.yml`, the hooks fall back to common defaults (`manage.py` or `backend/`, plus `web/`, `infra/` and `deploy/`).

## Central workspace mode

Use this opt-in mode when AI instructions and planning artifacts must stay outside application repositories. Existing installations remain in repository mode; updating the plugin does not create a workspace manifest or migrate any project.

```text
repo/                         # Open this folder in VS Code; start the CLI here
  .github/copilot-instructions.md
  .factory/
    workspace.yml
    projects/
      stratium-api.yml
      stratium-api.md          # Project instructions, commands, contract paths
      stratium-frontend.yml
      stratium-iac.yml
      stratium-gitops.yml
    stories/
    briefs/
    adr/
    reviews/
    closing-notes/
  software-factory/           # Optional local plugin source
  stratium-api/               # Independent Git repositories
  stratium-frontend/
  stratium-iac/
  stratium-gitops/
```

Only explicitly listed repositories use workspace mode. The parent folder does not need to be a Git repository. Keep project paths as direct child directory names; nested layouts and symlinked projects/configuration are not supported.

To onboard, install the plugin in your client, open/start at `repo/`, then ask:

```text
/onboard-project Set up centralized workspace mode for stratium-api,
stratium-frontend, stratium-iac and stratium-gitops. All AI configuration,
instructions and planning artifacts must live in this parent folder.
Inspect the repositories read-only and show the parent configuration drafts.
Preserve existing CI and the GitOps release process.
```

This branch of onboarding creates only parent files after draft approval. It does not run the repository onboarding steps that create branches, workflows, CODEOWNERS, docs or PRs. Do not onboard from a child directory if your intent is to create parent workspace mode.

The manifest at `.factory/workspace.yml` is:

```yaml
version: 1
mode: workspace
projects:
  stratium-api: { path: stratium-api }
  stratium-frontend: { path: stratium-frontend }
  stratium-iac: { path: stratium-iac }
  stratium-gitops: { path: stratium-gitops }
```

Each listed project must have `.factory/projects/<id>.yml`. For example, for a Django API with an existing `make check` target:

```yaml
layout: polyrepo
default_branch: main
areas:
  backend: { path: ., stack: django }
commands:
  check: make check
```

Use actual project commands and branches. `commands.check` is optional trusted shell configuration: it runs from that project's Git root when the project has changes. It replaces the default stack checks, so it must cover the project's full local lint/type/test requirements. The hook still runs its workflow linters for changed GitHub Actions files. Without it, existing area-based checks apply. GitOps projects should record their existing Helm/Kustomize validation command because there is no generic GitOps check in the default gate.

Store other project facts in `.factory/projects/<id>.md`. Parent Copilot instructions should identify the manifest, require the workspace-context skill, prohibit AI files in children, and require each Git/check command to run in the owning repository. Agent/model definitions remain in the shared plugin or parent `.github/agents`; no project-specific copies are needed. Use model identifiers supported by your Copilot client; this feature does not translate model aliases or tool definitions between clients.

For a cross-repository feature, invoke `/feature-factory` from the parent and name the affected projects. The factory passes absolute project and artifact paths to agents, records a baseline per repository, and creates one branch/PR per changed repository. Stories, briefs, ADRs, closing notes and written review reports stay in `.factory/` and are not committed to application repositories. Normal application code, tests, API contracts and user-facing documentation still belong in their repositories. Merge order follows actual dependencies, including GitOps reconciliation.

The Stop hook checks every registered repository when the session directory is the workspace root. From a registered child, it checks that child only. Unlisted repositories retain repository-mode configuration. Parent sessions do not automatically check unlisted repositories. Hook commands honor the runtime's `cwd`; verify your client actually loads the hooks and supplies compatible payloads before relying on them. The guards remain pattern-based and do not provide a filesystem sandbox.

**Existing installations:** a listed child containing `.factory.yml` is a configuration conflict, not an implicit migration. Leave it out of the manifest to retain its existing behavior. Migration requires a separate explicit request to move its AI context/artifacts and review any pipeline dependencies; onboarding never deletes those files for you.

**CI and sharing:** local external briefs are unavailable on GitHub runners. Scope review runs locally against each repository's section of the brief; preserve existing CI checks and never claim CI validated the external brief. If an existing required check needs an in-repository brief, report the policy conflict instead of disabling it. PRs use shared ticket/document links when available; otherwise identify the brief as local and summarize decisions/manual verification without broken local links. Do not automatically publish external artifacts. Teammates need their own central configuration or an approved shared distribution of it.

Developer verification (requires Git, Bash, jq and yq v4):

```shell
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

## Choosing models

Each agent's model is set in its file:

| Model | Used by |
| --- | --- |
| Haiku | `codebase-researcher`, i.e. cheap read-only scouting |
| Sonnet | Story writer, all builders, test-verifier, validator, design and PR reviewers |
| Opus | `architect` and `security-reviewer`, where a wrong call multiplies downstream; also the third fix loop |
| Fable 5.1 | On demand only. Use it for large cross-layer refactors, system-level design, or bugs Opus could not fix. Start a separate session with `claude --model claude-fable-5-1`, then switch back |

**Keep `security-reviewer` on Opus.** Fable carries extra cybersecurity safeguards that can limit vulnerability analysis.

**Habits that save the most tokens:**
- Use `/factory-lite` by default.
- Start one session per task, and use `/clear` between unrelated tasks.
- Keep `CLAUDE.md` short.
- Don't edit `CLAUDE.md`, skills or agents mid-session: it breaks prompt caching.
- Use medium effort unless a task is hard.
- Check `/cost` monthly. Move an agent down a tier if its findings never change, and up a tier if its fix loops keep failing.

## Keeping it sharp

Every time the AI surprises you, add a rule in exactly one place:

| Surprise | Fix it in |
| --- | --- |
| A wrong fact about this project | The project's `CLAUDE.md` → Lessons |
| A design principle was broken | The principle skill's rules, or the precedence table in `principles-design` |
| An agent did the wrong job or returned messy output | That agent's file |
| A dangerous command got through | `guard-bash.sh`, plus a deny rule in settings |
| A vulnerability reached a PR | The `security-reviewer` checklist, plus a CI scanner rule |
| A vulnerability reached main | A new required CI job |

Lessons from work projects should be rewritten as general rules before they go into the plugin. Never copy proprietary details into it. To release a change to the factory, see [Changing the factory](../README.md#changing-the-factory). Once a month, re-read the whole plugin and delete rules that no longer earn their place.

## Verify your setup

Run these once after setup. Each should produce the stated result.

- [ ] Ask Claude to run `terraform apply`: guard-bash blocks it and gives a reason.
- [ ] Ask it to edit `.env`: guard-files blocks it.
- [ ] Stage a fake AWS key and ask for a commit: gitleaks blocks it locally, and the CI secrets job would catch it on the PR.
- [ ] Add a failing test and let the session end: the Stop hook keeps Claude working.
- [ ] Open a PR that adds `uses: some/action@main`: zizmor fails CI.
- [ ] Open a PR with a vulnerable dependency: pip-audit or npm audit fails.
- [ ] Open a PR with a public storage account in Terraform: Checkov fails, and the plan comment shows the change.
- [ ] Run `/factory-lite` on a small bug: you get the research map, an approval prompt, a fix with a test, and two reviewer reports.
- [ ] Run `/feature-factory` on a tiny feature: you approve the story and brief, the brief is saved, and a PR opens.
- [ ] Merge: the image is signed (`cosign verify` passes), staging deploys by digest, and production waits for your approval.

## Using it with GitHub Copilot

The same repo installs into Copilot CLI and VS Code agent plugins:

```shell
copilot plugin marketplace add eng-rodriguez/software-factory
copilot plugin install factory@my-factory
```

Compatibility is good but not identical. Run the checklist above inside Copilot before trusting it, and check these in particular:

- **Agents don't load.** Copilot may not understand the model aliases or the `skills` preload field. Create a `.github/agents/<name>.agent.md` twin with Copilot's model and tool names, and keep the prompt the same.
- **Hooks don't block.** Confirm the hook input fields and that exit code 2 blocks the call.
- **`/feature-factory` can't call other agents.** Run each phase as its own prompt file instead.
- **Your organization blocks plugin marketplaces.** Copy the agents, skills and hooks into the work repo's `.github/`.

If your company already has review bots or release pipelines, the factory should feed into them. Don't run a parallel Claude review in CI unless it's approved.
