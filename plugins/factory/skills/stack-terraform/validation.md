# Terraform validation stages

Use the project's exact supported Terraform version and existing module/check configuration. Examples assume a root at `infra/envs/dev`; replace that with the discovered root.

1. `terraform -chdir=infra/envs/dev fmt -check -recursive` checks formatting, not provider behavior.
2. When dependencies are needed and access is permitted, `terraform -chdir=infra/envs/dev init -backend=false -input=false -lockfile=readonly` prepares reviewed providers without initializing the remote backend. A missing lockfile for a new project needs an explicit dependency setup step, not silently changing an existing lockfile.
3. `terraform -chdir=infra/envs/dev validate`, project TFLint and policy scans validate configuration. Local module paths may lie outside the root; scan the relevant modules too.
4. Use existing credential-free module tests/mocks when supported by the pinned version. Inspect `.tftest.hcl` and provider configuration first; ordinary Terraform tests can create infrastructure. Do not execute apply-based tests here.
5. An authorized plan uses the existing trusted planning lane and correct backend/workspace. Review replacements/deletions, identity/network/storage impacts and unexpected drift. Do not disable locking merely to bypass an error or convert a plan failure into apply.

For init errors check version/lockfile/module source and backend intent. For validation errors distinguish missing provider setup from invalid configuration. For planning failures report a sanitized diagnostic and the restricted evidence location; never paste full plan JSON into a public artifact.

A useful module fixture covers valid inputs plus a rejected boundary case without cloud resources. A plan that was not run is `blocked` or `not required` with a reason, not `passed`. State restoration and actual resource behavior require a separate authorized environment exercise.
