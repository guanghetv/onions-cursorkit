#!/usr/bin/env bash
set -euo pipefail

# CI 同步脚本：拉取 ai-guardrails → 运行 sync-guardrails.mjs → 有变更则自动提 MR。
#
# 必需 CI 变量：
#   SYNC_GITLAB_TOKEN   GitLab token，需具备：
#                       - ai-guardrails 的 read_repository
#                       - cursorkit 的 write_repository + api（推分支、建 MR）
# 可选变量：
#   GUARDRAILS_REPO     内容源仓库（host/path.git），默认 gitlab.yc345.tv/frontend/ai-guardrails.git
#   GUARDRAILS_REF      内容源分支或 tag，默认 master；发版联动时由上游传入 vX.Y.Z
#   TARGET_BRANCH       MR 目标分支，默认 CI_DEFAULT_BRANCH

GUARDRAILS_REPO="${GUARDRAILS_REPO:-gitlab.yc345.tv/frontend/ai-guardrails.git}"
GUARDRAILS_REF="${GUARDRAILS_REF:-master}"
TARGET_BRANCH="${TARGET_BRANCH:-${CI_DEFAULT_BRANCH:-master}}"

: "${SYNC_GITLAB_TOKEN:?缺少 CI 变量 SYNC_GITLAB_TOKEN}"
: "${CI_API_V4_URL:?本脚本需在 GitLab CI 中运行}"

echo "[ci-sync] 内容源: ${GUARDRAILS_REPO}@${GUARDRAILS_REF}"

CLONE_DIR=$(mktemp -d)
trap 'rm -rf "$CLONE_DIR"' EXIT
git clone --quiet --depth 1 --branch "$GUARDRAILS_REF" \
  "https://oauth2:${SYNC_GITLAB_TOKEN}@${GUARDRAILS_REPO}" "$CLONE_DIR/ai-guardrails"

node scripts/sync-guardrails.mjs --source "$CLONE_DIR/ai-guardrails"
node scripts/validate-template.mjs

if [ -z "$(git status --porcelain)" ]; then
  echo "[ci-sync] 内容无变化，跳过 MR"
  exit 0
fi

SRC_COMMIT=$(node -p "(require('./plugins/frontend/.sync-meta.json').sourceCommit||'').slice(0,8)")
BRANCH="sync/ai-guardrails-$(echo "$GUARDRAILS_REF" | tr '/' '-')-$(date +%Y%m%d%H%M%S)"
TITLE="chore: 同步 ai-guardrails@${GUARDRAILS_REF}（${SRC_COMMIT:-unknown}）"

git config user.name "guardrails-sync-bot"
git config user.email "ci-noreply@yc345.tv"
git checkout -b "$BRANCH"
git add -A
git commit -m "$TITLE"
git push --quiet \
  "https://oauth2:${SYNC_GITLAB_TOKEN}@${CI_SERVER_HOST}/${CI_PROJECT_PATH}.git" \
  "HEAD:${BRANCH}"

echo "[ci-sync] 已推送分支 ${BRANCH}，创建 MR..."

curl --fail -sS -X POST \
  -H "PRIVATE-TOKEN: ${SYNC_GITLAB_TOKEN}" \
  --data-urlencode "source_branch=${BRANCH}" \
  --data-urlencode "target_branch=${TARGET_BRANCH}" \
  --data-urlencode "title=${TITLE}" \
  --data-urlencode "description=由 ai-guardrails 发版流水线自动触发的内容同步。同步映射见 scripts/sync-guardrails.mjs，溯源信息见各插件 .sync-meta.json。" \
  --data-urlencode "remove_source_branch=true" \
  "${CI_API_V4_URL}/projects/${CI_PROJECT_ID}/merge_requests" >/dev/null

echo "[ci-sync] MR 已创建：${BRANCH} -> ${TARGET_BRANCH}"
