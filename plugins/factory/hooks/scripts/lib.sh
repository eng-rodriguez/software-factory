#!/usr/bin/env bash
# hooks/scripts/lib.sh — sourced, not executed. Needs jq; yq v4 when .factory.yml exists.
# Workspace mode is activated only by an ancestor .factory/workspace.yml.
# Existing/unlisted repositories keep their local configuration.
factory_error() { echo "Factory configuration: $*" >&2; return 2; }
factory_context() {
  ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd -P)
  CFG="$ROOT/.factory.yml"
  FACTORY_MODE=repository
  # Public context consumed by callers that source this library.
  export WORKSPACE_ROOT=""
  WORKSPACE_PROJECTS=""
  local dir manifest data id rel repo cfg rows
  dir=$(pwd -P)
  while [[ "$dir" != / && ! -f "$dir/.factory/workspace.yml" ]]; do dir=$(dirname "$dir"); done
  manifest="$dir/.factory/workspace.yml"
  [[ -f "$manifest" ]] || return 0
  if ! command -v yq >/dev/null || ! command -v jq >/dev/null; then factory_error "workspace mode requires yq v4 and jq"; return 2; fi
  data=$(yq -o=json '.' "$manifest") || { factory_error "cannot parse $manifest"; return 2; }
  jq -e '(.version == 1) and (.mode == "workspace") and (.projects | type == "object" and length > 0) and
    ([.projects[].path] | length == (unique | length)) and
    all(.projects | to_entries[]; (.key | test("^[A-Za-z0-9_-]+$")) and
      (.value.path | type == "string" and test("^[A-Za-z0-9_-]+$")))' <<<"$data" >/dev/null || {
    factory_error "invalid workspace manifest: use version 1, mode workspace, and direct-child project paths"; return 2;
  }
  # A workspace must not change the behavior of an unlisted Git repository.
  if [[ "$(pwd -P)" != "$dir" ]] && ! jq -e --arg path "${ROOT#"$dir"/}" 'any(.projects[]; .path == $path)' <<<"$data" >/dev/null; then
    return 0
  fi
  rows=$(jq -r '.projects | to_entries[] | [.key, .value.path] | @tsv' <<<"$data")
  while IFS=$'\t' read -r id rel; do
    repo="$dir/$rel"
    [[ -d "$repo" && ! -L "$repo" ]] && [[ "$(git -C "$repo" rev-parse --show-toplevel 2>/dev/null)" == "$repo" ]] || {
      factory_error "project $id must be an existing direct-child Git root (no symlink)"; return 2;
    }
    cfg="$dir/.factory/projects/$id.yml"
    [[ -f "$cfg" && ! -L "$cfg" && ! -L "$dir/.factory" && ! -L "$dir/.factory/projects" ]] || {
      factory_error "missing or symlinked external config: $cfg"; return 2;
    }
    [[ ! -f "$repo/.factory.yml" ]] || { factory_error "$repo already has .factory.yml; remove it from the workspace manifest or explicitly migrate it"; return 2; }
    yq -e 'tag == "!!map"' "$cfg" >/dev/null || { factory_error "invalid project config: $cfg"; return 2; }
    WORKSPACE_PROJECTS="${WORKSPACE_PROJECTS}${id}"$'\t'"${repo}"$'\t'"${cfg}"$'\n'
    if [[ "$ROOT" == "$repo" ]]; then
      FACTORY_MODE=workspace
      CFG="$cfg"
    fi
  done <<<"$rows"
  if [[ "$(pwd -P)" == "$dir" ]]; then FACTORY_MODE=workspace; ROOT="$dir"; CFG=""; fi
  if [[ "$FACTORY_MODE" == workspace ]]; then WORKSPACE_ROOT="$dir"; else WORKSPACE_PROJECTS=""; fi
}
factory_context || return 2
if [[ -f "$CFG" ]]; then
  command -v yq >/dev/null || { factory_error "configuration requires yq v4"; return 2; }
  yq -e 'tag == "!!map"' "$CFG" >/dev/null || { factory_error "invalid project config: $CFG"; return 2; }
fi

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
  local base; base=$(git merge-base HEAD "origin/$(default_branch)" 2>/dev/null || git rev-parse HEAD 2>/dev/null)
  { [[ -n "$base" ]] && git diff --name-only "$base"; git diff --name-only --cached; git ls-files --others --exclude-standard; } 2>/dev/null | sort -u
}

# Any change in an area may affect its build/tests, including lockfiles and config.
# Compare paths literally; a directory name is not a regular expression.
touched() {
  local p file
  p=$(area_path "$1"); [[ -z "$p" ]] && return 1
  while IFS= read -r file; do
    [[ "$p" == "." || "$file" == "$p/"* ]] && return 0
    case "$1:$file" in
      backend:pyproject.toml|backend:uv.lock|backend:requirements*.txt|backend:pytest.ini|backend:setup.cfg|backend:tox.ini|backend:.python-version) return 0 ;;
      web:package.json|web:package-lock.json|web:tsconfig*.json|web:vitest.config.*|web:vite.config.*) return 0 ;;
    esac
  done < <(changed_files)
  return 1
}

# py <cmd…> → run through uv when the project uses it
py() { if command -v uv >/dev/null && [[ -f uv.lock || -f "$ROOT/uv.lock" ]]; then uv run "$@"; else "$@"; fi; }
