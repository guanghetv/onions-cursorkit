#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_REPO="${1:-$(pwd)}"
DRY_RUN="${DRY_RUN:-false}"
RUN_SMOKE="${RUN_SMOKE:-false}"

usage() {
  cat <<'EOF'
Usage:
  install.sh [target_repo]

Env:
  DRY_RUN=true    Preview changes only.
  RUN_SMOKE=true  Run smoke-mr-coverage.sh after install.

What this installer does:
  1) Copy cr-precommit assets into <repo>/.githooks/aicr/
  2) Create .githooks/pre-commit / post-commit / pre-push launchers
  3) Sync cr-before-commit rule into <repo>/.cursor/rules/
  4) Copy GitLab CI template to <repo>/.gitlab/ci/ (optional reference)
  5) Set git core.hooksPath=.githooks in target repo

Note: Does NOT install /commit command or modify .gitlab-ci.yml automatically.
      Use /cr-setup-ci for Agent-guided CI integration.
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

write_launcher() {
  local path="$1"
  local hook_script="$2"
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "[dry-run] write launcher $path -> $hook_script"
    return 0
  fi
  cat >"$path" <<EOF
#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="\$(cd "\$(dirname "\${BASH_SOURCE[0]}")" && pwd)"
bash "\$SCRIPT_DIR/aicr/$hook_script"
EOF
  chmod +x "$path"
}

TARGET_HOOKS_DIR="$TARGET_REPO/.githooks"
TARGET_AICR_DIR="$TARGET_HOOKS_DIR/aicr"
TARGET_RULES_DIR="$TARGET_REPO/.cursor/rules"
TARGET_GITLAB_CI_DIR="$TARGET_REPO/.gitlab/ci"
RULE_SRC="$SCRIPT_DIR/../../rules/cr-before-commit.mdc"
GITLAB_CI_SRC="$SCRIPT_DIR/gitlab-ci"

for file in \
  hook-pre-commit.sh \
  hook-post-commit.sh \
  hook-pre-push.sh \
  validate-cr-gate.mjs \
  event-log.mjs \
  log-hook-event.mjs \
  link-cr-commit.mjs \
  read-events.mjs \
  repo-context.mjs \
  gitlab-auth.mjs \
  aggregate-mr.mjs \
  upload-events-ci.mjs \
  fetch-events-ci.mjs \
  list-mr-commits.mjs \
  schema.json \
  smoke-mr-coverage.sh; do
  if [[ -f "$SCRIPT_DIR/$file" ]]; then
    copy_asset "$SCRIPT_DIR/$file" "$TARGET_AICR_DIR/$file"
  fi
done

if [[ -f "$SCRIPT_DIR/publish-gitlab-note.mjs" ]]; then
  copy_asset "$SCRIPT_DIR/publish-gitlab-note.mjs" "$TARGET_AICR_DIR/publish-gitlab-note.mjs"
fi

if [[ -d "$GITLAB_CI_SRC" ]]; then
  copy_asset "$GITLAB_CI_SRC/aicr-mr-coverage.job.yml" "$TARGET_GITLAB_CI_DIR/aicr-mr-coverage.yml"
  copy_asset "$GITLAB_CI_SRC/integration-checklist.md" "$TARGET_GITLAB_CI_DIR/aicr-integration-checklist.md"
  copy_asset "$GITLAB_CI_SRC/workflow-rules.md" "$TARGET_GITLAB_CI_DIR/aicr-workflow-rules.md"
  copy_asset "$GITLAB_CI_SRC/starter.gitlab-ci.yml" "$TARGET_GITLAB_CI_DIR/aicr-starter.gitlab-ci.yml"
fi

if [[ -f "$RULE_SRC" ]]; then
  copy_asset "$RULE_SRC" "$TARGET_RULES_DIR/cr-before-commit.mdc"
else
  echo "[cr-setup] warning: rule source not found: $RULE_SRC" >&2
fi

write_launcher "$TARGET_HOOKS_DIR/pre-commit" "hook-pre-commit.sh"
write_launcher "$TARGET_HOOKS_DIR/post-commit" "hook-post-commit.sh"
write_launcher "$TARGET_HOOKS_DIR/pre-push" "hook-pre-push.sh"

if [[ "$DRY_RUN" != "true" ]]; then
  chmod +x "$TARGET_AICR_DIR/hook-pre-commit.sh" \
    "$TARGET_AICR_DIR/hook-post-commit.sh" \
    "$TARGET_AICR_DIR/hook-pre-push.sh" \
    "$TARGET_AICR_DIR/smoke-mr-coverage.sh" 2>/dev/null || true
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo "[dry-run] git -C $TARGET_REPO config core.hooksPath .githooks"
else
  git -C "$TARGET_REPO" config core.hooksPath .githooks
fi

echo "[cr-setup] installed successfully in: $TARGET_REPO"
echo "[cr-setup] hooksPath: $(git -C "$TARGET_REPO" config core.hooksPath 2>/dev/null || echo ".githooks")"
echo "[cr-setup] GitLab CI 模板: $TARGET_GITLAB_CI_DIR/aicr-mr-coverage.yml（需 include 或 /cr-setup-ci 接入）"
echo "[cr-setup] MR 覆盖率：CI 默认用 CI_JOB_TOKEN；本机 pre-push 上传 events 需配置 GITLAB_TOKEN。"

if [[ "$RUN_SMOKE" == "true" && "$DRY_RUN" != "true" && -f "$TARGET_AICR_DIR/smoke-mr-coverage.sh" ]]; then
  echo "[cr-setup] running smoke test..."
  bash "$TARGET_AICR_DIR/smoke-mr-coverage.sh" "$TARGET_REPO"
fi

if [[ "${AICR_SKIP_CI_PROMPT:-0}" != "1" ]]; then
  echo "[cr-setup] 提示：可在 Cursor 中执行 /cr-setup-ci，由 Agent 分析本仓库 GitLab CI 并给出接入方案（Agent 改文件但不 commit）。"
fi
