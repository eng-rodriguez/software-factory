# Changelog

## 0.2.1 - 2026-10-02

* pr-format.yml template skips Dependabot PRs, whose bodies lack the Summary / Why / Technical Notes sections.

## 0.2.0 - 2026-10-02

* Removed everything that needs a paid plan or API key: the `claude-review.yml` template, the CodeQL and dependency-review jobs in `ci.yml`, and artifact attestations in `deliver.yml`. Free scanners (gitleaks, pip-audit, npm audit, Checkov, Trivy, zizmor) stay.
* `pr-reviewer` runs locally only; `/onboard-project` no longer lists paid GitHub settings.
* `/onboard-project` no longer installs `claude-review.yml`.
* feature-factory, build-with-tests, onboard-project and pr-format forbid Co-Authored-By trailers and tool footers; USAGE.md documents the `attribution` setting.

## 0.1.3 - 2026-10-02

* pr-format: PR bodies must not end with an attribution or tool footer.

## 0.1.2 - 2026-10-02

* hooks: quote `${CLAUDE_PLUGIN_ROOT}` so hooks work when the plugin path contains spaces.

## 0.1.1 - 2026-10-02

* hooks: `changed_files` no longer prints git errors in repos without commits.

## 0.1.0 - 2026-10-02

* Initial factory: 13 agents, 18 skills, 4 hooks, 5 workflow templates, onboarding templates.
