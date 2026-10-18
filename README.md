# Software Factory

Local AI development plugin: agents, principles, stack skills, guardrail hooks and delivery templates. Django/DRF and React specialists remain available; a project-aware application builder handles other stacks using their existing conventions and checks. Infrastructure guidance covers Terraform, Docker/Compose, Kubernetes/Helm and existing GitOps delivery.

**How to use it:** see [docs/USAGE.md](docs/USAGE.md) for setup, onboarding a repo, the daily commands, the feature chain, guardrails and model routing.

## Install

### Claude Code:

```shell
/plugin marketplace add eng-rodriguez/software-factory
/plugin install factory@my-factory
```

### GitHub Copilot CLI:

```shell
copilot plugin marketplace add eng-rodriguez/software-factory
copilot plugin install factory@my-factory
```

Merge `settings/claude-settings.json` into `~/.claude/settings.json`

## Requirements

```plain
Generic: jq, yq (v4), git, gh
Stack: uv, ruff, mypy, bandit, node, npm, terraform, tflint, checkov, actionlint, zizmor, gitleaks, trivy
```

On macOS (tflint is not in homebrew-core; it ships from its own tap):

```shell
brew install jq yq gh uv node terraform checkov actionlint zizmor gitleaks trivy
brew install terraform-linters/tap/tflint
```

## Centralized workspaces

For teams that keep AI files outside application repositories, use the opt-in
[central workspace mode](docs/USAGE.md#central-workspace-mode). Configuration and
planning artifacts live in the parent folder; each child keeps its own Git history
and checks. Existing onboarded repositories keep their current behavior.

## Stack support

The factory detects project frameworks instead of selecting them from directory names. See [stack routing and infrastructure work](docs/USAGE.md#stack-routing-and-infrastructure-work) for Go/Angular examples, validation requirements and specialization limits. No hosted factory service or cluster is required.

## Commands

Start with a workflow for coordinated implementation and review:

```shell
/feature-factory <feature> full chain with story, brief and final approvals
/factory-lite <fix> researcher ➔ builder ➔ validator ➔ security review
/explore <question> read-only exploration
/adr <decision> record an architecture decision
/closing-notes [slug] plain-language closing notes for PMs, scrum masters and leadership
/onboard-project set up a repo for the factory
```

You can also request a skill directly for focused guidance. These skills are used by the workflows and builders automatically when relevant; invoking one alone does not run the full feature chain. Use the command name exposed by your installed client's command picker, which may include the `factory` namespace.

### Application and infrastructure skills

```shell
/stack-context detect project stacks, builder routes and validation commands
/stack-django Django/DRF implementation and review guidance
/stack-react React/TypeScript implementation and review guidance
/stack-terraform Terraform configuration, validation and plan review; no apply
/stack-containers Docker image and Compose build/runtime guidance
/stack-kubernetes Kubernetes manifests, Helm charts and Kustomize validation; no deployment
/gitops desired-state changes and promotion guidance for existing GitOps delivery
/devsecops-gha GitHub Actions pipelines and software supply-chain security
```

Helm guidance is part of `/stack-kubernetes`; Argo CD and Flux guidance is part of `/gitops`. For Go, Angular or another application stack, use `/factory-lite` or `/feature-factory` and name the stack: the project-aware `application-builder` agent follows its existing conventions and checks. See [stack routing](docs/USAGE.md#stack-routing-and-infrastructure-work) and [Helm and GitOps work](docs/USAGE.md#helm-and-gitops-work) for support boundaries and examples.

### Supporting skills and principles

```shell
/workspace-context resolve repository or central-workspace configuration and artifact paths
/build-with-tests implement using project conventions and quality checks
/change-scope keep implementation and review within the approved change
/pr-format format pull request titles and descriptions
/principles-design shared design guidance and applicability rules
/principles-domain domain boundaries, ownership and invariants
/principles-api API contracts, authorization and compatibility
/principles-data persistence, migrations and consistency
/principles-services service boundaries and remote-call reliability
/principles-ml ML/LLM systems, retrieval, agents and evaluations
```

## Changing the factory

1. Edit the agent, skill or hook. Run `bash scripts/check.sh` (requires Python 3, Git, Bash, jq, yq v4, ShellCheck, actionlint and zizmor). For prompt/model/workflow changes, run the relevant [scenario evaluations](evals/README.md) through each supported client and record actual outcomes.
2. Bump "version" in `plugins/factory/.claude-plugin/plugin.json`.
3. Add a CHANGELOG.md entry.
4. Review the diff and verification evidence, then commit, tag vX.Y.Z, push. Run `/plugin marketplace update my-factory` where it is installed.


Templates ship pinned actions. To check for upstream pin changes, run `python3 scripts/update-action-pins.py`. Review upstream releases and advisories before applying updates with `--write`, then run verification again. This covers template directories as well as factory CI; a moved tag alone is not evidence of safety.

New delivery installations require the [deployment setup and recovery runbook](plugins/factory/skills/devsecops-gha/templates/deployment.md). Existing CI/GitOps delivery remains owned by the project. Updating this plugin does not upgrade already-copied workflows or configure cloud/GitHub environments.

## Local development

Add the checkout as a marketplace so edits apply after a restart:

```shell
claude plugin marketplace add ./software-factory
claude plugin install factory@my-factory
```

## License

[MIT](LICENSE.md)
