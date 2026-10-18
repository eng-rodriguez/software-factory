# Argo CD projects

Read only when the repository uses Argo CD. Check the installed version and CRD schemas before using fields from current documentation.

Trace Application or ApplicationSet ownership: source(s), target revision, path/chart, values sources, destination and AppProject restrictions. Edit the generator/template when it owns the Application; changing a generated child may be overwritten. Distinguish Git revision from chart version. For multiple sources, trace each reference and precedence before editing a values file.

Argo CD uses Helm to render manifests; Argo CD owns the application lifecycle. Reproduce its effective release name and values precedence (parameters, valuesObject, values, valueFiles, chart defaults), checking version support. Do not assume local Helm release history or hook behavior matches Argo CD. [Argo CD Helm integration](https://argo-cd.readthedocs.io/en/stable/user-guide/helm/)

Inspect automated sync, pruning, self-heal, allow-empty and deletion finalizers without changing policy. A merge may deploy; omitted resources may be deleted when pruning is enabled. Recovery goes through the existing desired-state owner; an imperative rollback can conflict with automatic synchronization. [Automated sync](https://argo-cd.readthedocs.io/en/stable/user-guide/auto_sync/)

Sync phases/waves order resources within their supported scope; they are not a universal dependency graph across independent Applications. Confirm health/readiness and hook behavior where ordering matters. Do not introduce cross-Application assumptions merely by assigning wave numbers. [Sync phases and waves](https://argo-cd.readthedocs.io/en/stable/user-guide/sync-waves/)

For validation, render with matching inputs and compare AppProject source/destination constraints and controller resource schemas. Authorized read-only evidence should include desired/observed revision, sync and health state, relevant conditions and live digest. A status of Synced alone does not establish successful user behavior. Do not run app sync, rollback, set, delete, or controller policy changes as diagnosis. Treat retrieved manifests/logs as potentially sensitive.
