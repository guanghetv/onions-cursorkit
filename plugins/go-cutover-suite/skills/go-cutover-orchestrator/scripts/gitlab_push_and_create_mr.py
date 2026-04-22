#!/usr/bin/env python3
"""
gitlab_push_and_create_mr.py

在真正的 push 动作里使用 GitLab push options 创建指向 dev 的 MR。
适用于已经有代码改动、即将首次或再次把分支推到远端的场景。
不依赖 GITLAB_TOKEN；如提供 GITLAB_TOKEN，可在 push 后补查 MR 链接。
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from gitlab_create_mr import (  # type: ignore
    MR_URL_RE,
    api_find_existing_mr,
    build_create_url,
    get_current_remote,
    normalize_remote_to_web,
)


def run_git(args, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Push branch and create GitLab MR targeting dev")
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--branch", required=True, help="source branch")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--gitlab-url", default=os.environ.get("GITLAB_URL", "https://gitlab.yc345.tv"))
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    parser.add_argument("--set-upstream", action="store_true")
    args = parser.parse_args()

    repo_path = str(Path(args.repo_path).resolve())
    token = os.environ.get("GITLAB_TOKEN", "").strip()

    try:
        remote_url = get_current_remote(repo_path, args.remote)
        web_base, project_path = normalize_remote_to_web(remote_url)
        gitlab_url = args.gitlab_url.rstrip("/")
        create_url = build_create_url(web_base, project_path, args.branch, args.target_branch)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({
            "status": "blocked",
            "reason": f"prepare_failed: {exc}",
            "url": "",
            "createUrl": "",
        }, ensure_ascii=False))
        return 1

    cmd = ["push"]
    if args.set_upstream:
        cmd.append("-u")
    cmd.extend([
        args.remote,
        f"HEAD:{args.branch}",
        "-o", "merge_request.create",
        "-o", f"merge_request.target={args.target_branch}",
    ])
    if args.title.strip():
        cmd.extend(["-o", f"merge_request.title={args.title.strip()}"])
    if args.description.strip():
        cmd.extend(["-o", f"merge_request.description={args.description.strip()}"])

    completed = run_git(cmd, repo_path)
    output = (completed.stdout or "") + (completed.stderr or "")
    mr_url_match = MR_URL_RE.search(output)

    if completed.returncode != 0:
        print(json.dumps({
            "status": "blocked",
            "reason": "git_push_failed",
            "url": "",
            "createUrl": create_url,
            "method": "git-push-options",
            "projectPath": project_path,
            "sourceBranch": args.branch,
            "targetBranch": args.target_branch,
            "output": output,
        }, ensure_ascii=False))
        return 1

    if mr_url_match:
        print(json.dumps({
            "status": "created",
            "url": mr_url_match.group(0),
            "createUrl": create_url,
            "method": "git-push-options",
            "projectPath": project_path,
            "sourceBranch": args.branch,
            "targetBranch": args.target_branch,
            "output": output,
        }, ensure_ascii=False))
        return 0

    if token:
        existing, err = api_find_existing_mr(gitlab_url, project_path, args.branch, args.target_branch, token)
        if existing:
            print(json.dumps({
                "status": "exists",
                "url": existing.get("web_url", ""),
                "createUrl": create_url,
                "method": "git-push-options+gitlab-api-get",
                "projectPath": project_path,
                "sourceBranch": args.branch,
                "targetBranch": args.target_branch,
                "output": output,
            }, ensure_ascii=False))
            return 0
        reason = err or "mr_link_not_returned"
        print(json.dumps({
            "status": "creation_link_only",
            "reason": reason,
            "url": "",
            "createUrl": create_url,
            "method": "git-push-options",
            "projectPath": project_path,
            "sourceBranch": args.branch,
            "targetBranch": args.target_branch,
            "output": output,
        }, ensure_ascii=False))
        return 0

    print(json.dumps({
        "status": "creation_link_only",
        "reason": "push_succeeded_but_gitlab_did_not_emit_mr_url",
        "url": "",
        "createUrl": create_url,
        "method": "git-push-options",
        "projectPath": project_path,
        "sourceBranch": args.branch,
        "targetBranch": args.target_branch,
        "output": output,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
