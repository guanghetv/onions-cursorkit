#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  gitlab_clone_or_update.sh --repo <namespace/project> [--dest-root ~/work] [--branch <branch>] [--protocol auto|https|ssh] [--keep-namespace]

Environment:
  GITLAB_URL    Base GitLab URL, for example: https://gitlab.yc345.tv
  GITLAB_TOKEN  Optional token for HTTPS clone URLs

Behavior:
  - Clones the repo if it is missing locally
  - Fetches updates if the repo already exists
  - Optionally switches to a branch after clone or update
EOF
}

REPO_PATH=""
DEST_ROOT="${HOME}/work"
TARGET_BRANCH=""
PROTOCOL="auto"
KEEP_NAMESPACE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO_PATH="${2:-}"
      shift 2
      ;;
    --dest-root)
      DEST_ROOT="${2:-}"
      shift 2
      ;;
    --branch)
      TARGET_BRANCH="${2:-}"
      shift 2
      ;;
    --protocol)
      PROTOCOL="${2:-}"
      shift 2
      ;;
    --keep-namespace)
      KEEP_NAMESPACE="true"
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

if [[ -z "${REPO_PATH}" ]]; then
  usage >&2
  exit 1
fi

GITLAB_URL="${GITLAB_URL:-https://gitlab.yc345.tv}"
GITLAB_URL="${GITLAB_URL%/}"
HOST_ONLY="${GITLAB_URL#https://}"
HOST_ONLY="${HOST_ONLY#http://}"

build_clone_url() {
  local mode="$1"
  if [[ "${mode}" == "ssh" ]]; then
    printf 'git@%s:%s.git' "${HOST_ONLY}" "${REPO_PATH}"
    return
  fi

  if [[ -n "${GITLAB_TOKEN:-}" ]]; then
    printf 'https://oauth2:%s@%s/%s.git' "${GITLAB_TOKEN}" "${HOST_ONLY}" "${REPO_PATH}"
    return
  fi

  printf '%s/%s.git' "${GITLAB_URL}" "${REPO_PATH}"
}

if [[ "${PROTOCOL}" == "auto" ]]; then
  if [[ -n "${GITLAB_TOKEN:-}" ]]; then
    CLONE_URL="$(build_clone_url https)"
  else
    CLONE_URL="$(build_clone_url ssh)"
  fi
else
  CLONE_URL="$(build_clone_url "${PROTOCOL}")"
fi

mkdir -p "${DEST_ROOT}"

if [[ "${KEEP_NAMESPACE}" == "true" ]]; then
  LOCAL_PATH="${DEST_ROOT}/${REPO_PATH}"
else
  LOCAL_PATH="${DEST_ROOT}/${REPO_PATH##*/}"
fi

LOCAL_DIR="$(dirname "${LOCAL_PATH}")"
mkdir -p "${LOCAL_DIR}"

ACTION="updated"
if [[ -d "${LOCAL_PATH}/.git" ]]; then
  git -C "${LOCAL_PATH}" fetch --all --prune >/dev/null
else
  git clone "${CLONE_URL}" "${LOCAL_PATH}" >/dev/null
  ACTION="cloned"
fi

if [[ -n "${TARGET_BRANCH}" ]]; then
  if git -C "${LOCAL_PATH}" show-ref --verify --quiet "refs/heads/${TARGET_BRANCH}"; then
    git -C "${LOCAL_PATH}" switch "${TARGET_BRANCH}" >/dev/null
  elif git -C "${LOCAL_PATH}" ls-remote --exit-code --heads origin "${TARGET_BRANCH}" >/dev/null 2>&1; then
    git -C "${LOCAL_PATH}" switch -c "${TARGET_BRANCH}" --track "origin/${TARGET_BRANCH}" >/dev/null
  fi
fi

CURRENT_BRANCH="$(git -C "${LOCAL_PATH}" rev-parse --abbrev-ref HEAD)"
CURRENT_COMMIT="$(git -C "${LOCAL_PATH}" rev-parse HEAD)"

export GITLAB_REPO_PATH="${REPO_PATH}"
export GITLAB_LOCAL_PATH="${LOCAL_PATH}"
export GITLAB_ACTION="${ACTION}"
export GITLAB_BRANCH="${CURRENT_BRANCH}"
export GITLAB_COMMIT="${CURRENT_COMMIT}"
export GITLAB_CLONE_URL="${CLONE_URL}"

python3 - <<'PY'
import json
import os

print(json.dumps({
    "repo": os.environ["GITLAB_REPO_PATH"],
    "localPath": os.environ["GITLAB_LOCAL_PATH"],
    "action": os.environ["GITLAB_ACTION"],
    "branch": os.environ["GITLAB_BRANCH"],
    "commit": os.environ["GITLAB_COMMIT"],
    "cloneUrl": os.environ["GITLAB_CLONE_URL"],
}, ensure_ascii=False, indent=2))
PY
