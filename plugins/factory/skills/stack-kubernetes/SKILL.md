---
name: stack-kubernetes
description: Implement and validate Kubernetes manifests, Helm charts and Kustomize overlays in existing projects. Use for workload configuration and rollout diagnosis, without deploying from the development workflow.
---

Follow the approved scope and [principles-design](../principles-design/SKILL.md). Inspect the actual cluster distribution/version and chart/overlay layout; do not assume AKS, EKS, OpenShift or a cluster is available.

For chart or values changes read [Helm engineering](helm.md). When a reconciler owns delivery, also load [GitOps](../gitops/SKILL.md) and only its relevant controller reference.

## Discover and implement
1. Identify deployment/GitOps ownership, namespaces, values/overlays, image contract, service accounts, secret references, networking and storage. Keep cluster-owned resources separate from application-owned workloads; do not create a competing deploy path.
2. Preserve selectors and immutable-resource constraints. Render each affected environment; avoid copying full manifests where existing values/overlays express the change. Deploy released images by digest and verify the chart consumes that field.
3. Default to non-root, no privilege escalation, dropped capabilities and an appropriate seccomp profile. Design writable mounts before requiring a read-only root. Respect OpenShift UID/SCC constraints when applicable rather than requesting broader privileges.
4. Set resources from workload evidence. Define startup/readiness/liveness independently; dependency outages should not create liveness restart loops. Use replicas, topology and PDBs when availability requirements justify them; check that disruption budgets permit intended maintenance. Configure autoscaling only with suitable metrics and capacity assumptions.
5. Scope service accounts/RBAC to actual needs; disable token automount when unnecessary. Network policies must account for DNS and required ingress/egress and need an enforcing CNI. Preserve TLS/certificate and ingress ownership. Reference the project's secret provider; do not generate plaintext credentials.
6. For persistent data, identify storage/reclaim behavior and recovery expectations before changing claims or stateful workloads. Define migration order and known-good rollback/forward-fix behavior; reverting YAML does not restore data.

## Validate and hand off
Use [validation.md](validation.md) for rendering, schema/security checks and diagnostic evidence. Use the project's supported Kubernetes versions and CRD schemas; report unsupported schema coverage. Static validation does not prove admission, scheduling, networking or rollout success.

Development agents do not deploy, mutate clusters or initiate GitOps synchronization. Read-only cluster diagnostics require explicit access within runtime permissions; never dump secrets. Return affected workloads/environments, rendered evidence, compatibility risks, deployment owner, verification and recovery steps. Missing cluster access is an environment-verification gap, not permission to apply locally.
