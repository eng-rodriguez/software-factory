#!/usr/bin/env bash
# hooks/scripts/guard-bash.sh — PreToolUse on Bash. Exit 2 blocks the call and shows stderr to Claude.
set -euo pipefail
cmd=$(jq -r '.tool_input.command // ""')

deny() { echo "BLOCKED by factory guard: $1" >&2; exit 2; }

# Infrastructure and cloud mutations
echo "$cmd" | grep -Eq 'terraform[[:space:]]+(apply|destroy|import|state|taint|force-unlock)' && deny "Terraform changes run only in CI with approval"
echo "$cmd" | grep -Eq 'kubectl[[:space:]]+(apply|delete|edit|patch|scale|drain|replace|rollout[[:space:]]+restart)' && deny "kubectl writes are not allowed; use --dry-run=client"
echo "$cmd" | grep -Eq 'kubectl.*--context[= ][^ ]*prod' && deny "no commands against prod contexts"
echo "$cmd" | grep -Eq 'helm[[:space:]]+(install|upgrade|uninstall|rollback)' && deny "Helm releases deploy via CI"
echo "$cmd" | grep -Eq '(^|[;&| ])az[[:space:]].*[[:space:]](create|delete|update|set|purge|start|stop|restart)([[:space:]]|$)' && deny "Azure CLI is read-only here"
echo "$cmd" | grep -Eq '(^|[;&| ])aws[[:space:]].*[[:space:]](create|delete|put|update|terminate|run-instances|modify|attach|detach)-?' && deny "AWS CLI is read-only here"

# Git safety
echo "$cmd" | grep -Eq 'git[[:space:]]+push.*(--force|-f)([[:space:]]|$)' && deny "no force push"
echo "$cmd" | grep -Eq 'git[[:space:]]+push.*[[:space:]](main|master)([[:space:]]|$)' && deny "push a branch and open a PR"
if echo "$cmd" | grep -Eq 'git[[:space:]]+commit'; then
  if git diff --cached --name-only 2>/dev/null | grep -Eq '(^|/)(\.env(\..*)?|.*\.(pem|key|pfx|p12)|.*\.tfvars|.*\.tfstate.*|kubeconfig|id_rsa.*)$'; then
    deny "staged files look like secrets"
  fi
  if command -v gitleaks >/dev/null; then
    gitleaks protect --staged --no-banner >/dev/null 2>&1 || deny "gitleaks found a secret in staged changes"
  fi
fi

# Destructive local commands
echo "$cmd" | grep -Eq 'rm[[:space:]]+-rf[[:space:]]+(/|~|\$HOME|\.)([[:space:]]|$)' && deny "destructive rm"
exit 0
