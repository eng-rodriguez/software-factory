# Helm chart engineering

Read for chart, dependency or values changes. Identify the project's Helm major/minor, target Kubernetes versions and actual release owner before choosing flags or lifecycle behavior. A local Helm CLI and a GitOps controller may use different Helm versions.

## Structure and compatibility

Keep the existing chart layout, helpers and value names. Distinguish chart `version` from application `appVersion`; follow the project's chart release policy. Inspect `Chart.yaml`, `Chart.lock`, `values.yaml`, `values.schema.json`, templates, tests and environment overrides. Review schema constraints together with templates: new optional values need safe defaults; renaming/removing keys or changing types is a consumer compatibility change.

Preserve resource names, selectors, service target ports and ownership labels unless the approved change requires them. Quote strings deliberately and preserve booleans/numbers; avoid broad `tpl` evaluation of untrusted values. Avoid random/time-dependent templates and hidden live-cluster lookups when repeatable Git rendering is required. Inspect existing `lookup` usage; local rendering may not reproduce its cluster-dependent output.

## Dependencies

Preserve dependency aliases, conditions, tags and reviewed source/version constraints. For existing locked dependencies, use the project's dependency build procedure rather than silently resolving newer versions. `helm dependency build` reconstructs from `Chart.lock`; without a lock it behaves like update. Do not use it to silently generate a missing lockfile or download dependencies without normal network authorization. An intentional dependency upgrade reviews `Chart.yaml`, `Chart.lock`, changed defaults and rendered output together. Registry credentials stay outside values and chart packages. [Helm dependency build](https://helm.sh/docs/helm/helm_dependency_build/)

## Verification matrix

Use the project's existing complete check command and installed tools. For each affected environment:
1. Lint the chart with the same ordered values files, release name, namespace and supported Kubernetes capabilities as the real renderer. Do not disable schema validation to make invalid values pass.
2. Render defaults and affected overrides with `helm template`; compare before/after object identities, selectors, service ports, image digest and intended fields. Inspect CRDs separately or include them explicitly when relevant. Keep rendered secrets out of shared logs/artifacts.
3. Run existing schema/policy checks and template tests. Add behavioral assertions for the changed contract and negative values cases. Use an existing Helm test plugin only if installed and approved; do not install one for a trivial values change.
4. Render an unchanged consumer/environment when shared templates or defaults change, to detect accidental compatibility breaks. Local static rendering does not establish admission or rollout success.

Example for an existing service chart: changing staging's Service port from 8080 to 9090 should preserve its target port 8080 and leave production unchanged. Validate the rendered Service, not just the values file. Include file order and any inline/controller overrides in the evidence.

## Hooks, CRDs and recovery

Hooks can run jobs and mutate external systems. Inspect their ordering, retry/idempotency, timeout and cleanup behavior, plus the controller's supported hook semantics. `helm test` creates cluster resources; it is not a static local check. Do not execute install, upgrade, test or rollback from the development workflow. Hook resources have lifecycle/cleanup considerations separate from ordinary release resources. [Helm hooks](https://helm.sh/docs/topics/charts_hooks/)

Helm's `crds/` handling is not an ordinary templated resource upgrade path. Plan CRD ownership, schema compatibility, controller sequencing and custom-resource data migration explicitly; do not assume a chart rollback restores CRDs or their data. [Helm CRD guidance](https://helm.sh/docs/chart_best_practices/custom_resource_definitions/)

For an operator handoff record chart version/source, effective values, prior known-good artifact, required compatibility window and recovery path. A Helm rollback does not reverse database/external side effects. For GitOps-managed resources, use [GitOps guidance](../gitops/SKILL.md); an out-of-band Helm rollback may conflict with reconciliation.
