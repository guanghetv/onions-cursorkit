#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EVENT_LOGGER="$SCRIPT_DIR/event-log.mjs"
VALIDATOR="$SCRIPT_DIR/validate-cr-gate.mjs"
EVENT_LOG_FILE="${AICR_EVENT_LOG:-.git/aicr/events.ndjson}"
ENFORCEMENT_MODE="${AICR_ENFORCEMENT_MODE:-hard}"
BYPASS_FLAG="${AICR_BYPASS_CR:-0}"
BYPASS_REASON="${AICR_BYPASS_REASON:-}"

log_event() {
  if [[ -f "$EVENT_LOGGER" ]]; then
    node "$EVENT_LOGGER" --event "$1" --extra "$2" >/dev/null 2>&1 || true
  fi
}

log_telemetry_error() {
  local message="$1"
  log_event "telemetry_error" "$(node -e "process.stdout.write(JSON.stringify({message: process.argv[1]}))" "$message")"
}

run_validator() {
  if [[ ! -f "$VALIDATOR" ]]; then
    return 2
  fi
  local repo_name branch_name author_name
  repo_name="$(basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)")"
  branch_name="$(git branch --show-current 2>/dev/null || echo unknown)"
  author_name="$(git config user.email 2>/dev/null || echo unknown)"
  node "$VALIDATOR" \
    --events "$EVENT_LOG_FILE" \
    --repo "$repo_name" \
    --branch "$branch_name" \
    --author "$author_name"
}

if [[ "$BYPASS_FLAG" == "1" ]]; then
  echo "[aicr-reminder] 检测到本次提交前未发现有效 /cr 记录，已按 AICR_BYPASS_CR=1 跳过阻断。"
  log_event "commit_attempted" '{"status":"bypassed"}'
  extra="{}"
  if [[ -n "$BYPASS_REASON" ]]; then
    extra="$(node -e 'process.stdout.write(JSON.stringify({bypass_reason: process.argv[1]}))' "$BYPASS_REASON")"
  fi
  log_event "commit_bypassed_cr" "$extra"
  exit 0
fi

set +e
run_validator
validator_status=$?
set -e

if [[ "$validator_status" -eq 0 ]]; then
  log_event "commit_attempted" '{"status":"allowed"}'
  exit 0
fi

if [[ "$validator_status" -ge 2 ]]; then
  echo "[aicr-reminder] 提醒链路异常，已放行本次提交（telemetry_error）。"
  log_telemetry_error "validator_unavailable_or_crashed"
  log_event "commit_attempted" '{"status":"telemetry_fallback"}'
  exit 0
fi

if [[ "$ENFORCEMENT_MODE" == "soft" ]]; then
  echo "[aicr-reminder] 检测到本次提交前未发现有效 /cr 记录，建议先运行 /cr 自检。"
  log_event "commit_attempted" '{"status":"soft_warn"}'
  log_event "commit_without_cr" "{}"
  exit 0
fi

echo "[aicr-reminder] 阻断提交：检测到本次提交前未发现有效 /cr 记录。"
echo "[aicr-reminder] 默认策略要求每次 commit 前执行一次 /cr，审查须通过（status=pass），且范围与暂存区一致。"
echo "[aicr-reminder] 请先执行 /cr 后重试，或使用 AICR_BYPASS_CR=1 显式跳过。"
log_event "commit_attempted" '{"status":"blocked"}'
log_event "commit_blocked_without_cr" "{}"
exit 1
