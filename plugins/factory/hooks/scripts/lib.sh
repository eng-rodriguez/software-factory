#!/usr/bin/env bash
# hooks/scripts/lib.sh — sourced, not executed. Needs jq; yq v4 when .factory.yml exists.
ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
CFG="$ROOT/.factory.yml"

has_cfg() { [[ -f "$CFG" ]] && command -v yq >/dev/null; }

default_branch() { if has_cfg; then yq -r '.default_branch // "main"' "$CFG"; else echo main; fi; }

# area_path <backend|web|infra|deploy> → path relative to the repo root, empty if absent
area_path() {
  if has_cfg; then yq -r ".areas.$1.path // \"\"" "$CFG"; return; fi
  case "$1" in
    backend) if [[ -f "$ROOT/manage.py" ]]; then echo .; elif [[ -d "$ROOT/backend" ]]; then echo backend; fi ;;
    web|infra|deploy) [[ -d "$ROOT/$1" ]] && echo "$1" ;;
  esac
}

# Files changed on this branch, staged, unstaged or new
changed_files() {
  local base; base=$(git merge-base HEAD "origin/$(default_branch)" 2>/dev/null || git rev-parse HEAD)
  { git diff --name-only "$base"; git diff --name-only --cached; git ls-files --others --exclude-standard; } | sort -u
}

# touched <area> <extension-regex> → true if a changed file under the area matches
touched() {
  local p prefix; p=$(area_path "$1"); [[ -z "$p" ]] && return 1
  if [[ "$p" == "." ]]; then prefix=""; else prefix="$p/"; fi
  changed_files | grep -Eq "^${prefix}.*\.($2)$"
}

# py <cmd…> → run through uv when the project uses it
py() { if command -v uv >/dev/null && [[ -f uv.lock || -f "$ROOT/uv.lock" ]]; then uv run "$@"; else "$@"; fi; }
