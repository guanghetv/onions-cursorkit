#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-$(pwd)}"
DRY_RUN="${DRY_RUN:-false}"
INSTALL_MODE="${INSTALL_MODE:-bundled}" # legacy|bundled

usage() {
  cat <<'EOF'
Usage:
  install.sh [target_repo]

Env:
  DRY_RUN=true    Preview changes only.
  INSTALL_MODE=legacy|bundled  default bundled (thin hooks + vendor runtime).

What this installer does:
  1) bundled: install thin hooks + vendor runtime (recommended)
  2) legacy: copy cr-precommit assets into <repo>/.githooks/aicr/
  3) Create .githooks/pre-commit / post-commit / pre-push launchers
  4) Set git core.hooksPath=.githooks in target repo

Note: Does NOT install /commit command.
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -d "$TARGET_REPO" ]]; then
  echo "[cr-setup] target repo not found: $TARGET_REPO" >&2
  exit 1
fi

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "[cr-setup] not a git repository: $TARGET_REPO" >&2
  exit 1
fi

if [[ "$INSTALL_MODE" == "bundled" ]]; then
  MODE="apply"
  if [[ "$DRY_RUN" == "true" ]]; then
    MODE="dry-run"
  fi
  MODE="$MODE" bash "$SCRIPT_DIR/migrate-to-bundled-runtime.sh" "$TARGET_REPO"
  echo "[cr-setup] bundled 模式完成：thin hook + vendor/aicr-runtime"
  exit 0
fi

copy_asset() {
  local src="$1"
  local dest="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] copy $src -> $dest"
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  cp "$src" "$dest"
}

write_pre_commit_launcher() {
  local path="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] write launcher $path -> hook-pre-commit.sh"
    return 0
  fi
  cat >"$path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
bash "\$SCRIPT_DIR/aicr/hook-pre-commit.sh"
EOF
  chmod +x "$path"
}

write_post_commit_launcher() {
  local path="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] write launcher $path -> link-cr-commit.mjs"
    return 0
  fi
  cat >"$path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINKER="$SCRIPT_DIR/aicr/link-cr-commit.mjs"
if [[ -f "$LINKER" ]]; then
  node "$LINKER" >/dev/null 2>&1 || true
fi
exit 0
EOF
  chmod +x "$path"
}

write_pre_push_launcher() {
  local path="$1"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] write launcher $path -> upload-events-ci.mjs"
    return 0
  fi
  cat >"$path" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPLOADER="$SCRIPT_DIR/aicr/upload-events-ci.mjs"
if [[ -f "$UPLOADER" ]]; then
  node "$UPLOADER" || echo "[aicr-reminder] events 上传失败，已保留本地 snapshot（见 .git/aicr/ci-export/）。" >&2
fi
exit 0
EOF
  chmod +x "$path"
}

TARGET_HOOKS_DIR="$TARGET_REPO/.githooks"
TARGET_AICR_DIR="$TARGET_HOOKS_DIR/aicr"

for file in \
  hook-pre-commit.sh \
  diff-fingerprint.mjs \
  validate-cr-gate.mjs \
  event-log.mjs \
  link-cr-commit.mjs \
  repo-context.mjs \
  resolve-runtime-dir.sh \
  upload-events-ci.mjs; do
  if [[ -f "$SCRIPT_DIR/$file" ]]; then
    copy_asset "$SCRIPT_DIR/$file" "$TARGET_AICR_DIR/$file"
  fi
done

write_pre_commit_launcher "$TARGET_HOOKS_DIR/pre-commit"
write_post_commit_launcher "$TARGET_HOOKS_DIR/post-commit"
write_pre_push_launcher "$TARGET_HOOKS_DIR/pre-push"

if [[ "$DRY_RUN" != "true" ]]; then
  chmod +x "$TARGET_AICR_DIR/hook-pre-commit.sh" 2>/dev/null || true
  chmod +x "$TARGET_AICR_DIR/resolve-runtime-dir.sh" 2>/dev/null || true
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] git -C $TARGET_REPO config core.hooksPath .githooks"
else
  git -C "$TARGET_REPO" config core.hooksPath .githooks
fi

echo "[cr-setup] installed successfully in: $TARGET_REPO"
echo "[cr-setup] hooksPath: $(git -C "$TARGET_REPO" config core.hooksPath 2>/dev/null || echo ".githooks")"
echo "[cr-setup] MR 覆盖率：统一由 AI-CodeReview 服务聚合；本机 pre-push 上传需配置 AICR_INGEST_URL。"

