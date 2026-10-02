---
name: stack-terraform
description: How we write Terraform for Azure and AWS - module layout, remote state, pinning, secrets, tagging, and the commands agents may run. Use when writing or reviewing anything under infra/.
---
- Modules per concern (`network`, `cluster`, `database`, `registry`, `identity`); environments in `envs/<env>` composing modules.
- Remote state with locking: Azure Storage backend or S3 + DynamoDB/lockfile. One state per environment per stack.
- Pin provider and module versions; commit `.terraform.lock.hcl`.
- No secrets in variables or state where avoidable: use Key Vault / Secrets Manager references and managed identities / IAM roles.
- Tag every resource with `project`, `env`, `owner`, `managed-by=terraform`.
- Encryption at rest and private endpoints by default; anything public needs a line in the brief.
- Agents run `terraform fmt -check`, `validate`, `tflint`, `checkov`, and `plan`. Never `apply`, `destroy`, `import` or `state` commands.
