# Kubernetes verification and diagnosis

For chart dependencies, values contracts, hooks and upgrades read [Helm engineering](helm.md). For reconciler-owned workloads use [GitOps](../gitops/SKILL.md) to identify effective inputs and publication effects.

Use only affected environments and existing tools. Rendering may require dependencies already supplied by the project; do not update chart dependencies or fetch unknown plugins implicitly.

| Artifact | Credential-free checks | Environment evidence, only with authorized access |
| --- | --- | --- |
| Helm | `helm lint <chart> -f <values>` then `helm template <release> <chart> -f <values>` | Admission, scheduling, actual rollout and digest |
| Kustomize | `kustomize build <overlay>` | Live reconciliation and overlay selection |
| Rendered YAML | Existing schema validator (for example kubeconform with the target version and project CRD schemas), then Trivy/Checkov config scan | Actual RBAC, CNI network policy, secret provider, TLS and storage behavior |

Treat rendered YAML as potentially sensitive: avoid printing Secret resources or uploading unfiltered manifests. Do not use an ignore-missing-schemas flag as evidence that CRDs were validated. Confirm rendered image repository/digest, resource selectors, service ports and security contexts; check environment values, not only defaults.

For authorized read-only diagnosis: inspect workload status, rollout history, events and narrowly scoped application logs without secret contents. Image pull errors suggest registry/identity issues; Pending suggests resources, scheduling or storage; probe failures require checking path/port/startup assumptions. Report evidence and a proposed fix; do not run apply, rollout restart, rollback, scale or controller sync.

Fixture acceptance examples: a values change must appear in rendered output; a missing digest or privileged container must fail policy; a service port change must still target the container port. Static passing results remain distinct from a successful cluster rollout.
