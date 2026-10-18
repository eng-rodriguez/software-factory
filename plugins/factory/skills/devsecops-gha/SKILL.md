---
name: devsecops-gha
description: Rules for GitHub Actions pipelines and supply-chain security. Use when creating or editing anything in .github/, Dockerfiles, deploy steps, or when reviewing a PR for security.
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.

## Adapt to the project

Inspect existing triggers, stacks, check commands, release ownership and artifact contracts before selecting template jobs. Python/Django, React, Terraform and AKS paths are examples, not a required topology. For Go, Angular or other stacks preserve the existing build/test/security tools and connect them to the same outcome gates. Do not copy incompatible jobs or create a second deploy pipeline. For reconciler-owned environments use [GitOps](../gitops/SKILL.md): CI can propose a digest PR, but must not also perform Helm/kubectl deployment or trigger synchronization.

Validate changed path filters against representative source, lockfile, check-script and deployment changes. Render/validate changed Kubernetes configuration separately from image scanning, using [stack-kubernetes](../stack-kubernetes/SKILL.md). Match checks to actual artifacts; document what a skipped job means.

Credentialed planning executes repository code: same-repository PR origin alone is not approval. Prefer credential-free PR checks and the project's trusted lane for cloud/state access. Verify the target revision's required checks and existing environment protections before enabling delivery; report prerequisites without changing owner-managed settings. Use [verification evidence](../../guides/verification.md) to distinguish lint from actual workflow behavior.

## Pipeline rules
1. Every third-party action is pinned to a full commit SHA with a version comment. Never a tag or branch.
2. Top-level `permissions: contents: read`; jobs request only what they need (id-token: write for OIDC, security-events: write for SARIF).
3. Cloud access only through OIDC federation (Azure federated credentials / AWS IAM role). No long-lived cloud keys in secrets.
4. Never use pull_request_target with a checkout of PR code. Never interpolate untrusted input (titles, branch names, comments) directly into run: — pass via env.
5. Every PR receives applicable tests and security checks: secrets detection plus language-appropriate SAST/SCA, IaC/configuration and container scans for affected artifacts. Bandit/pip-audit/npm audit are stack-specific examples. Each required check fails its job; preserve existing controls and report missing coverage. The factory never creates or changes rulesets or branch protection; the repo owner or the org decides which checks are required. Use the existing approved tooling; factory defaults require no paid service or API key. Do not remove an organization's existing scanners or attestations to match a template.
6. Images: build once, scan, generate SBOM, sign with cosign keyless, deploy by digest.
7. Staging and production deploys run in GitHub Environments with required reviewers and branch restrictions. Verify image signatures before cloud mutations. Prepare a saved plan for each environment, approve that exact plan, validate revision/run/age/checksums, and apply it without replanning. Follow templates/deployment.md for sensitive artifact access and recovery. Preserve existing deployment ownership; never add a parallel delivery pipeline.
8. Workflows set timeout-minutes and concurrency; caches never hold secrets.
9. Templates live under skills/devsecops-gha/templates/. Reuse their relevant controls, adapt to verified project facts and validate the result; do not copy assumptions blindly.

## Templates
- `templates/ci.yml` — PR gates: secrets, python, web, IaC, Terraform plan, container, workflows, scope, and the `ci-ok` aggregator.
- `templates/deliver.yml` — build once, SBOM, sign, deploy staging by digest, DAST, approve, production.
- `templates/pr-format.yml` — PR title and section check.
- `templates/terraform-plan.sh` and `templates/deployment.md` — saved-plan verification and operations runbook.
- `templates/dependabot.yml` — weekly grouped updates with Conventional Commit prefixes.

Templates ship with full commit SHAs and version comments. Review upstream releases/advisories before updating pins; use scripts/update-action-pins.py in the factory checkout to include both templates and factory CI. A moved tag is not evidence of safety. Run bash scripts/check.sh after updates. Versioned Go tool installs use the checksum database; never execute a downloader from a mutable branch.

## Review questions
- Could a malicious PR or a hijacked action tag reach a secret in this workflow?
- Does any job have more permissions or cloud scope than its steps need?
- Is anything deployed that was not scanned and signed?
