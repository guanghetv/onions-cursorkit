#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
UPLOADER="$SCRIPT_DIR/upload-events-ci.mjs"

if [[ -f "$UPLOADER" ]]; then
  node "$UPLOADER" || echo "[aicr-reminder] events 上传失败，已保留本地 snapshot（见 .git/aicr/ci-export/）。" >&2
fi

exit 0
