# Flux projects

Read only for Flux repositories. Determine installed controller versions and CRD schemas before selecting fields or flags.

Trace source-controller objects to the consuming Kustomization or HelmRelease, including sourceRef, paths, revisions, target namespace, substitutions and service-account impersonation. A Flux Kustomization custom resource is distinct from a Kustomize `kustomization.yaml`; both may be needed to reconstruct effective desired state. Inspect dependsOn, health checks/wait, pruning, deletion policy and suspension without changing them. Dependencies must be acyclic and use the controller's readiness semantics. [Flux Kustomization](https://fluxcd.io/flux/components/kustomize/kustomizations/)

For HelmRelease, resolve chart source/version and ordered valuesFrom references plus inline values. Account for externally supplied ConfigMaps/Secrets and targetPath semantics rather than pretending `helm template` has all live inputs. Inspect install/upgrade remediation, rollback and drift-detection configuration; do not assume every Flux Helm installation enables drift correction. HelmRelease dependencies are not a generic ordering mechanism for every resource kind. [Flux HelmRelease](https://fluxcd.io/flux/components/helm/helmreleases/)

Inspect image-reflector/image-automation ownership where present before editing a promoted digest or marker. Preserve approved source branches, write targets and policies; do not trigger automation, rotate credentials or widen permissions.

Use the project's rendering/schema checks with the controller's effective substitutions and values. Missing encrypted or external secret inputs must remain explicit coverage limits; never dump them for easier reproduction. Authorized read-only diagnosis correlates source artifact revision, observed generation/revision, Ready conditions and workload digest. A local render is not evidence of controller reconciliation. Do not run bootstrap, reconcile, suspend/resume or resource mutations from this workflow. Prepare recovery in Git and leave operator actions to the established owner.
