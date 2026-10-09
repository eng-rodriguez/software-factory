# Software Factory assessment — 2026-10-08

Reviewed revision: `eae345d` (plugin 0.5.0). This is an assessment, not an implementation change or a certification of deployed environments.

The architecture is appropriate for a personal software factory. Keep the lightweight workflow, bounded repairs, separate acceptance verification, human decisions, and existing project tooling. The next investment should be evidence that these controls work. More agents or more instructions would not address the most consequential gaps below.

No system can be made literally bulletproof. The practical target is bounded authority, reproducible checks, visible failures, and a tested recovery path. This fits Anthropic's recommendation to add complexity only when it improves outcomes and DORA's guidance on small, independently testable changes. [Anthropic](https://www.anthropic.com/engineering/building-effective-agents), [DORA](https://dora.dev/capabilities/working-in-small-batches/).

## What is already strong

- Full and lite workflows separate planning, implementation, and review, with explicit human decisions before publication.
- `change-scope` requires evidence before calling a failure pre-existing, preserves unrelated findings, and limits repairs to the requested work.
- Repair budgets are bounded across a run rather than reset whenever a new finding appears.
- Acceptance verification exercises public interfaces and cannot alter production code. Builders reuse existing test tooling.
- Architecture guidance covers API contracts, tenant isolation, data consistency, expand/contract migrations, documentation, and observability.
- Workspace mode has behavioral tests for configuration conflicts, isolation, path handling, and per-repository execution.
- Delivery templates use OIDC, separate planning/deployment identities, image digests, scanning, signing, and signature verification. These are good building blocks, subject to the gaps below.

## Findings and smallest useful remedies

Priorities here mean P1: address before relying on the affected safeguard for sensitive work; P2: improve reliability in the next small iteration. They are assessment priorities, not scanner severity ratings.

### 1. P1 — Shell guards do not enforce all the restrictions described in the documentation

Evidence: `plugins/factory/hooks/scripts/guard-bash.sh:12–21`. Passing command strings to the hook, without executing those commands, produced:

| Input | Hook exit | Result |
| --- | --- | --- |
| `terraform apply` | 2 | Blocked |
| `terraform -chdir=infra apply` | 0 | Allowed |
| `kubectl --namespace default delete pod example` | 0 | Allowed |
| `aws s3 rm s3://example-bucket/object` | 0 | Allowed |
| `git push origin HEAD:main` | 0 | Allowed |

These are ordinary CLI forms. The documentation already acknowledges that regex guards are not a sandbox, but also says the model cannot override the hooks. Distinguish a hook executing from its policy covering the requested action. Claude settings may provide additional restrictions; these probes establish hook behavior, not end-to-end permission bypasses.

Minimum remedy: fix common variants, add table-driven regression tests, and state the limits consistently. Keep write-capable production credentials outside the development runtime and use runtime sandbox/permission controls. Do not build a complete shell parser or keep expanding regexes in pursuit of a security boundary. Read-only reviewer prompts with unrestricted Bash are also behavioral instructions, not enforced read-only execution. OWASP recommends validating tool actions against permissions and enforcing least privilege. [OWASP](https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html).

### 2. P1 — Infrastructure approval is not bound to the production plan

Evidence: `plugins/factory/skills/devsecops-gha/templates/deliver.yml:74–92` and `:141–159`. Both deployment jobs run `terraform apply -auto-approve` before verifying the image signature. The PR plan is for `infra/envs/dev`; deployment uses environment-specific `TF_DIR` and generates a fresh plan implicitly. Approving the environment does not mean the human saw the plan that will execute.

Minimum remedy: verify the image before cloud mutations; prepare a plan for the target environment and exact revision, present it for approval, and apply that saved plan. Protect plan artifacts because they can contain sensitive state; expire them and re-plan/re-approve when stale. HashiCorp explicitly recommends reviewing a plan before automated apply. [Terraform apply reference](https://developer.hashicorp.com/terraform/cli/commands/apply).

The template also needs a concrete recovery procedure: previous known-good image digest, rollback command, smoke check, and handling of non-reversible data changes. `helm --wait` and a failing smoke check do not themselves restore the previous release. Keep this in the existing deployment runbook; a new release platform is unnecessary. Existing GitOps deployments should retain their own promotion and recovery mechanisms.

### 3. P1 — The factory does not continuously validate its own releases

Evidence: the checkout has 17 workspace/hook tests but no `.github/workflows/` for the factory itself. README release instructions are edit, bump, changelog, commit/tag/push. Local `actionlint` passes; `zizmor --offline --min-severity medium` reports 39 high findings, all unpinned action references, across the CI and delivery templates.

The tags are intentional placeholders: onboarding instructs the builder to pin them. That reduces the risk if onboarding succeeds, but makes security depend on every generated copy being corrected. Separately, `ci.yml:180` executes a downloader from an upstream `main` branch; pinning `uses:` does not fix that. The gitleaks download at `:47` is versioned but has no checksum verification.

Minimum remedy: one factory verification command and one CI workflow running the existing tests, shell checks, JSON/config validation, internal reference checks, and template lint/security checks. Ship pinned templates and immutable, verified tool downloads. Add an explicit update process for references inside template directories. GitHub recommends full commit SHAs for immutable action references. [GitHub secure use reference](https://docs.github.com/en/actions/reference/security/secure-use).

### 4. P1 — Repository onboarding can introduce a second delivery pipeline

Evidence: `plugins/factory/skills/onboard-project/SKILL.md:26` instructs the builder to add workflows and use a `factory-` prefix when a name collides. Renaming a workflow preserves the old file but does not prevent both workflows from deploying on the same push. Workspace onboarding explicitly preserves GitOps; repository onboarding needs equally clear delivery ownership.

Minimum remedy: inventory existing checks and release ownership first. Reuse or extend the established delivery mechanism; create a deployment workflow only when there is no existing equivalent and deployment setup is in scope. Test onboarding against a fixture that already has a push-triggered deployment and assert that no competing deployment is added.

### 5. P2 — Local green results can mean checks never ran

Evidence: `plugins/factory/hooks/scripts/quality-gate.sh:35–46` selects backend/frontend checks by source extension. A temporary repository with only `web/package-lock.json` changed returned exit 0 with no checks/output. Python test exit 5 and Vitest's `--passWithNoTests` also permit zero tests. `stop_hook_active` intentionally permits stopping after one block; it must not be interpreted as eventual success.

Minimum remedy: support the project's existing check command in both repository and workspace modes; include dependency manifests, lockfiles, and relevant test/build configuration in selection. Report passed, failed, skipped, and blocked distinctly, with the revision and test count. Treat unexpected zero-test runs as failed verification; allow intentional no-test projects explicitly. Preserve the Stop recursion protection and keep CI as the authoritative merge signal.

The CI container filter (`ci.yml:34`) also excludes root `uv.lock`, `pyproject.toml`, and requirements files. Dependency-only changes can therefore skip the PR container scan, although delivery scans the image later. Match triggers to actual image build inputs.

### 6. P2 — Migration protection assumes the default branch is main

Evidence: `plugins/factory/hooks/scripts/guard-files.sh:19` hardcodes `origin/main` despite configuration supporting `default_branch`. A temporary workspace configured for `develop`, with a migration committed to `origin/develop`, allowed editing that migration.

Minimum remedy: resolve the owning repository's configured default branch, including workspace configuration, and distinguish an unavailable base reference from a new migration. Add tests for `develop`, missing remote refs, nested session directories, and path normalization. Report inability to verify immutability rather than silently claiming protection.

### 7. P2 — Risk and completion rules need explicit definitions

Evidence: the feature workflow requires manual confirmation for “High-risk” work, but the architect's required sections do not define a risk classification. Reviews emit Critical / Important / Minor without shared severity criteria. The lite workflow does not create a brief, while `implementation-validator` still requires one with manual verification.

Minimum remedy: add a short shared definition of done to existing instructions. High risk should include authorization/tenant isolation changes, destructive data migrations, cloud permissions, and deployment behavior. Require risk reason, relevant verification, recovery method, and owner acceptance of remaining material risks. Make lite validation follow its plan/manual steps instead of requiring a nonexistent brief. Keep unrelated repairs out of scope, while recording an owner and follow-up for unresolved vulnerabilities. NIST SSDF includes vulnerability response as well as prevention. [NIST SSDF](https://csrc.nist.gov/Projects/ssdf).

For interrupted runs, append a small checkpoint to the existing brief or workspace review artifact: current phase, baseline/current revisions, checks, approvals, repair count, and next action. On resume, verify the working tree and preserve unrelated user edits. This does not require a workflow database.

### 8. P2 — The factory's agent behavior is not evaluated like an AI product

Evidence: `principles-ml` correctly requires evaluations for application AI changes. The factory itself has no checked-in scenario suite testing whether its prompts follow approvals, preserve scope, resist instructions embedded in tickets/tool output, or recover after interruption. Shell tests cannot establish those behaviors.

Minimum remedy: start with six small fixture scenarios: a bug fix, an authorization change, a dependency-only update, an unrelated failing baseline, a malicious instruction embedded in task data, and an interrupted cross-repository change. Use known expected outcomes and real tests to grade code; inspect action logs for unauthorized mutations and approval violations. Keep fixtures synthetic and credential-free. Run representative cases through the installed client before prompt/model releases, repeat ambiguous cases, and automate only when repetition warrants it. Anthropic recommends evaluating environmental outcomes as well as agent traces. [Agent evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).

Record plugin/client/model version, successful outcome, human rework, repair rounds, elapsed time, and available usage/cost data in a simple CSV or Markdown table. Measure whether a review role catches distinct defects before adding or removing roles. Treat Claude Code and Copilot compatibility as separately tested configurations; this assessment did not execute either client.

## A small implementation sequence

| Change | Scope | Acceptance evidence |
| --- | --- | --- |
| 1. Factory regression checks | Existing tests in CI, common guard variants, configured migration branch, dependency triggers, honest check statuses | Reproductions above become passing regression tests; no cloud credentials required |
| 2. Safe pipeline templates | Immutable references/downloads, delivery ownership during onboarding, signature-before-mutation, approved saved plans, recovery instructions | Template lint/security checks pass; existing-delivery fixture remains single-owner; deployment flow tested in a disposable environment |
| 3. Workflow reliability | Risk/completion definitions, lite validator consistency, brief checkpoint, six agent scenarios | Recorded client-specific scenario outcomes and evidence for each acceptance criterion |

Keep each change reviewable; split the second change further if deployment validation requires separate infrastructure work. Do not introduce a queue, vector database, workflow service, agent memory platform, additional reviewer roles, or a paid evaluation service for these needs. The existing files, Python tests, shell hooks, and CI are sufficient starting points.

## Verification and limits

- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v`: 17 passed.
- `actionlint` on CI, delivery, and PR-format templates: passed.
- Offline `zizmor` on those templates: failed with 39 high unpinned-reference findings; 22 other findings suppressed by the selected settings/severity threshold. This is not a complete vulnerability count.
- Guard probes passed command strings as JSON only. No Terraform, kubectl, AWS, or push operation was executed.
- Migration/default-branch and lockfile-selection probes used disposable Git repositories.
- No hosted workflows, production environments, cloud IAM policies, client hook integration, or model behavior were exercised. Deployment findings are static review findings, not observed production incidents.
- Only this assessment document was added. Runtime behavior, repository settings, and application repositories were not changed.
