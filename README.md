# Software Factory

Personal Claude Code plugin: agents, principle and stack skills, guardrail hooks and DevSecOps templates for Django/DRF, React, Terraform, Azure/AWS and containers.

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

## Commands

```shell
/feature-factory <feature> full chain with story, brief and final approvals
/factory-lite <fix> researcher ➔ builder ➔ validator ➔ security review
/explore <question> read-only exploration
/adr <decision> record an architecture decision
/onboard-project set up a repo for the factory
```

## Changing the factory

1. Edit the agent, skill or hook.
2. Bump "version" in `plugins/factory/.claude-plugin/plugin.json`.
3. Add a CHANGELOG.md entry.
4. Commit, tag vX.Y.Z, push. Run `/plugin marketplace update my-factory` where it is installed.


## Local development

Add the checkout as a marketplace so edits apply after a restart:

```shell
claude plugin marketplace add ./software-factory
claude plugin install factory@my-factory
```

`claude-review.yml` installs this plugin straight from the public repo, so CI needs no extra token.

## License

[MIT](LICENSE.md)
