# Software Factory

Personal Claude Code plugin: agents, principle and stack skills, guardrail hooks and DevSecOps templates for Django/DRF, React, Terraform, Azure/AWS and containers.

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

## Commands

```shell
/feature-factory <feature> full chain with story, brief and final approvals
/factory-lite <fix> researcher ➔ builder ➔ validator ➔ security review
/explore <question> read-only exploration
/adr <decision> record an architecture decision
/closing-notes [slug] plain-language closing notes for PMs, scrum masters and leadership
/onboard-project set up a repo for the factory
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
