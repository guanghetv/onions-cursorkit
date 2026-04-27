#!/usr/bin/env python3
"""
gitlab_token.py - GitLab Personal Access Token 的保存、读取与校验工具。

职责：
1. 读取本地保存的 GitLab PAT
2. 调用 GitLab API 校验 token 是否有效
3. 保存新 token，并将配置写入本机私有 telemetry-suite config.json
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

from telemetry_config import private_config_path, load_config as load_suite_config, save_private_config

DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
DEFAULT_TOKEN_SCOPES = ["read_api", "read_repository"]
CONFIG_PATH = private_config_path()


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_config(cfg: dict) -> None:
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)
        f.write("\n")
    try:
        CONFIG_PATH.chmod(0o600)
    except OSError:
        pass


def build_manual_setup_plan(gitlab_url: str) -> dict:
    return {
        "gitlab_url": gitlab_url,
        "token_url": f"{gitlab_url}/-/user_settings/personal_access_tokens",
        "scopes": DEFAULT_TOKEN_SCOPES,
        "save_command": f"python3 {Path(__file__).resolve()} --save-token <TOKEN>",
        "notes": [
            "推荐至少勾选 read_api",
            "如果后续要直接读仓库或 clone，可再加 read_repository",
            "token 只保存在本机 skill 配置里，不要提交进 git 仓库",
        ],
    }


def api_get_json(gitlab_url: str, token: str, path: str) -> dict:
    req = urllib.request.Request(
        f"{gitlab_url}{path}",
        headers={
            "PRIVATE-TOKEN": token,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def validate_token(gitlab_url: str, token: str) -> tuple[bool, dict]:
    try:
        data = api_get_json(gitlab_url, token, "/api/v4/user")
        return True, data
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "ignore")
        print(f"[ERROR] GitLab token validation failed: HTTP {e.code} {detail}", file=sys.stderr)
        return False, {}
    except Exception as e:
        print(f"[ERROR] GitLab token validation failed: {e}", file=sys.stderr)
        return False, {}


def main() -> int:
    parser = argparse.ArgumentParser(description="获取、验证或保存 GitLab Personal Access Token")
    parser.add_argument("--save-token", default="", help="保存并验证新的 GitLab PAT")
    parser.add_argument("--gitlab-url", default="", help="覆盖 GitLab URL")
    args = parser.parse_args()

    cfg = load_config()
    gitlab_url = args.gitlab_url or cfg.get("GITLAB_URL", DEFAULT_GITLAB_URL)

    if args.save_token.strip():
        token = args.save_token.strip()
        ok, user = validate_token(gitlab_url, token)
        if not ok:
            print("[ERROR] Provided GitLab token is invalid.", file=sys.stderr)
            return 3
        cfg["GITLAB_URL"] = gitlab_url
        cfg["GITLAB_TOKEN"] = token
        save_config(cfg)
        print("[OK] GitLab token saved and validated.")
        print(json.dumps({"username": user.get("username"), "name": user.get("name")}, ensure_ascii=False))
        return 0

    existing_token = (cfg.get("GITLAB_TOKEN") or "").strip()
    if existing_token:
        print(f"[INFO] Found existing GitLab token: {existing_token[:8]}...")
        ok, user = validate_token(gitlab_url, existing_token)
        if ok:
            print("[OK] GitLab token is valid.")
            print(json.dumps({"username": user.get("username"), "name": user.get("name")}, ensure_ascii=False))
            return 0
        print("[WARN] GitLab token is invalid or expired.")

    print("[ACTION] MANUAL_TOKEN_NEEDED")
    print(json.dumps(build_manual_setup_plan(gitlab_url), ensure_ascii=False))
    return 2


if __name__ == "__main__":
    sys.exit(main())
