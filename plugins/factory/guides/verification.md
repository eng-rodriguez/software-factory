# Evidence appropriate to the artifact

Use the project's tools and approved scope. Reuse existing tests; add tests for meaningful behavior or failure modes, not assertions that mirror prose or configuration formatting.

| Artifact | Static evidence | Local behavior evidence | Environment evidence |
| --- | --- | --- | --- |
| Application | Lint/types/security checks | Unit, integration and acceptance tests | Actual service integration or user flow |
| Terraform | fmt, validate, policy checks | Credential-free module tests/mocks after inspecting test behavior | Authorized real plan; apply/restore belongs to operators/CI |
| Docker/Compose | Dockerfile/config checks | Build, startup, health, permissions, termination in a disposable runtime | Target runtime behavior |
| Helm/Kustomize | Render, schemas, policies across affected values/overlays | Existing local harness, if authorized | Admission, scheduling, connectivity and rollout |
| GitOps | Effective desired-state rendering, controller schemas, promotion and unchanged-environment comparison | Existing fixture checks without controller access | Observed source revision, reconciliation conditions, live digest and workload health |
| Pipeline | Syntax/security checks | Fixtures exercising selection, permissions and artifact wiring | Actual CI run and external identity behavior |

For every criterion report the command/artifact, repository revision, outcome (passed/failed/skipped/blocked), evidence level (static/local/environment), and what remains unproven. A test count may be not applicable for a configuration validator; report its actual scope instead. Never call syntax validity, a mock or an image build a successful deployment.

When a criterion needs unavailable infrastructure, retain local evidence and supply an operator verification step with expected outcome and recovery constraints. Missing optional environment evidence is a limitation; missing evidence required to establish the requested behavior is a completion blocker under change-scope/completion. No stage authorizes cloud mutation, deployment, secret access or installation on its own.
