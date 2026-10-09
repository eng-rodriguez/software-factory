#!/usr/bin/env bash
# hooks/scripts/quality-gate.sh — Stop hook
set -uo pipefail
input=$(cat)
# Let Claude stop if this hook already blocked once in this turn
if [[ $(jq -r '.stop_hook_active // false' <<<"$input") == "true" ]]; then
  echo "Factory checks: BLOCKED — stop recursion protection; previous failure is unresolved, not a pass" >&2
  exit 0
fi
hook_dir=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
# Honor the runtime's session directory, not the plugin installation directory.
cwd=$(jq -r '.cwd // empty' <<<"$input")
[[ -z "$cwd" ]] || cd "$cwd" || exit 2
source "$hook_dir/lib.sh" || exit 2
if [[ "$FACTORY_MODE" == workspace && "$ROOT" == "$WORKSPACE_ROOT" ]]; then
  result=0
  while IFS=$'\t' read -r project repo _config; do
    [[ -n "$project" ]] || continue
    echo "Factory checks: $project" >&2
    (cd "$repo" && jq --arg cwd "$repo" '.cwd = $cwd' <<<"$input" | bash "$hook_dir/quality-gate.sh") || result=2
  done <<<"$WORKSPACE_PROJECTS"
  exit "$result"
fi
cd "$ROOT" || exit 2
echo "Factory checks: revision $(git rev-parse --short HEAD 2>/dev/null || echo unborn), including working tree in $ROOT" >&2
checked=false
allow_empty=false
if has_cfg; then allow_empty=$(yq -r '.checks.allow_no_tests // false' "$CFG"); fi
fail() { echo "Quality gate failed: $1. Use change-scope to classify the failure against the current approved feature or fix. Fix only in-scope defects within the workflow's repair limit; report unrelated failures separately. If scope is uncertain or verification is blocked, stop and report the blocker. Do not weaken or skip checks." >&2; exit 2; }

# Project configs can record the repository's existing check command.
# Commands are trusted project configuration, executed only from this Git root.
custom_checked=false
if has_cfg; then
  check=$(yq -r '.commands.check // ""' "$CFG") || exit 2
  if [[ -n "$check" ]]; then
    if [[ -n "$(changed_files)" ]]; then
      bash -c "$check" || fail "project checks in $ROOT"
      checked=true
      echo "Factory checks: PASSED project command (test count is reported by that command)" >&2
    fi
    custom_checked=true
  fi
fi

if [[ "$custom_checked" == false ]] && touched backend; then
  b=$(area_path backend)
  ( cd "$b" && py ruff check . && py ruff format --check . ) || fail "ruff in $b"
  ( cd "$b" && py mypy . ) || fail "mypy in $b"
  ( cd "$b" && py pytest -x -q --no-header -m "not slow" ); rc=$?
  if [[ $rc -eq 5 && "$allow_empty" == true ]]; then
    echo "Factory checks: SKIPPED pytest — no tests collected; checks.allow_no_tests explicitly enabled" >&2
  elif [[ $rc -ne 0 ]]; then fail "pytest in $b (exit $rc; zero tests is not verified)"
  else echo "Factory checks: PASSED pytest; see runner output for test count" >&2; fi
  ( cd "$b" && py python manage.py makemigrations --check --dry-run >/dev/null ) || fail "missing migrations"
  checked=true
  echo "Factory checks: PASSED backend lint, types and migration checks" >&2
fi

if [[ "$custom_checked" == false ]] && touched web; then
  w=$(area_path web)
  args=(run)
  if [[ "$allow_empty" == true ]]; then
    args+=(--passWithNoTests)
    echo "Factory checks: zero-test frontend runs are explicitly allowed; inspect Vitest count (zero = SKIPPED)" >&2
  fi
  ( cd "$w" && npm run -s lint && npx --no-install tsc --noEmit && npx --no-install vitest "${args[@]}" ) || fail "frontend checks in $w"
  checked=true
  echo "Factory checks: PASSED frontend command; see Vitest output for test count/status" >&2
fi

if [[ "$custom_checked" == false ]] && touched infra; then
  i=$(area_path infra)
  ( terraform -chdir="$i" fmt -check -recursive && tflint --chdir="$i" --recursive ) || fail "terraform fmt/tflint in $i"
  checked=true
  echo "Factory checks: PASSED infrastructure lint (not application tests)" >&2
fi

if changed_files | grep -q '^\.github/workflows/'; then
  ( actionlint && zizmor --min-severity medium .github/workflows ) || fail "workflow lint"
  checked=true
  echo "Factory checks: PASSED workflow lint" >&2
fi
[[ "$checked" == true ]] || echo "Factory checks: SKIPPED — no applicable checks ran; this is not verification" >&2
exit 0
