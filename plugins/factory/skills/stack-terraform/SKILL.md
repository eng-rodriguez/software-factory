---
name: stack-terraform
description: Implement and validate Terraform infrastructure changes using the project's existing modules, state ownership and cloud provider. Use for Terraform configuration and plan review, not apply operations.
---

Follow the approved scope and [principles-design](../principles-design/SKILL.md).

## Discover and implement
1. Inspect root modules, module interfaces, environment/backend selection, provider constraints/lockfiles, existing checks and infrastructure ownership. Do not assume `infra/` or a cloud provider. Identify state/credential access without reading or disclosing secret/state values unnecessarily.
2. Preserve resource addresses and state boundaries. Explain replacements, deletions, provider upgrades and lifecycle changes before proceeding; moving source files does not necessarily move resource addresses. Draft reviewed moved blocks when supported instead of running state/import commands.
3. Prefer modules with a meaningful interface and ownership boundary; do not create a network/cluster/database module merely to fill a standard layout. Separate environment state and access where required. Follow existing remote-state locking, encryption, backup and recovery arrangements; report missing safeguards without provisioning a backend implicitly.
4. Constrain provider/module versions and preserve reviewed provider lockfiles. Initialization may download executable providers/modules and requires appropriate runtime permission. Avoid static credentials and secret values in configuration; references do not guarantee that providers omit values from state.
5. Apply least privilege, relevant encryption/network protections and existing tags (`project`, `env`, `owner`, `managed-by` when appropriate). Explain public exposure, private-endpoint connectivity/cost, and ownership instead of adding resources mechanically.

## Validate and hand off
Use the project's pinned toolchain: fmt check, backend-disabled initialization where needed, validate, TFLint and existing policy scans. Test changed module contracts with the project's existing Terraform test/mocking facilities; inspect tests before running because tests can apply resources. Do not add apply-based tests to local verification.

A real plan requires authorized backend/cloud access and may execute providers or external programs. Prefer credential-free validation first; report planning as blocked when access is unavailable. Saved plans and JSON may contain secrets; keep them in the authorized restricted system. Never run apply, destroy, import or state mutations in this development workflow.

Read [validation.md](validation.md) for example stages and failure triage. Return affected roots/resources, expected replacement/deletion/cost impact, policy findings, static versus actual-plan evidence, and the approved CI/operator handoff. Do not claim infrastructure works from formatting or validation alone.
