#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALLER="$SCRIPT_DIR/install.sh"
MODE="${MODE:-dry-run}" # dry-run|apply
REPOS_FILE="${REPOS_FILE:-}"
REPORT_FILE="${REPORT_FILE:-}" # optional csv output path
LOG_DIR="${LOG_DIR:-$(mktemp -d "${TMPDIR:-/tmp}/aicr-rollout.XXXXXX")}"

usage() {
  cat <<'EOF'
Usage:
  batch-rollout.sh --repos-file <path>

Env:
  MODE=dry-run|apply
  REPORT_FILE=/path/to/report.csv   optional
  LOG_DIR=/path/to/log-dir          optional (default: temp dir)
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "${1:-}" == "--repos-file" ]]; then
  REPOS_FILE="${2:-}"
fi

if [[ -z "$REPOS_FILE" || ! -f "$REPOS_FILE" ]]; then
  echo "[aicr-rollout] missing repos file. use --repos-file <path>" >&2
  exit 1
fi

if [[ "$MODE" != "dry-run" && "$MODE" != "apply" ]]; then
  echo "[aicr-rollout] invalid MODE: $MODE" >&2
  exit 1
fi

mkdir -p "$LOG_DIR"
if [[ -n "$REPORT_FILE" ]]; then
  mkdir -p "$(dirname "$REPORT_FILE")"
  : >"$REPORT_FILE"
fi

updated_count=0
unchanged_count=0
preview_count=0
failed_count=0

print_row() {
  local row="$1"
  echo "$row"
  if [[ -n "$REPORT_FILE" ]]; then
    echo "$row" >>"$REPORT_FILE"
  fi
}

parse_migration_status() {
  local log_file="$1"
  if grep -q "status=UNCHANGED" "$log_file"; then
    echo "UNCHANGED"
  elif grep -q "status=UPDATED" "$log_file"; then
    echo "UPDATED"
  elif grep -q "status=PREVIEW" "$log_file"; then
    echo "PREVIEW"
  else
    echo "UNKNOWN"
  fi
}

print_row "repo,status,reason,log_file"
while IFS= read -r repo || [[ -n "$repo" ]]; do
  [[ -z "$repo" ]] && continue
  [[ "$repo" =~ ^# ]] && continue

  reason=""
  status="UPDATED"
  safe_name="$(echo "$repo" | tr '/ ' '__')"
  repo_log="$LOG_DIR/${safe_name}.log"
  if [[ ! -d "$repo/.git" ]]; then
    status="FAILED"
    reason="not_git_repo"
    failed_count=$((failed_count + 1))
    print_row "$repo,$status,$reason,$repo_log"
    continue
  fi

  set +e
  MODE="$MODE" bash "$INSTALLER" "$repo" >"$repo_log" 2>&1
  code=$?
  set -e
  if [[ "$code" -ne 0 ]]; then
    status="FAILED"
    reason="migration_error"
    failed_count=$((failed_count + 1))
  else
    status="$(parse_migration_status "$repo_log")"
    case "$status" in
      PREVIEW)
        preview_count=$((preview_count + 1))
        ;;
      UNCHANGED)
        unchanged_count=$((unchanged_count + 1))
        ;;
      UPDATED)
        updated_count=$((updated_count + 1))
        ;;
      *)
        status="FAILED"
        reason="unknown_migration_status"
        failed_count=$((failed_count + 1))
        ;;
    esac
  fi
  print_row "$repo,$status,$reason,$repo_log"
done <"$REPOS_FILE"

echo "[aicr-rollout] mode=$MODE log_dir=$LOG_DIR"
echo "[aicr-rollout] summary updated=$updated_count unchanged=$unchanged_count preview=$preview_count failed=$failed_count"
