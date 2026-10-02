---
name: devsecops-gha
description: Rules for GitHub Actions pipelines and supply-chain security. Use when creating or editing anything in .github/, Dockerfiles, deploy steps, or when reviewing a PR for security.
---
## Pipeline rules
1. Every third-party action is pinned to a full commit SHA with a version comment. Never a tag or branch.
2. Top-level `permissions: contents: read`; jobs request only what they need (id-token: write for OIDC, security-events: write for SARIF).
3. Cloud access only through OIDC federation (Azure federated credentials / AWS IAM role). No long-lived cloud keys in secrets.
4. Never use pull_request_target with a checkout of PR code. Never interpolate untrusted input (titles, branch names, comments) directly into run: — pass via env.
5. Required checks: secrets scan, SAST, dependency review, IaC scan, container scan, tests. All block merge.
6. Images: build once, scan, generate SBOM, sign, attest provenance, deploy by digest.
7. Production deploys run in a GitHub Environment with required reviewers and branch restrictions.
8. Workflows set timeout-minutes and concurrency; caches never hold secrets.
9. Templates live in the factory plugin under skills/devsecops-gha/templates/; copy, don't improvise.

## Templates
- `templates/ci.yml` — PR gates: secrets, CodeQL, python, web, dependency review, IaC, Terraform plan, container, workflows, scope, and the `ci-ok` aggregator.
- `templates/claude-review.yml` — AI review with this plugin's pr-reviewer and security-reviewer.
- `templates/deliver.yml` — build once, SBOM, sign, attest, deploy staging by digest, DAST, approve, production.
- `templates/pr-format.yml` — PR title and section check.
- `templates/dependabot.yml` — weekly grouped updates with Conventional Commit prefixes.

Templates show action tags for readability. Run `pinact run` after copying to pin every `uses:` to a full SHA.

## Review questions
- Could a malicious PR or a hijacked action tag reach a secret in this workflow?
- Does any job have more permissions or cloud scope than its steps need?
- Is anything deployed that was not scanned and signed?
