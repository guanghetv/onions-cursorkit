#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-$(pwd)}"
MODE="${MODE:-apply}" # apply|dry-run
WITH_POST_COMMIT="${WITH_POST_COMMIT:-1}"
WITH_PRE_PUSH="${WITH_PRE_PUSH:-1}"
TIMESTAMP="$(date +%Y%m%d%H%M%S)"
BACKUP_ROOT="$TARGET_REPO/.aicr-migration-backup/$TIMESTAMP"

RUNTIME_FILES=(
  "hook-pre-commit.sh"
  "diff-fingerprint.mjs"
  "validate-cr-gate.mjs"
  "event-log.mjs"
  "repo-context.mjs"
  "resolve-runtime-dir.sh"
)

POST_COMMIT_FILES=(
  "link-cr-commit.mjs"
)

PRE_PUSH_FILES=(
  "upload-events-ci.mjs"
)

log() {
  echo "[aicr-bundled] $*"
}

ensure_git_repo() {
  if [[ ! -d "$TARGET_REPO/.git" ]]; then
    echo "[aicr-bundled] not a git repository: $TARGET_REPO" >&2
    exit 1
  fi
}

all_runtime_sources() {
  local files=("${RUNTIME_FILES[@]}")
  if [[ "$WITH_POST_COMMIT" == "1" ]]; then
    files+=("${POST_COMMIT_FILES[@]}")
  fi
  if [[ "$WITH_PRE_PUSH" == "1" ]]; then
    files+=("${PRE_PUSH_FILES[@]}")
  fi
  printf "%s\n" "${files[@]}"
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
  done < <(all_runtime_sources)
  return 0
}

launcher_content_pre_commit() {
  cat <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME_DIR="$REPO_ROOT/vendor/aicr-runtime"
if [[ ! -f "$RUNTIME_DIR/hook-pre-commit.sh" ]]; then
  echo "[aicr-bundled] missing runtime hook: $RUNTIME_DIR/hook-pre-commit.sh" >&2
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
  local pre expected
  pre="$(launcher_content_pre_commit)"
  if ! file_matches_content "$TARGET_REPO/.githooks/pre-commit" "$pre"; then
    return 1
  fi
  if [[ "$WITH_POST_COMMIT" == "1" ]]; then
    expected="$(launcher_content_post_commit)"
    if ! file_matches_content "$TARGET_REPO/.githooks/post-commit" "$expected"; then
      return 1
    fi
  fi
  if [[ "$WITH_PRE_PUSH" == "1" ]]; then
    expected="$(launcher_content_pre_push)"
    if ! file_matches_content "$TARGET_REPO/.githooks/pre-push" "$expected"; then
      return 1
    fi
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

backup_if_exists() {
  if [[ "$MODE" == "dry-run" ]]; then
    log "dry-run backup from $TARGET_REPO"
    return 0
  fi
  local has_backup="0"
  if [[ -d "$TARGET_REPO/.githooks" ]]; then
    mkdir -p "$BACKUP_ROOT"
    cp -R "$TARGET_REPO/.githooks" "$BACKUP_ROOT/.githooks"
    has_backup="1"
  fi
  if [[ -d "$TARGET_REPO/vendor/aicr-runtime" ]]; then
    mkdir -p "$BACKUP_ROOT/vendor"
    cp -R "$TARGET_REPO/vendor/aicr-runtime" "$BACKUP_ROOT/vendor/aicr-runtime"
    has_backup="1"
  fi
  if [[ "$has_backup" == "1" ]]; then
    log "backup saved at $BACKUP_ROOT"
  fi
}

write_launchers() {
  write_file "$TARGET_REPO/.githooks/pre-commit" "$(launcher_content_pre_commit)"
  if [[ "$MODE" != "dry-run" ]]; then
    chmod +x "$TARGET_REPO/.githooks/pre-commit"
  fi

  if [[ "$WITH_POST_COMMIT" == "1" ]]; then
    write_file "$TARGET_REPO/.githooks/post-commit" "$(launcher_content_post_commit)"
    if [[ "$MODE" != "dry-run" ]]; then
      chmod +x "$TARGET_REPO/.githooks/post-commit"
    fi
  fi

  if [[ "$WITH_PRE_PUSH" == "1" ]]; then
    write_file "$TARGET_REPO/.githooks/pre-push" "$(launcher_content_pre_push)"
    if [[ "$MODE" != "dry-run" ]]; then
      chmod +x "$TARGET_REPO/.githooks/pre-push"
    fi
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
  done < <(all_runtime_sources)
  if [[ "$MODE" != "dry-run" ]]; then
    chmod +x "$runtime_dir/hook-pre-commit.sh" 2>/dev/null || true
    chmod +x "$runtime_dir/resolve-runtime-dir.sh" 2>/dev/null || true
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

main() {
  ensure_git_repo

  if [[ "$MODE" == "dry-run" ]]; then
    backup_if_exists
    install_runtime
    write_launchers
    set_hooks_path
    log "mode=dry-run repo=$TARGET_REPO with_post_commit=$WITH_POST_COMMIT with_pre_push=$WITH_PRE_PUSH"
    log "status=PREVIEW"
    return 0
  fi

  if ! needs_update; then
    log "mode=$MODE repo=$TARGET_REPO with_post_commit=$WITH_POST_COMMIT with_pre_push=$WITH_PRE_PUSH"
    log "status=UNCHANGED"
    return 0
  fi

  backup_if_exists
  install_runtime
  write_launchers
  set_hooks_path

  log "mode=$MODE repo=$TARGET_REPO with_post_commit=$WITH_POST_COMMIT with_pre_push=$WITH_PRE_PUSH"
  log "done. hooksPath=$(git -C "$TARGET_REPO" config core.hooksPath)"
  log "status=UPDATED"
}

main "$@"
