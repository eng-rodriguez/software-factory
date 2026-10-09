#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
for tool in python3 git bash jq yq shellcheck actionlint zizmor; do
  command -v "$tool" >/dev/null || { echo "Missing verification tool: $tool" >&2; exit 1; }
done
yq --version | grep -Eq 'version v?4\.' || { echo 'Use mikefarah/yq v4' >&2; exit 1; }
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
while IFS= read -r script; do
  bash -n "$script"
  shellcheck -x -P SCRIPTDIR "$script"
done < <(find plugins scripts -name '*.sh' -type f | sort)
actionlint .github/workflows/*.yml plugins/factory/skills/devsecops-gha/templates/{ci,deliver,pr-format}.yml
zizmor --offline --min-severity medium --format plain .github/workflows plugins/factory/skills/devsecops-gha/templates/{ci,deliver,pr-format}.yml
