#!/usr/bin/env bash
# hooks/scripts/guard-files.sh — PreToolUse on Edit|Write|MultiEdit.
set -euo pipefail
f=$(jq -r '.tool_input.file_path // ""')
deny() { echo "BLOCKED by factory guard: $1" >&2; exit 2; }

case "$f" in
  *.env|*.env.*|*.pem|*.key|*.tfvars|*.tfstate*|*kubeconfig*) deny "secret or state file: $f" ;;
  *.terraform.lock.hcl) deny "lock file changes come from terraform init" ;;
esac

# Migrations already on main are immutable
if [[ "$f" == */migrations/*.py ]]; then
  top=$(git rev-parse --show-toplevel 2>/dev/null || true)
  if [[ -n "$top" ]] && git cat-file -e "origin/main:${f#"$top"/}" 2>/dev/null; then
    deny "migration already merged; create a new one"
  fi
fi
exit 0
