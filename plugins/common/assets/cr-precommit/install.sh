#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-$(pwd)}"
DRY_RUN="${DRY_RUN:-false}"
MODE="${MODE:-apply}" # apply|dry-run

RUNTIME_FILES=(
  "hook-pre-commit.sh"
  "aicr-utils.mjs"
  "validate-cr-gate.mjs"
  "event-log.mjs"
  "link-cr-commit.mjs"
  "upload-events-ci.mjs"
)

# Removed from runtime in V2; prune on upgrade so UNCHANGED detection stays accurate.
OBSOLETE_RUNTIME_FILES=(
  "repo-context.mjs"
  "diff-fingerprint.mjs"
  "resolve-runtime-dir.sh"
  "hook-post-commit.sh"
  "hook-pre-push.sh"
  "aggregate-mr.mjs"
  "fetch-events-ci.mjs"
  "gitlab-auth.mjs"
  "log-hook-event.mjs"
  "list-mr-commits.mjs"
  "publish-gitlab-note.mjs"
  "read-events.mjs"
)

usage() {
  cat <<'EOF'
Usage:
  install.sh [target_repo]

Env:
  DRY_RUN=true              Preview changes only (sets MODE=dry-run).
  MODE=apply|dry-run        Install mode (batch-rollout uses this).

What this installer does:
  1) Install thin hooks + vendor/aicr-runtime
  2) Set git core.hooksPath=.githooks in target repo

Note: Does NOT install /commit command.
EOF
}

log() {
  echo "[cr-setup] $*"
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ "$DRY_RUN" == "true" ]]; then
  MODE="dry-run"
fi

if [[ ! -d "$TARGET_REPO" ]]; then
  echo "[cr-setup] target repo not found: $TARGET_REPO" >&2
  exit 1
fi

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "[cr-setup] not a git repository: $TARGET_REPO" >&2
  exit 1
fi

runtime_has_obsolete_files() {
  local runtime_dir="$TARGET_REPO/vendor/aicr-runtime"
  local file
  for file in "${OBSOLETE_RUNTIME_FILES[@]}"; do
    if [[ -f "$runtime_dir/$file" ]]; then
      return 0
    fi
  done
  return 1
}

prune_obsolete_runtime() {
  local runtime_dir="$TARGET_REPO/vendor/aicr-runtime"
  local file
  for file in "${OBSOLETE_RUNTIME_FILES[@]}"; do
    if [[ ! -f "$runtime_dir/$file" ]]; then
      continue
    fi
    if [[ "$MODE" == "dry-run" ]]; then
      log "dry-run remove $runtime_dir/$file"
    else
      rm -f "$runtime_dir/$file"
      log "removed obsolete $file"
    fi
  done
}

runtime_matches_source() {
  local runtime_dir="$TARGET_REPO/vendor/aicr-runtime"
  local file
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    if [[ ! -f "$runtime_dir/$file" ]]; then
      return 1
    fi
    if ! cmp -s "$SCRIPT_DIR/$file" "$runtime_dir/$file"; then
      return 1
    fi
  done < <(printf "%s\n" "${RUNTIME_FILES[@]}")
  return 0
}

launcher_content_pre_commit() {
  cat <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$REPO_ROOT/vendor/aicr-runtime"
if [[ ! -f "$RUNTIME_DIR/hook-pre-commit.sh" ]]; then
  echo "[cr-setup] missing runtime hook: $RUNTIME_DIR/hook-pre-commit.sh" >&2
  exit 2
fi
exec bash "$RUNTIME_DIR/hook-pre-commit.sh" "$@"
EOF
}

launcher_content_post_commit() {
  cat <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$REPO_ROOT/vendor/aicr-runtime"
LINKER="$RUNTIME_DIR/link-cr-commit.mjs"
if [[ ! -f "$LINKER" ]]; then
  exit 0
fi
node "$LINKER" >/dev/null 2>&1 || true
exit 0
EOF
}

launcher_content_pre_push() {
  cat <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$REPO_ROOT/vendor/aicr-runtime"
UPLOADER="$RUNTIME_DIR/upload-events-ci.mjs"
if [[ ! -f "$UPLOADER" ]]; then
  exit 0
fi
node "$UPLOADER" || echo "[aicr-reminder] events 上传失败，已保留本地 snapshot（见 .git/aicr/ci-export/）。" >&2
exit 0
EOF
}

file_matches_content() {
  local path="$1"
  local expected="$2"
  if [[ ! -f "$path" ]]; then
    return 1
  fi
  local current
  current="$(cat "$path")"
  [[ "$current" == "$expected" ]]
}

launchers_match_expected() {
  local expected
  if ! file_matches_content "$TARGET_REPO/.githooks/pre-commit" "$(launcher_content_pre_commit)"; then
    return 1
  fi
  expected="$(launcher_content_post_commit)"
  if ! file_matches_content "$TARGET_REPO/.githooks/post-commit" "$expected"; then
    return 1
  fi
  expected="$(launcher_content_pre_push)"
  if ! file_matches_content "$TARGET_REPO/.githooks/pre-push" "$expected"; then
    return 1
  fi
  return 0
}

hooks_path_is_set() {
  local current
  current="$(git -C "$TARGET_REPO" config core.hooksPath 2>/dev/null || true)"
  [[ "$current" == ".githooks" ]]
}

copy_file() {
  local src="$1"
  local dst="$2"
  if [[ "$MODE" == "dry-run" ]]; then
    log "dry-run copy $src -> $dst"
    return 0
  fi
  mkdir -p "$(dirname "$dst")"
  cp "$src" "$dst"
}

write_file() {
  local path="$1"
  local content="$2"
  if [[ "$MODE" == "dry-run" ]]; then
    log "dry-run write $path"
    return 0
  fi
  mkdir -p "$(dirname "$path")"
  printf "%s" "$content" >"$path"
}

write_launchers() {
  write_file "$TARGET_REPO/.githooks/pre-commit" "$(launcher_content_pre_commit)"
  write_file "$TARGET_REPO/.githooks/post-commit" "$(launcher_content_post_commit)"
  write_file "$TARGET_REPO/.githooks/pre-push" "$(launcher_content_pre_push)"
  if [[ "$MODE" != "dry-run" ]]; then
    chmod +x "$TARGET_REPO/.githooks/pre-commit" \
      "$TARGET_REPO/.githooks/post-commit" \
      "$TARGET_REPO/.githooks/pre-push"
  fi
}

install_runtime() {
  local runtime_dir="$TARGET_REPO/vendor/aicr-runtime"
  if [[ "$MODE" == "dry-run" ]]; then
    log "dry-run sync runtime dir $runtime_dir"
  else
    mkdir -p "$runtime_dir"
  fi
  local file
  while IFS= read -r file; do
    [[ -z "$file" ]] && continue
    copy_file "$SCRIPT_DIR/$file" "$runtime_dir/$file"
  done < <(printf "%s\n" "${RUNTIME_FILES[@]}")
  prune_obsolete_runtime
  if [[ "$MODE" != "dry-run" ]]; then
    chmod +x "$runtime_dir/hook-pre-commit.sh" 2>/dev/null || true
  fi
}

set_hooks_path() {
  if [[ "$MODE" == "dry-run" ]]; then
    log "dry-run git -C $TARGET_REPO config core.hooksPath .githooks"
    return 0
  fi
  git -C "$TARGET_REPO" config core.hooksPath .githooks
}

needs_update() {
  if runtime_has_obsolete_files; then
    return 0
  fi
  if ! runtime_matches_source; then
    return 0
  fi
  if ! launchers_match_expected; then
    return 0
  fi
  if ! hooks_path_is_set; then
    return 0
  fi
  return 1
}

if [[ "$MODE" == "dry-run" ]]; then
  install_runtime
  write_launchers
  set_hooks_path
  log "mode=dry-run repo=$TARGET_REPO"
  log "status=PREVIEW"
  exit 0
fi

if ! needs_update; then
  log "mode=$MODE repo=$TARGET_REPO"
  log "status=UNCHANGED"
  exit 0
fi

install_runtime
write_launchers
set_hooks_path

log "mode=$MODE repo=$TARGET_REPO"
log "done. hooksPath=$(git -C "$TARGET_REPO" config core.hooksPath)"
log "status=UPDATED"
