#!/usr/bin/env bash
# hooks/scripts/guard-bash.sh — PreToolUse on Bash. Exit 2 blocks the call and shows stderr to Claude.
set -euo pipefail
input=$(cat)
cmd=$(jq -r '.tool_input.command // ""' <<<"$input")
cwd=$(jq -r '.cwd // empty' <<<"$input")
[[ -z "$cwd" ]] || cd "$cwd" || exit 2

deny() { echo "BLOCKED by factory guard: $1" >&2; exit 2; }

# These patterns catch common mistakes; runtime permissions and read-only cloud
# credentials remain the security boundary. Do not treat this as a shell parser.
# Infrastructure and cloud mutations
echo "$cmd" | grep -Eq 'terraform([[:space:]]+-chdir(=[^[:space:]]+|[[:space:]]+[^[:space:]]+))?[[:space:]]+(apply|destroy|import|state|taint|force-unlock)' && deny "Terraform changes run only in CI with approval"
echo "$cmd" | grep -Eq 'kubectl[[:space:]]+([^;&|]*[[:space:]])?(apply|delete|edit|patch|scale|drain|replace|rollout[[:space:]]+restart)([[:space:]]|$)' && deny "kubectl writes run only in approved CI"
echo "$cmd" | grep -Eq 'kubectl.*--context[= ][^ ]*prod' && deny "no commands against prod contexts"
echo "$cmd" | grep -Eq 'helm[[:space:]]+([^;&|]*[[:space:]])?(install|upgrade|uninstall|rollback)([[:space:]]|$)' && deny "Helm releases deploy via CI"
echo "$cmd" | grep -Eq '(^|[;&| ])az[[:space:]].*[[:space:]](create|delete|update|set|purge|start|stop|restart)([[:space:]]|$)' && deny "Azure CLI is read-only here"
echo "$cmd" | grep -Eq '(^|[;&| ])aws[[:space:]].*[[:space:]](create|delete|put|update|terminate|run-instances|modify|attach|detach)-?' && deny "AWS CLI is read-only here"

echo "$cmd" | grep -Eq '(^|[;&| ])aws[[:space:]]+([^;&|]*[[:space:]])?s3[[:space:]]+(rm|mv|cp|sync|mb|rb)([[:space:]]|$)' && deny "AWS S3 mutations run only in CI"

# Git safety
echo "$cmd" | grep -Eq 'git[[:space:]]+([^;&|]*[[:space:]])?push.*(--force([-a-z]*|=[^[:space:]]*)?|-f)([[:space:]]|$)' && deny "no force push"
echo "$cmd" | grep -Eq 'git[[:space:]]+([^;&|]*[[:space:]])?push.*([[:space:]:]|refs/heads/)(main|master)([[:space:]]|$)' && deny "push a branch and open a PR"
if echo "$cmd" | grep -Eq 'git[[:space:]]+commit'; then
  if git diff --cached --name-only 2>/dev/null | grep -Eq '(^|/)(\.env(\..*)?|.*\.(pem|key|pfx|p12)|.*\.tfvars|.*\.tfstate.*|kubeconfig|id_rsa.*)$'; then
    deny "staged files look like secrets"
  fi
  if command -v gitleaks >/dev/null; then
    gitleaks protect --staged --no-banner >/dev/null 2>&1 || deny "gitleaks found a secret in staged changes"
  fi
fi

# Destructive local commands; match a literal $HOME in the submitted command.
# shellcheck disable=SC2016
echo "$cmd" | grep -Eq 'rm[[:space:]]+-rf[[:space:]]+(/|~|\$HOME|\.)([[:space:]]|$)' && deny "destructive rm"
exit 0
