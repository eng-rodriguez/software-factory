---
name: stack-containers
description: Build, modify and diagnose Docker images and Compose configurations. Use for container build/runtime work; Kubernetes workloads use stack-kubernetes.
---

Follow the approved scope and [principles-design](../principles-design/SKILL.md). Load [stack-kubernetes](../stack-kubernetes/SKILL.md) only when workloads also change.

## Discover and implement
1. Inspect existing Dockerfiles, build contexts, ignore files, lockfiles, startup commands, Compose services and CI. Identify runtime user, writable paths, ports, signals, health behavior, target architecture and secret inputs. Preserve the existing build/deployment owner.
2. Change the smallest relevant stage/configuration. Prefer multi-stage builds where they separate build dependencies; choose an existing supported runtime base and reviewed digest. Keep caches useful without copying credentials or unnecessary source into the final image. Use build-secret mounts for secrets, not ARG/ENV or copied files.
3. Run as non-root with intentional ownership and writable directories. A read-only root filesystem may need explicit temporary volumes. Avoid broad chmod, privileged mode, host mounts or Docker socket access as permission fixes. Allow arbitrary UIDs when the target requires it.
4. Preserve signal delivery and graceful shutdown. Add a meaningful healthcheck or workload probe; distinguish liveness from dependency readiness. Keep logs on stdout/stderr using the project's format.
5. For Compose, preserve service DNS and internal ports; expose only required host ports. Keep local credentials external and distinguish disposable volumes from persistent user data. Do not run destructive volume cleanup or start privileged services as routine verification.

## Validate and hand off
Use existing Dockerfile lint/scanning tools and `docker compose config --quiet` when applicable. Build only within the runtime's permissions; builds execute project code and may access the network. Exercise startup, health, non-root/writable paths and termination in an authorized disposable local container. Do not mount host secrets or claim an image works because it builds.

For concrete commands and failure triage, read [validation.md](validation.md). Report commands/results, image identity, runtime assumptions and blocked checks. Image publication/signing belongs to the existing delivery pipeline, following [devsecops-gha](../devsecops-gha/SKILL.md) when it uses GitHub Actions; development work does not authorize publishing.
