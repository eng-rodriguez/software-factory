---
name: stack-context
description: Detect project stacks and route work to the appropriate builder and validation commands. Use before planning, onboarding or implementing across application and infrastructure areas.
---

Resolve paths with [workspace-context](../workspace-context/SKILL.md), then inspect manifests, lockfiles, source imports, existing build/test commands and project instructions. Directory names alone do not establish a framework. Record detected versions, area paths, contract artifacts and commands; report conflicts or unknowns rather than guessing.

## Routing
| Detected work | Builder | Relevant skills |
| --- | --- | --- |
| Django/DRF backend | factory:django-builder | stack-django |
| React frontend | factory:react-builder | stack-react |
| Other application stack, e.g. Go or Angular | factory:application-builder | build-with-tests and the project's conventions |
| Terraform, Docker/Compose, Kubernetes | factory:infra-builder | Only the applicable stack-terraform, stack-containers, stack-kubernetes skills |
| Existing GitOps desired state or promotion | factory:infra-builder | gitops plus applicable Kubernetes/Helm guidance; pipeline-builder only for CI integration |
| GitHub Actions | factory:pipeline-builder | devsecops-gha |
| Other CI system | factory:pipeline-builder | Existing system's conventions; do not transplant GitHub syntax |
| Model/prompt/retrieval behavior | factory:ai-engineer | principles-ml |

Mixed projects can use several routes. Select builder order from actual dependencies in the approved brief, keeping writers sequential. In configuration, `web` remains the frontend area key regardless of framework; stack values are descriptive (for example `angular`, `go`, `django`, `react`).

## A new or unfamiliar stack
The project-aware application builder can implement with existing patterns and commands; this is not a claim of a tested framework specialization. Keep Go as Go and Angular as Angular. Do not install Django, React, Celery, Vitest or a client generator simply to fit factory defaults. Preserve the existing framework's routing, data loading, dependency injection and test conventions.

For a new project, use the user's chosen stack and approve a minimal layout/check plan before adding dependencies. If no stack was selected and the choice materially affects the task, present the relevant tradeoff for a decision. React/Django are available defaults, not mandatory migrations.

Set `commands.check` to the project's existing complete local verification command (from the Git root) for stacks outside the built-in Django/React/Terraform checks, or whenever their tooling differs. This is trusted executable configuration; inspect it before use. Reuse existing CI rather than copying incompatible template jobs. Missing tools, documentation or check commands are reported as verification gaps; do not fabricate a pass. Consult official documentation for the installed version when needed; if unavailable, state the limitation.

Add a dedicated stack skill only for repeated needs: discovery cues, implementation conventions, validation, pitfalls and representative scenarios. Add a new specialist agent only when its responsibility differs, not merely because another language appears. Record actual client trials before claiming specialization quality.
