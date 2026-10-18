---
name: gitops
description: Prepare and validate desired-state changes, image promotions and recovery plans in an existing GitOps repository. Use for Argo CD, Flux or another established reconciler; do not install a controller or initiate synchronization.
---

Use [workspace-context](../workspace-context/SKILL.md) and [stack-context](../stack-context/SKILL.md) to resolve project ownership and paths. GitOps is an operating model for the target project; it does not require hosting the software factory.

## Discover the effective desired state

Trace the actual source repository/ref/path through chart/overlay generation and controller overrides to the destination cluster/namespace. Record reconciliation owner, auto-sync/prune/self-heal or suspension settings, environment promotion rules, secret references and image-update automation. A values file is not authoritative if another layer overrides it. Inspect ApplicationSet/generators or automation writers before editing generated outputs.

Read only the relevant controller reference: [Argo CD](references/argo-cd.md) or [Flux](references/flux.md). For another controller, preserve its established conventions and consult official version-appropriate documentation; do not translate it into Argo/Flux implicitly. Load [Kubernetes validation](../stack-kubernetes/SKILL.md) for workloads and [Helm guidance](../stack-kubernetes/helm.md) for charts.

## Prepare a bounded change

- Preserve a single deployment owner. CI may build, scan, sign and propose a configuration PR; it must not also deploy the same resources. Do not install a controller, restructure environment repositories or add automation without an approved requirement.
- Promote the same verified image digest rather than rebuilding for each environment. Confirm the source evidence, destination, previous digest and configuration compatibility. Change only the intended environment; chart versions, image digests and Git revisions are separate identifiers. Coordinate with existing image automation rather than fighting its next write.
- Use existing values/overlays and keep immutable references where supported by the project's promotion model. For a shared base, identify every affected consumer. Do not copy environment configuration wholesale or broaden permissions to solve a reconciliation failure.
- Keep secrets in the established external reference or encrypted-file mechanism. Do not decrypt secrets into the worktree, logs or PRs. Assess controller identity and decryption permissions without exposing values.
- Review deletions, pruning, finalizers, namespace changes, CRDs and persistent data as operational changes. Order dependencies using the controller's real readiness/ordering semantics; numeric ordering alone does not prove external systems are ready.

## Publication is an operational boundary

A push or merge to a watched ref can deploy automatically, including preview branches. Before publication identify watched refs and PR-preview triggers and disclose the deployment effect. Preparing a diff or PR is not authorization to merge, push to a watched deployment ref, or trigger reconciliation. Follow existing workflow publication approvals; never merge, sync, reconcile, suspend/resume controllers or run out-of-band Helm/kubectl writes in this development chain. Do not change auto-sync/pruning/approval policy to make the task easier.

## Verify and hand off

Render the effective target configuration with the existing tools and input order; validate schemas/policies and compare changed/unchanged environments. Check the actual rendered image digest and controller source mapping, not only a source string. Record missing dependencies, secret inputs or CRD schemas as coverage limits. Use [verification evidence](../../guides/verification.md): static passing output is not proof of convergence.

With authorized read-only access, correlate desired Git revision and image digest with controller observed revision, conditions, workload health and live image identity. Synced/Ready signals have controller-specific meaning; investigate drift without disabling its detection. Otherwise supply explicit operator checks and mark environment evidence unverified.

Recovery usually proposes a reviewed revert/forward-fix of desired state to a known-good digest/configuration through the same owner. Account for migrations, destructive pruning and external side effects; reverting Git does not restore data. Return source/ref/path, destination, precise promotion diff, verification evidence, deployment trigger/owner and recovery constraints. Preserve existing access controls and never claim a live rollout occurred from a Git edit.
