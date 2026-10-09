# Deployment setup and recovery

Copy/adapt this runbook into the application's existing operations documentation. Preserve the established release/GitOps owner; do not install a competing delivery workflow. Copy `terraform-plan.sh` to `scripts/factory-terraform-plan.sh` only when installing this template's Terraform lane.

## Setup before enabling delivery

The template is for GitHub.com and Azure/AKS; adapt it to the actual stack before enabling it. Existing installations are not migrated automatically.

- Record the deployment owner, escalation contact and existing release mechanism.
- Configure `staging-plan` and `production-plan` environments, restricted to main, with separate plan identities. Grant only necessary read and state-lock permissions. Configure `staging` and `production`, also main-only, with deploy identities and required human reviewers. These are prerequisites, not settings the factory silently changes. If environment approval controls are unavailable, use an existing approved delivery mechanism; do not run this lane without them.
- Each plan/deploy environment pair must have identical `TF_DIR`, tenant and subscription values, using the same Terraform backend/workspace. Set a repository-wide exact `TF_VERSION` (for example the version already used by the project). Commit provider lockfiles; initialize in read-only lockfile mode.
- Set the image, Helm, cluster and URL variables documented in `deliver.yml`. Verify the chart actually uses `image.digest`. Adapt the signing workflow identity if the file/default branch changes. Ensure private registry authentication is available for signing, verification, scanning and cluster pulls as appropriate.
- Plans can contain secrets even when Terraform marks values sensitive. This template refuses plan storage in public repositories. All readers of a private repository can access its Actions artifacts: use it only if every reader is authorized for the plan's contents. Otherwise keep planning/apply in the existing restricted infrastructure system. Do not relax the guard or upload plaintext plans to public CI.
- Test the entire flow in a disposable nonproduction environment, including failed verification, expired plans and recovery, before enabling production.

## Review and promotion

Build/scanning/signing runs once on main. Staging planning publishes an immutable artifact tied to the revision, run/attempt, image digest, target environment, provider lockfile and plan checksum. Its public job summary contains action counts only. The artifact excludes raw plan logs and expires after one day.

Before approving the environment job, download that run's plan artifact to an authorized workstation and inspect `terraform show -no-color <path>/tf.plan` with the project's Terraform version. Review replacements/deletions, target environment, revision and image digest. Do not paste full plans into public comments or tickets. Counts alone are insufficient approval evidence. Delete local copies according to the project's sensitive-data policy.

After approval, the deployment job verifies the image signature before cloud login/mutation, downloads the exact artifact ID from its plan job, validates context/checksums and a maximum age of one hour, and applies that saved plan. It never generates a replacement plan. A stale-state error, expiry or changed run attempt requires a new complete workflow run and new plan review/approval. Production planning occurs only after staging smoke tests and DAST succeed; review its separate plan before approving production.

## Recovery

Before approval, record the last known-good image digest and Helm revision, the application rollback/flag-off procedure, database compatibility, recovery owner and smoke-test commands. Keep these with the release record. A passing image scan does not prove that a migration can be reversed.

If deployment or smoke tests fail, stop promotion and have the authorized release operator inspect status. From the approved operations environment, an application rollback can use:

```sh
helm history "$RELEASE" -n "$NS"
# Set PREVIOUS_REVISION from the verified release record, not a guessed value.
helm rollback "$RELEASE" "$PREVIOUS_REVISION" -n "$NS" --wait --timeout 10m
bash scripts/smoke.sh "$BASE_URL"
```

Verify the resulting workload runs the recorded known-good digest and exercise a critical user path. Helm rollback does not undo Terraform or database changes. For compatible expand/contract migrations, roll back application code while retaining the additive schema; for destructive changes, follow the reviewed restore/forward-fix procedure and its recovery objectives. For infrastructure, prepare a new reviewed plan from the intended configuration; do not blindly destroy resources or reuse an old saved plan. GitOps repositories recover through their established reconciliation process.

Record the failure, recovery evidence and follow-up owner. A failed post-deploy check leaves the release failed even if the workflow has already changed infrastructure.
