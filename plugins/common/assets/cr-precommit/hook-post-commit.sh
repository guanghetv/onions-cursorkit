#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LINKER="$SCRIPT_DIR/link-cr-commit.mjs"

if [[ -f "$LINKER" ]]; then
  node "$LINKER" >/dev/null 2>&1 || true
fi

exit 0
