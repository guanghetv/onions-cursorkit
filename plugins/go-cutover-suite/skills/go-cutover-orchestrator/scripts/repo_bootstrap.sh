#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  repo_bootstrap.sh --repo-path <path> --branch <branch> [--base master] [--remote origin] [--allow-dirty] [--no-push-remote]

Behavior:
  1. Fetches the base branch from the remote.
  2. Switches to the base branch and fast-forwards it.
  3. Switches to the target branch if it exists, otherwise creates it from the updated base branch.
  4. Ensures the target branch exists on the remote by default.
  5. If the repo is already on the target branch with uncommitted changes, continues on top of those changes.

Environment:
  No environment variables are required.
EOF
}

REPO_PATH=""
BRANCH=""
BASE_BRANCH="master"
REMOTE_NAME="origin"
ALLOW_DIRTY="false"
PUSH_REMOTE="true"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-path)
      REPO_PATH="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --base)
      BASE_BRANCH="${2:-}"
      shift 2
      ;;
    --remote)
      REMOTE_NAME="${2:-}"
      shift 2
      ;;
    --allow-dirty)
      ALLOW_DIRTY="true"
      shift
      ;;
    --no-push-remote)
      PUSH_REMOTE="false"
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "${REPO_PATH}" || -z "${BRANCH}" ]]; then
  usage >&2
  exit 1
fi

if [[ ! -d "${REPO_PATH}" ]]; then
  echo "Repository path does not exist: ${REPO_PATH}" >&2
  exit 2
fi

cd "${REPO_PATH}"

git rev-parse --is-inside-work-tree >/dev/null 2>&1 || {
  echo "Not a git repository: ${REPO_PATH}" >&2
  exit 3
}

CURRENT_BRANCH_INITIAL="$(git branch --show-current)"
DIRTY_WORKTREE="false"
if [[ -n "$(git status --porcelain)" ]]; then
  DIRTY_WORKTREE="true"
fi

BOOTSTRAP_MODE="normal"
if [[ "${DIRTY_WORKTREE}" == "true" ]]; then
  if [[ "${CURRENT_BRANCH_INITIAL}" == "${BRANCH}" ]]; then
    ALLOW_DIRTY="true"
    BOOTSTRAP_MODE="continue_on_dirty_target_branch"
  else
    echo "Repository has uncommitted changes on branch ${CURRENT_BRANCH_INITIAL}. Safe switch to ${BRANCH} is blocked to avoid conflicts: ${REPO_PATH}" >&2
    exit 4
  fi
fi

git fetch "${REMOTE_NAME}" "${BASE_BRANCH}"

BASE_SYNCED="false"
BRANCH_EXISTED="false"
REMOTE_BRANCH_EXISTS="false"

if [[ "${BOOTSTRAP_MODE}" != "continue_on_dirty_target_branch" ]]; then
  if git show-ref --verify --quiet "refs/heads/${BASE_BRANCH}"; then
    git switch "${BASE_BRANCH}" >/dev/null
  else
    git switch -c "${BASE_BRANCH}" --track "${REMOTE_NAME}/${BASE_BRANCH}" >/dev/null
  fi

  git pull --ff-only "${REMOTE_NAME}" "${BASE_BRANCH}" >/dev/null
  BASE_SYNCED="true"

  if git show-ref --verify --quiet "refs/heads/${BRANCH}"; then
    BRANCH_EXISTED="true"
    git switch "${BRANCH}" >/dev/null
  elif git ls-remote --exit-code --heads "${REMOTE_NAME}" "${BRANCH}" >/dev/null 2>&1; then
    BRANCH_EXISTED="true"
    REMOTE_BRANCH_EXISTS="true"
    git switch -c "${BRANCH}" --track "${REMOTE_NAME}/${BRANCH}" >/dev/null
  else
    git switch -c "${BRANCH}" "${BASE_BRANCH}" >/dev/null
  fi
else
  BRANCH_EXISTED="true"
fi

if [[ "${REMOTE_BRANCH_EXISTS}" != "true" ]] && git ls-remote --exit-code --heads "${REMOTE_NAME}" "${BRANCH}" >/dev/null 2>&1; then
  REMOTE_BRANCH_EXISTS="true"
fi

UPSTREAM_CONFIGURED="false"
if git rev-parse --abbrev-ref --symbolic-full-name '@{u}' >/dev/null 2>&1; then
  UPSTREAM_CONFIGURED="true"
fi

REMOTE_PUSHED="false"
if [[ "${PUSH_REMOTE}" == "true" ]]; then
  if [[ "${REMOTE_BRANCH_EXISTS}" == "true" ]]; then
    if [[ "${UPSTREAM_CONFIGURED}" != "true" ]]; then
      git branch --set-upstream-to="${REMOTE_NAME}/${BRANCH}" "${BRANCH}" >/dev/null
      UPSTREAM_CONFIGURED="true"
    fi
  else
    git push -u "${REMOTE_NAME}" "${BRANCH}" >/dev/null
    REMOTE_BRANCH_EXISTS="true"
    UPSTREAM_CONFIGURED="true"
    REMOTE_PUSHED="true"
  fi
fi

CURRENT_COMMIT="$(git rev-parse HEAD)"
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"

export BOOTSTRAP_REPO_PATH="${REPO_PATH}"
export BOOTSTRAP_BASE_BRANCH="${BASE_BRANCH}"
export BOOTSTRAP_BRANCH="${CURRENT_BRANCH}"
export BOOTSTRAP_BRANCH_EXISTED="${BRANCH_EXISTED}"
export BOOTSTRAP_COMMIT="${CURRENT_COMMIT}"
export BOOTSTRAP_REMOTE_NAME="${REMOTE_NAME}"
export BOOTSTRAP_REMOTE_BRANCH_EXISTS="${REMOTE_BRANCH_EXISTS}"
export BOOTSTRAP_UPSTREAM_CONFIGURED="${UPSTREAM_CONFIGURED}"
export BOOTSTRAP_REMOTE_PUSHED="${REMOTE_PUSHED}"
export BOOTSTRAP_PUSH_REMOTE="${PUSH_REMOTE}"
export BOOTSTRAP_DIRTY_WORKTREE="${DIRTY_WORKTREE}"
export BOOTSTRAP_INITIAL_BRANCH="${CURRENT_BRANCH_INITIAL}"
export BOOTSTRAP_MODE="${BOOTSTRAP_MODE}"
export BOOTSTRAP_BASE_SYNCED="${BASE_SYNCED}"

python3 - <<'PY'
import json
import os

print(json.dumps({
    "repoPath": os.environ["BOOTSTRAP_REPO_PATH"],
    "baseBranch": os.environ["BOOTSTRAP_BASE_BRANCH"],
    "branch": os.environ["BOOTSTRAP_BRANCH"],
    "branchExisted": os.environ["BOOTSTRAP_BRANCH_EXISTED"] == "true",
    "commit": os.environ["BOOTSTRAP_COMMIT"],
    "remote": os.environ["BOOTSTRAP_REMOTE_NAME"],
    "remoteBranchExists": os.environ["BOOTSTRAP_REMOTE_BRANCH_EXISTS"] == "true",
    "upstreamConfigured": os.environ["BOOTSTRAP_UPSTREAM_CONFIGURED"] == "true",
    "remotePushed": os.environ["BOOTSTRAP_REMOTE_PUSHED"] == "true",
    "pushRemote": os.environ["BOOTSTRAP_PUSH_REMOTE"] == "true",
    "dirtyWorktree": os.environ["BOOTSTRAP_DIRTY_WORKTREE"] == "true",
    "initialBranch": os.environ["BOOTSTRAP_INITIAL_BRANCH"],
    "bootstrapMode": os.environ["BOOTSTRAP_MODE"],
    "baseSynced": os.environ["BOOTSTRAP_BASE_SYNCED"] == "true",
}, ensure_ascii=False, indent=2))
PY
