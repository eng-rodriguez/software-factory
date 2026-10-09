# Factory scenario evaluations

These seven synthetic scenarios test the plugin as an AI workflow: six core cases plus onboarding with existing delivery. Deterministic hook/template tests run in `scripts/check.sh`; these scenarios require a real client session and a human to review its actions. No API key, hosted judge or evaluation service is required. Preparing and grading fixtures never invokes an AI client.

```sh
python3 scripts/evaluate.py prepare bug /tmp/factory-eval-bug
# Open that directory in your installed client, with this plugin version loaded.
# Submit TASK.md's request. Respond at the normal approval checkpoints.
PYTHONDONTWRITEBYTECODE=1 python3 scripts/evaluate.py grade bug /tmp/factory-eval-bug
```

Use a fresh, nonexistent directory per trial. Run without cloud credentials or write-capable remote tokens, inside the client's normal sandbox. The grader imports fixture code; inspect that code before running it and keep grading inside a sandbox. Do not run unreviewed model-generated code on a privileged host. Preserve the factory checkout/grader outside the agent's writable fixture. The fixture repositories have no remote, and the release fixture only prints a message.

For every scenario in `scenarios.json`, check both the grader's outcome and every `review` item against tool calls and actual state. A grader exit 0 verifies only its listed code/file outcomes. It does not prove that hooks loaded, that tests ran, that no data was exfiltrated, or that approvals were honored. For onboarding, inspect every new workflow's triggers/environment/actions to rule out a second deploy, regardless of its filename. For resume, inspect the checkpoint to confirm the repair budget was retained.

Run the relevant cases before releasing prompt/model changes, plus the complete suite before a release that changes workflow behavior. Test each supported client separately; repeat an ambiguous or failed case in a fresh fixture. Do not tune the grader to excuse a regression. Convert deterministic defects into ordinary regression tests.

Record one row per trial in a local copy of `results.csv`. Mark passed only when both outcome and human action review pass. Use failed or blocked otherwise; unavailable cost data is unknown. Keep evidence references local unless publication is authorized, and exclude credentials/proprietary content from logs. Compare task success, human rework, repairs and elapsed time before changing model routing or adding reviewer roles.

No live-client pass is implied by shipping this suite. Fill actual results only after running it; CI validates the fixture/grader mechanics separately.
