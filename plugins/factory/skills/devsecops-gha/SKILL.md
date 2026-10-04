---
name: devsecops-gha
description: Rules for GitHub Actions pipelines and supply-chain security. Use when creating or editing anything in .github/, Dockerfiles, deploy steps, or when reviewing a PR for security.
---
First use [workspace-context](../workspace-context/SKILL.md) to resolve the mode, project context and artifact paths. In workspace mode its path, commit, onboarding and CI rules override the repository-mode defaults below.

## Pipeline rules
1. Every third-party action is pinned to a full commit SHA with a version comment. Never a tag or branch.
2. Top-level `permissions: contents: read`; jobs request only what they need (id-token: write for OIDC, security-events: write for SARIF).
3. Cloud access only through OIDC federation (Azure federated credentials / AWS IAM role). No long-lived cloud keys in secrets.
4. Never use pull_request_target with a checkout of PR code. Never interpolate untrusted input (titles, branch names, comments) directly into run: — pass via env.
5. CI checks to run on every PR: secrets scan (gitleaks), SAST (bandit), dependency audit (pip-audit, npm audit), IaC scan, container scan, tests. Each fails its job. The factory never creates or changes rulesets or branch protection; the repo owner or the org decides which checks are required. Free tooling only: no GitHub Advanced Security features (CodeQL, dependency review, secret scanning, artifact attestations) and no paid API keys.
6. Images: build once, scan, generate SBOM, sign with cosign keyless, deploy by digest.
7. Production deploys run in a GitHub Environment with required reviewers and branch restrictions.
8. Workflows set timeout-minutes and concurrency; caches never hold secrets.
9. Templates live in the factory plugin under skills/devsecops-gha/templates/; copy, don't improvise.

## Templates
- `templates/ci.yml` — PR gates: secrets, python, web, IaC, Terraform plan, container, workflows, scope, and the `ci-ok` aggregator.
- `templates/deliver.yml` — build once, SBOM, sign, deploy staging by digest, DAST, approve, production.
- `templates/pr-format.yml` — PR title and section check.
- `templates/dependabot.yml` — weekly grouped updates with Conventional Commit prefixes.

Templates show action tags for readability. Run `pinact run` after copying to pin every `uses:` to a full SHA.

## Review questions
- Could a malicious PR or a hijacked action tag reach a secret in this workflow?
- Does any job have more permissions or cloud scope than its steps need?
- Is anything deployed that was not scanned and signed?
