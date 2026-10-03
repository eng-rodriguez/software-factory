---
name: onboard-project
description: Sets up an existing repo for the software factory - detects layout and commands, writes .factory.yml and CLAUDE.md (or AGENTS.md), docs skeleton, PR template, CODEOWNERS and the devsecops workflows, then opens one PR. Use the first time the factory touches a repo, or for /onboard-project.
---
Templates are in [templates/](templates/). Never restructure the repo; record the real layout instead.

1. Detect, without writing anything:
   - Layout: monorepo (backend/web/infra together) or polyrepo (one layer here, siblings nearby).
   - Areas and paths: Django (manage.py, pyproject), React (package.json with react), Terraform (*.tf), Helm/Kustomize, Dockerfile.
   - Commands: Makefile targets, pyproject scripts, package.json scripts, uv vs pip.
   - Existing CLAUDE.md / AGENTS.md, .github/workflows, CODEOWNERS, docs/.
   - Default branch: `git symbolic-ref refs/remotes/origin/HEAD`.
   - Work or personal: ask the human if unclear. For work repos write AGENTS.md as the canonical file and CLAUDE.md containing only `@AGENTS.md`.
2. Draft `.factory.yml` from templates/factory.yml.tmpl and `CLAUDE.md` from templates/CLAUDE.md.tmpl, filled only with detected facts; mark unknowns `<TODO>`. Keep CLAUDE.md under 150 lines.
3. ASK HUMAN: approve both drafts. Apply feedback, then write them.
4. Create branch `chore/onboard-factory`.
5. Create the docs skeleton if missing: docs/domain.md (templates/domain.md.tmpl), docs/adr/, docs/briefs/, docs/stories/, docs/closing-notes/ (add .gitkeep to empty folders).
6. Copy templates/pull_request_template.md to .github/pull_request_template.md and templates/CODEOWNERS.tmpl to .github/CODEOWNERS with real paths and owner. Copy templates/smoke.sh to scripts/smoke.sh if the repo deploys a service.
7. factory:pipeline-builder: add ci.yml, deliver.yml (only if it deploys), pr-format.yml and dependabot.yml from the devsecops-gha templates. Never modify or delete existing workflows; if a name collides, report it and use a factory- prefix.
8. Commit in small Conventional Commits (chore(factory): ..., ci: ...). No Co-Authored-By trailers or tool footers.
9. Draft the PR with the pr-format skill. Technical Notes must list the GitHub settings the human may want to configure: Dependabot alerts, Actions policy, environments, OIDC identity variables. Never list paid features (Advanced Security, hosted AI review) as required. Never create, change or recommend replacing rulesets or branch protection; existing ones belong to the repo owner or the organization, especially in work repos.
10. ASK HUMAN: open the PR? On yes, push and run gh pr create --body-file. Never merge.
