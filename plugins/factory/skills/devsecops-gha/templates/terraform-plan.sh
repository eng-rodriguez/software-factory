#!/usr/bin/env bash
# Copy to scripts/factory-terraform-plan.sh. Run only in the approved CI workflow.
# PLAN_DIR must be outside the Terraform configuration directory.
set -euo pipefail
: "${TF_DIR:?}" "${PLAN_DIR:?}" "${TARGET_ENV:?}" "${IMAGE_DIGEST:?}"
: "${GITHUB_SHA:?}" "${GITHUB_RUN_ID:?}" "${GITHUB_RUN_ATTEMPT:?}"
hash() { shasum -a 256 "$1" | awk '{print $1}'; }
fail() { echo "Plan verification failed: $*; start a new run, review and approve its plan" >&2; exit 1; }
case "${1:-}" in
  prepare)
    mkdir -p "$PLAN_DIR"
    PLAN_DIR=$(cd "$PLAN_DIR" && pwd -P)
    # Require the repository's reviewed provider lockfile; do not resolve new providers.
    terraform -chdir="$TF_DIR" init -input=false -lockfile=readonly
    terraform -chdir="$TF_DIR" plan -input=false -lock-timeout=5m -no-color \
      -out="$PLAN_DIR/tf.plan" > "$PLAN_DIR/plan.log" 2>&1 || fail "planning failed (inspect restricted runner logs)"
    jq -n --arg revision "$GITHUB_SHA" --arg run "$GITHUB_RUN_ID" \
      --arg attempt "$GITHUB_RUN_ATTEMPT" --arg environment "$TARGET_ENV" \
      --arg directory "$TF_DIR" --arg image "$IMAGE_DIGEST" \
      --arg plan_hash "$(hash "$PLAN_DIR/tf.plan")" \
      --arg lock_hash "$(hash "$TF_DIR/.terraform.lock.hcl")" \
      --argjson created "$(date +%s)" \
      '{revision:$revision,run:$run,attempt:$attempt,environment:$environment,
        directory:$directory,image:$image,plan_hash:$plan_hash,lock_hash:$lock_hash,created:$created}' \
      > "$PLAN_DIR/manifest.json"
    # Only action counts enter the job summary; plan values can contain secrets.
    terraform -chdir="$TF_DIR" show -json "$PLAN_DIR/tf.plan" |
      jq '[.resource_changes[]?.change.actions[]] | group_by(.) | map({action:.[0],count:length})' \
      > "$PLAN_DIR/summary.json"
    if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
      printf 'Plan for %s at %s, run %s attempt %s. Review the restricted plan artifact before approving. Expires after one hour.\n' \
        "$TARGET_ENV" "$GITHUB_SHA" "$GITHUB_RUN_ID" "$GITHUB_RUN_ATTEMPT" >> "$GITHUB_STEP_SUMMARY"
      cat "$PLAN_DIR/summary.json" >> "$GITHUB_STEP_SUMMARY"
    fi
    ;;
  apply)
    PLAN_DIR=$(cd "$PLAN_DIR" && pwd -P)
    jq -e --arg revision "$GITHUB_SHA" --arg run "$GITHUB_RUN_ID" \
      --arg attempt "$GITHUB_RUN_ATTEMPT" --arg environment "$TARGET_ENV" \
      --arg directory "$TF_DIR" --arg image "$IMAGE_DIGEST" --argjson now "$(date +%s)" \
      '.revision == $revision and .run == $run and .attempt == $attempt and
       .environment == $environment and .directory == $directory and .image == $image and
       (.created | type == "number") and .created <= $now and ($now - .created) <= 3600' \
      "$PLAN_DIR/manifest.json" >/dev/null || fail "wrong context or expired plan"
    [[ "$(hash "$PLAN_DIR/tf.plan")" == "$(jq -r .plan_hash "$PLAN_DIR/manifest.json")" ]] || fail "plan checksum"
    [[ "$(hash "$TF_DIR/.terraform.lock.hcl")" == "$(jq -r .lock_hash "$PLAN_DIR/manifest.json")" ]] || fail "provider lockfile checksum"
    terraform -chdir="$TF_DIR" init -input=false -lockfile=readonly
    # No implicit re-plan. Terraform also rejects a saved plan against stale state.
    terraform -chdir="$TF_DIR" apply -input=false -lock-timeout=5m "$PLAN_DIR/tf.plan"
    ;;
  *) echo "usage: $0 prepare|apply" >&2; exit 2 ;;
esac
