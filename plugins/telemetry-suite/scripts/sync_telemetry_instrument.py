#!/usr/bin/env python3
"""
sync_telemetry_instrument.py - 从 GitLab 拉取 telemetry-instrument skill，
同步到本地 references/telemetry-instrument.md。
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from pathlib import Path

from telemetry_config import private_config_path

DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
DEFAULT_PROJECT = "backend/skills"
DEFAULT_FILE_PATH = "skills/telemetry-instrument/SKILL.md"
DEFAULT_REF = "main"
CONFIG_PATH = private_config_path()
OUTPUT_PATH = Path(__file__).parent.parent / "references" / "telemetry-instrument.md"


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def fetch_remote_content(gitlab_url: str, token: str, project: str, file_path: str, ref: str) -> str:
    url = (
        f"{gitlab_url.rstrip('/')}/api/v4/projects/{urllib.parse.quote_plus(project)}"
        f"/repository/files/{urllib.parse.quote_plus(file_path)}/raw?ref={urllib.parse.quote_plus(ref)}"
    )
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token, "Accept": "text/plain"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)
        if not content.endswith("\n"):
            f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="同步远端 telemetry-instrument 到本地 references")
    parser.add_argument("--project", default=DEFAULT_PROJECT)
    parser.add_argument("--file-path", default=DEFAULT_FILE_PATH)
    parser.add_argument("--ref", default=DEFAULT_REF)
    parser.add_argument("--output-file", default=str(OUTPUT_PATH))
    args = parser.parse_args()

    cfg = load_config()
    token = (cfg.get("GITLAB_TOKEN") or "").strip()
    gitlab_url = (cfg.get("GITLAB_URL") or DEFAULT_GITLAB_URL).strip()
    if not token:
        print("[ERROR] Missing GITLAB_TOKEN in telemetry-resolve-repos config.", file=sys.stderr)
        return 2

    content = fetch_remote_content(
        gitlab_url=gitlab_url,
        token=token,
        project=args.project,
        file_path=args.file_path,
        ref=args.ref,
    )
    output_file = Path(args.output_file).expanduser().resolve()
    write_file(output_file, content)
    print(
        json.dumps(
            {
                "output_file": str(output_file),
                "project": args.project,
                "file_path": args.file_path,
                "ref": args.ref,
                "line_count": len(content.splitlines()),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
