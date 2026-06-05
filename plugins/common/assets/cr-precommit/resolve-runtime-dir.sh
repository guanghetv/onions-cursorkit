#!/usr/bin/env bash
# Resolve AICR runtime directory (bundled or legacy). Prints path to stdout.
set -euo pipefail

if [[ -n "${1:-}" ]]; then
  REPO_ROOT="$(cd "$1" && pwd)"
else
  REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
fi

if [[ -f "$REPO_ROOT/vendor/aicr-runtime/event-log.mjs" ]]; then
  echo "$REPO_ROOT/vendor/aicr-runtime"
  exit 0
fi

if [[ -f "$REPO_ROOT/.githooks/aicr/event-log.mjs" ]]; then
  echo "$REPO_ROOT/.githooks/aicr"
  exit 0
fi

if [[ -f "$REPO_ROOT/.git-hooks/aicr/event-log.mjs" ]]; then
  echo "$REPO_ROOT/.git-hooks/aicr"
  exit 0
fi

exit 1
