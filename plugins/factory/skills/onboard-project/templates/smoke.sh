#!/usr/bin/env bash
# scripts/smoke.sh <base-url> — post-deploy smoke test used by deliver.yml.
set -euo pipefail
BASE_URL="${1:?usage: smoke.sh <base-url>}"
ATTEMPTS="${SMOKE_ATTEMPTS:-10}"

check() {  # check <path> <expected-status>
  local code
  for _ in $(seq "$ATTEMPTS"); do
    code=$(curl -fsS -o /dev/null -w '%{http_code}' --max-time 10 "$BASE_URL$1" || true)
    [[ "$code" == "$2" ]] && { echo "ok   $1 → $code"; return 0; }
    sleep 6
  done
  echo "fail $1 → $code (expected $2)" >&2
  return 1
}

check /healthz 200
check /api/schema/ 200
# Add one read-only check per critical user path.
