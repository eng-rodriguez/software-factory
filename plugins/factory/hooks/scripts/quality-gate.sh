#!/usr/bin/env bash
# hooks/scripts/quality-gate.sh — Stop hook
set -uo pipefail
input=$(cat)
# Let Claude stop if this hook already blocked once in this turn
[[ $(jq -r '.stop_hook_active // false' <<<"$input") == "true" ]] && exit 0
hook_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# Honor the runtime's session directory, not the plugin installation directory.
cwd=$(jq -r '.cwd // empty' <<<"$input")
[[ -z "$cwd" ]] || cd "$cwd" || exit 2
source "$hook_dir/lib.sh" || exit 2
if [[ "$FACTORY_MODE" == workspace && "$ROOT" == "$WORKSPACE_ROOT" ]]; then
  result=0
  while IFS=$'\t' read -r project repo config; do
    [[ -n "$project" ]] || continue
    echo "Factory checks: $project" >&2
    (cd "$repo" && jq --arg cwd "$repo" '.cwd = $cwd' <<<"$input" | bash "$hook_dir/quality-gate.sh") || result=2
  done <<<"$WORKSPACE_PROJECTS"
  exit "$result"
fi
cd "$ROOT" || exit 0
fail() { echo "Quality gate failed: $1. Use change-scope to classify the failure against the current approved feature or fix. Fix only in-scope defects within the workflow's repair limit; report unrelated failures separately. If scope is uncertain or verification is blocked, stop and report the blocker. Do not weaken or skip checks." >&2; exit 2; }

# External configs can record the repository's existing check command.
# Commands are trusted workspace configuration, executed only from this Git root.
custom_checked=false
if [[ "$FACTORY_MODE" == workspace ]]; then
  check=$(yq -r '.commands.check // ""' "$CFG") || exit 2
  if [[ -n "$check" ]]; then
    if [[ -n "$(changed_files)" ]]; then bash -c "$check" || fail "project checks in $ROOT"; fi
    custom_checked=true
  fi
fi

if [[ "$custom_checked" == false ]] && touched backend 'py'; then
  b=$(area_path backend)
  ( cd "$b" && py ruff check . && py ruff format --check . ) || fail "ruff in $b"
  ( cd "$b" && py mypy . ) || fail "mypy in $b"
  ( cd "$b" && py pytest -x -q --no-header -m "not slow" ); rc=$?
  [[ $rc -eq 0 || $rc -eq 5 ]] || fail "pytest in $b"          # 5 = no tests collected
  ( cd "$b" && py python manage.py makemigrations --check --dry-run >/dev/null ) || fail "missing migrations"
fi

if [[ "$custom_checked" == false ]] && touched web 'ts|tsx|js|jsx'; then
  w=$(area_path web)
  ( cd "$w" && npm run -s lint && npx tsc --noEmit && npx vitest run --passWithNoTests ) || fail "frontend checks in $w"
fi

if [[ "$custom_checked" == false ]] && touched infra 'tf'; then
  i=$(area_path infra)
  ( terraform -chdir="$i" fmt -check -recursive && tflint --chdir="$i" --recursive ) || fail "terraform fmt/tflint in $i"
fi

if changed_files | grep -q '^\.github/workflows/'; then
  ( actionlint && zizmor --min-severity medium .github/workflows ) || fail "workflow lint"
fi
exit 0
