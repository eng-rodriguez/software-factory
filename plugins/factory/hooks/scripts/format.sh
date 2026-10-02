#!/usr/bin/env bash
# hooks/scripts/format.sh — PostToolUse on Edit|Write|MultiEdit. Never blocks.
f=$(jq -r '.tool_input.file_path // empty')
[[ -z "$f" || ! -f "$f" ]] && exit 0
case "$f" in
  *.py)
    command -v ruff >/dev/null && ruff format -q "$f" ;;
  *.ts|*.tsx|*.js|*.jsx|*.css|*.scss|*.json|*.md|*.yml|*.yaml)
    p="$(cd "$(dirname "$f")" && npm root 2>/dev/null)/.bin/prettier"
    [[ -x "$p" ]] && "$p" --write --log-level silent "$f" ;;
  *.tf)
    command -v terraform >/dev/null && terraform fmt "$f" >/dev/null ;;
esac
exit 0
