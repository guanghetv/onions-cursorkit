#!/usr/bin/env python3
"""
gitlab_create_mr.py

为 GitLab 仓库的 source branch 自动创建或探测一个指向 target branch 的 Merge Request。
优先使用 git push options；如提供 GITLAB_TOKEN，则再尝试用 GitLab API 查询/创建并补充直达链接。
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple


MR_URL_RE = re.compile(r"https?://[^\s]+/-/merge_requests/\d+")


def run_git(args, cwd: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        capture_output=True,
    )


def normalize_remote_to_web(remote_url: str) -> Tuple[str, str]:
    remote_url = remote_url.strip()
    if remote_url.startswith("git@"):
        host_path = remote_url.split("@", 1)[1]
        host, path = host_path.split(":", 1)
        return f"https://{host}", path.removesuffix(".git")
    if remote_url.startswith("ssh://"):
        parsed = urllib.parse.urlparse(remote_url)
        return f"https://{parsed.hostname}", parsed.path.lstrip("/").removesuffix(".git")
    if remote_url.startswith("http://") or remote_url.startswith("https://"):
        parsed = urllib.parse.urlparse(remote_url)
        return f"{parsed.scheme}://{parsed.netloc}", parsed.path.lstrip("/").removesuffix(".git")
    raise ValueError(f"Unsupported remote URL: {remote_url}")


def build_create_url(web_base: str, project_path: str, source_branch: str, target_branch: str) -> str:
    query = urllib.parse.urlencode(
        {
            "merge_request[source_branch]": source_branch,
            "merge_request[target_branch]": target_branch,
        }
    )
    return f"{web_base}/{project_path}/-/merge_requests/new?{query}"


def api_request(
    method: str,
    url: str,
    token: str,
    data: Optional[dict] = None,
) -> Tuple[Optional[dict], Optional[str]]:
    body = None
    headers = {
        "PRIVATE-TOKEN": token,
        "Content-Type": "application/json",
    }
    if data is not None:
        body = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            payload = resp.read().decode("utf-8")
            return json.loads(payload), None
    except urllib.error.HTTPError as exc:
        try:
            payload = exc.read().decode("utf-8")
        except Exception:  # noqa: BLE001
            payload = exc.reason if hasattr(exc, "reason") else str(exc)
        return None, f"http_{exc.code}: {payload}"
    except Exception as exc:  # noqa: BLE001
        return None, str(exc)


def api_find_existing_mr(
    gitlab_url: str,
    project_path: str,
    source_branch: str,
    target_branch: str,
    token: str,
) -> Tuple[Optional[dict], Optional[str]]:
    encoded_project = urllib.parse.quote_plus(project_path)
    params = urllib.parse.urlencode(
        {
            "state": "opened",
            "source_branch": source_branch,
            "target_branch": target_branch,
        }
    )
    url = f"{gitlab_url}/api/v4/projects/{encoded_project}/merge_requests?{params}"
    data, err = api_request("GET", url, token)
    if err:
        return None, err
    if isinstance(data, list) and data:
        return data[0], None
    return None, None


def api_create_mr(
    gitlab_url: str,
    project_path: str,
    source_branch: str,
    target_branch: str,
    token: str,
    title: Optional[str],
    description: Optional[str],
) -> Tuple[Optional[dict], Optional[str]]:
    encoded_project = urllib.parse.quote_plus(project_path)
    url = f"{gitlab_url}/api/v4/projects/{encoded_project}/merge_requests"
    payload = {
        "source_branch": source_branch,
        "target_branch": target_branch,
        "title": title or f"{source_branch} -> {target_branch}",
        "description": description or "",
        "remove_source_branch": False,
    }
    return api_request("POST", url, token, payload)


def push_options_create_mr(
    repo_path: str,
    source_branch: str,
    target_branch: str,
    title: Optional[str],
    description: Optional[str],
    remote: str,
) -> Tuple[bool, str, str]:
    cmd = [
        "push",
        remote,
        source_branch,
        "-o",
        "merge_request.create",
        "-o",
        f"merge_request.target={target_branch}",
    ]
    if title:
        cmd.extend(["-o", f"merge_request.title={title}"])
    if description:
        cmd.extend(["-o", f"merge_request.description={description}"])
    completed = run_git(cmd, repo_path)
    output = (completed.stdout or "") + (completed.stderr or "")
    return completed.returncode == 0, output, completed.stderr or ""


def get_current_remote(repo_path: str, remote: str) -> str:
    cp = run_git(["remote", "get-url", remote], repo_path)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or f"remote {remote} not found")
    return cp.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Create or detect GitLab Merge Request")
    parser.add_argument("--repo-path", required=True)
    parser.add_argument("--branch", required=True, help="source branch")
    parser.add_argument("--target-branch", default="dev")
    parser.add_argument("--gitlab-url", default=os.environ.get("GITLAB_URL", "https://gitlab.yc345.tv"))
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    args = parser.parse_args()

    repo_path = str(Path(args.repo_path).resolve())
    token = os.environ.get("GITLAB_TOKEN", "").strip()

    try:
        remote_url = get_current_remote(repo_path, args.remote)
        web_base, project_path = normalize_remote_to_web(remote_url)
        gitlab_url = args.gitlab_url.rstrip("/")
        create_url = build_create_url(web_base, project_path, args.branch, args.target_branch)
    except Exception as exc:  # noqa: BLE001
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": f"prepare_failed: {exc}",
                    "url": "",
                    "createUrl": "",
                },
                ensure_ascii=False,
            )
        )
        return 1

    # 先查已有 MR，避免重复创建
    if token:
        existing, err = api_find_existing_mr(gitlab_url, project_path, args.branch, args.target_branch, token)
        if existing:
            print(
                json.dumps(
                    {
                        "status": "exists",
                        "url": existing.get("web_url", ""),
                        "createUrl": create_url,
                        "method": "gitlab-api-get",
                        "projectPath": project_path,
                        "sourceBranch": args.branch,
                        "targetBranch": args.target_branch,
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        api_probe_error = err
    else:
        api_probe_error = "missing_gitlab_token_for_after_the_fact_lookup"

    push_ok, push_output, _ = push_options_create_mr(
        repo_path=repo_path,
        source_branch=args.branch,
        target_branch=args.target_branch,
        title=args.title.strip() or None,
        description=args.description.strip() or None,
        remote=args.remote,
    )

    mr_url_match = MR_URL_RE.search(push_output)
    if push_ok and mr_url_match:
        print(
            json.dumps(
                {
                    "status": "created",
                    "url": mr_url_match.group(0),
                    "createUrl": create_url,
                    "method": "git-push-options",
                    "projectPath": project_path,
                    "sourceBranch": args.branch,
                    "targetBranch": args.target_branch,
                    "output": push_output,
                },
                ensure_ascii=False,
            )
        )
        return 0

    if token:
        existing, err = api_find_existing_mr(gitlab_url, project_path, args.branch, args.target_branch, token)
        if existing:
            print(
                json.dumps(
                    {
                        "status": "exists",
                        "url": existing.get("web_url", ""),
                        "createUrl": create_url,
                        "method": "gitlab-api-get-after-push",
                        "projectPath": project_path,
                        "sourceBranch": args.branch,
                        "targetBranch": args.target_branch,
                        "output": push_output,
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        created, create_err = api_create_mr(
            gitlab_url=gitlab_url,
            project_path=project_path,
            source_branch=args.branch,
            target_branch=args.target_branch,
            token=token,
            title=args.title.strip() or None,
            description=args.description.strip() or None,
        )
        if created:
            print(
                json.dumps(
                    {
                        "status": "created",
                        "url": created.get("web_url", ""),
                        "createUrl": create_url,
                        "method": "gitlab-api-post",
                        "projectPath": project_path,
                        "sourceBranch": args.branch,
                        "targetBranch": args.target_branch,
                        "output": push_output,
                    },
                    ensure_ascii=False,
                )
            )
            return 0
        reason = create_err or err or api_probe_error or "mr_create_failed"
        print(
            json.dumps(
                {
                    "status": "blocked",
                    "reason": reason,
                    "url": "",
                    "createUrl": create_url,
                    "method": "git-push-options+gitlab-api",
                    "projectPath": project_path,
                    "sourceBranch": args.branch,
                    "targetBranch": args.target_branch,
                    "output": push_output,
                },
                ensure_ascii=False,
            )
        )
        return 1

    status = "creation_link_only" if push_ok else "blocked"
    reason = api_probe_error if status == "creation_link_only" else "git_push_options_failed"
    if status == "creation_link_only" and "Everything up-to-date" in push_output:
        reason = "no_remote_update_for_push_options; create MR during the real push step or use the createUrl"
    print(
        json.dumps(
            {
                "status": status,
                "reason": reason,
                "url": mr_url_match.group(0) if mr_url_match else "",
                "createUrl": create_url,
                "method": "git-push-options",
                "projectPath": project_path,
                "sourceBranch": args.branch,
                "targetBranch": args.target_branch,
                "output": push_output,
            },
            ensure_ascii=False,
        )
    )
    return 0 if status == "creation_link_only" else 1


if __name__ == "__main__":
    sys.exit(main())
