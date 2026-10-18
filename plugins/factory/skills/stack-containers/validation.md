# Container verification examples

Adapt paths, image names and commands to the existing project. Use installed tools; missing tools are blockers for their checks, not permission to download or start privileged services.

| Stage | Example | Evidence and limitation |
| --- | --- | --- |
| Configuration | `docker compose config --quiet` | Parses configuration without starting services; avoid printing resolved secrets |
| Build | `docker build -f containers/api.Dockerfile -t factory-api-check .` | Exercises build inputs; does not establish runtime behavior |
| Image policy | `trivy image --severity HIGH,CRITICAL factory-api-check` with the project's failure policy | Inventory and policy result; retain accepted risks rather than hiding them |
| Runtime | Start the built image using the existing disposable test harness, no host-secret mounts | Verify UID, required writable paths, health and shutdown; record container identity and clean up only resources this check created |

For a read-only runtime, identify directories such as `/tmp` or application caches and provide narrow disposable mounts. Do not fix permission errors by changing to root. For build failures inspect context/ignore paths and dependency locks; for startup failures inspect entrypoint, UID and configuration; for shutdown failures inspect PID 1 and signal forwarding. Compose `down -v` is not routine cleanup when data ownership is uncertain.

A useful fixture deliberately denies a required writable path; the expected fix adds correct ownership or a narrow mount while retaining non-root execution. Pair static review with a real runtime test before claiming that behavior is verified.
