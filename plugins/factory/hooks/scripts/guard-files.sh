#!/usr/bin/env bash
# hooks/scripts/guard-files.sh — PreToolUse on Edit|Write|MultiEdit.
set -euo pipefail
input=$(cat)
f=$(jq -r '.tool_input.file_path // ""' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")
[[ -z "$cwd" ]] || cd "$cwd" || exit 2
[[ "$f" == /* || -z "$f" ]] || f="$PWD/$f"
deny() { echo "BLOCKED by factory guard: $1" >&2; exit 2; }

case "$f" in
  *.env|*.env.*|*.pem|*.key|*.pfx|*.p12|*.tfvars|*.tfstate*|*kubeconfig*) deny "secret or state file: $f" ;;
  *.terraform.lock.hcl) deny "lock file changes come from terraform init" ;;
esac

# Resolve the owning repository, not the session or plugin directory.
if [[ "$f" == */migrations/*.py ]]; then
  [[ ! -L "$f" ]] || deny "cannot verify a symlinked migration"
  dir=$(cd "$(dirname "$f")" 2>/dev/null && pwd -P) || deny "cannot resolve migration directory"
  f="$dir/$(basename "$f")"
  top=$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null) || deny "cannot resolve migration repository"
  hook_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
  cd "$top" || exit 2
  source "$hook_dir/lib.sh" || exit 2
  branch=$(default_branch) || deny "cannot resolve default branch"
  git rev-parse --verify "refs/remotes/origin/$branch^{commit}" >/dev/null 2>&1 || deny "cannot verify migration: origin/$branch is unavailable; fetch the base branch"
  if git cat-file -e "origin/$branch:${f#"$top"/}" 2>/dev/null; then
    deny "migration already merged; create a new one"
  fi
fi
exit 0
