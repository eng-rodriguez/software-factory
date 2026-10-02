---
name: stack-containers
description: How we build and run containers - Dockerfiles, base images, runtime behavior, Kubernetes manifests on AKS/EKS, workload identity, and supply-chain steps. Use when writing or reviewing Dockerfiles, Helm charts or Kustomize.
---
- Multi-stage Dockerfiles; slim or distroless runtime; run as non-root; no build tools in the final stage.
- Pin base images by digest; Dependabot or Renovate updates them.
- `HEALTHCHECK` (or Kubernetes probes), graceful shutdown on SIGTERM, logs to stdout as JSON.
- Kubernetes (AKS/EKS): Helm or Kustomize per service; resource requests/limits, liveness/readiness probes, `securityContext` (`runAsNonRoot`, `readOnlyRootFilesystem`, drop all capabilities), NetworkPolicies, PodDisruptionBudgets.
- Workload identity (Azure Workload Identity / EKS Pod Identity or IRSA) instead of static cloud keys.
- Images are scanned, get an SBOM, and are signed before any deploy. Deploy by digest, never by tag.
