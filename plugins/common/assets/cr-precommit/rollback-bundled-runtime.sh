#!/usr/bin/env bash
set -euo pipefail

TARGET_REPO="${1:-$(pwd)}"
BACKUP_DIR="${2:-}"

usage() {
  cat <<'EOF'
Usage:
  rollback-bundled-runtime.sh <target_repo> [backup_dir]

Notes:
  - If backup_dir is empty, use the latest directory in .aicr-migration-backup/.
EOF
}

if [[ "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -d "$TARGET_REPO/.git" ]]; then
  echo "[aicr-rollback] not a git repository: $TARGET_REPO" >&2
  exit 1
fi

BACKUP_ROOT="$TARGET_REPO/.aicr-migration-backup"
if [[ -z "$BACKUP_DIR" ]]; then
  if [[ ! -d "$BACKUP_ROOT" ]]; then
    echo "[aicr-rollback] no backup found: $BACKUP_ROOT" >&2
    exit 1
  fi
  BACKUP_DIR="$(ls -1 "$BACKUP_ROOT" | sort | tail -n 1)"
  BACKUP_DIR="$BACKUP_ROOT/$BACKUP_DIR"
fi

if [[ ! -d "$BACKUP_DIR" ]]; then
  echo "[aicr-rollback] backup dir not found: $BACKUP_DIR" >&2
  exit 1
fi

if [[ -d "$BACKUP_DIR/.githooks" ]]; then
  rm -rf "$TARGET_REPO/.githooks"
  cp -R "$BACKUP_DIR/.githooks" "$TARGET_REPO/.githooks"
fi

if [[ -d "$BACKUP_DIR/vendor/aicr-runtime" ]]; then
  mkdir -p "$TARGET_REPO/vendor"
  rm -rf "$TARGET_REPO/vendor/aicr-runtime"
  cp -R "$BACKUP_DIR/vendor/aicr-runtime" "$TARGET_REPO/vendor/aicr-runtime"
else
  rm -rf "$TARGET_REPO/vendor/aicr-runtime"
fi

if [[ -d "$TARGET_REPO/.githooks" ]]; then
  git -C "$TARGET_REPO" config core.hooksPath .githooks
fi

echo "[aicr-rollback] restored from $BACKUP_DIR"
