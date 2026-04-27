#!/usr/bin/env python3
"""Unified utility entrypoint for telemetry-suite."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

from telemetry_config import example_config, load_config, private_config_path, save_private_config

SCRIPT_DIR = Path(__file__).resolve().parent


def run(cmd: list[str], timeout: int = 30) -> tuple[bool, str]:
    try:
        proc = subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)
        output = (proc.stdout or "") + ("\n" + proc.stderr if proc.stderr else "")
        return proc.returncode == 0, output.strip()
    except Exception as exc:
        return False, str(exc)


def command_exists(name: str) -> bool:
    return shutil.which(name) is not None


def cmd_setup(args: argparse.Namespace) -> int:
    cfg = example_config()
    if args.gitlab_url:
        cfg["gitlab"]["url"] = args.gitlab_url
    if args.gitlab_token:
        cfg["gitlab"]["token"] = args.gitlab_token
    if args.feishu_base_token:
        cfg["feishu"]["baseToken"] = args.feishu_base_token
    if args.feishu_table_id:
        cfg["feishu"]["tableId"] = args.feishu_table_id
    if args.feishu_view_id:
        cfg["feishu"]["viewId"] = args.feishu_view_id
    if args.workspace_root:
        cfg["workspace"]["root"] = str(Path(args.workspace_root).expanduser().resolve())

    if args.write:
        path = save_private_config(cfg)
        print(json.dumps({"config_path": str(path), "written": True}, ensure_ascii=False, indent=2))
    else:
        print(json.dumps({"config_path": str(private_config_path()), "example": cfg}, ensure_ascii=False, indent=2))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    cfg = load_config(args.workspace_root)
    checks: list[dict[str, object]] = []

    def add(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"name": name, "ok": ok, "detail": detail})

    for binary in ["python3", "git", "node", "npm", "npx", "lark-cli", "glab", "agent"]:
        add(f"binary:{binary}", command_exists(binary), shutil.which(binary) or "missing")

    ok, out = run(["lark-cli", "auth", "status"], timeout=30) if command_exists("lark-cli") else (False, "lark-cli missing")
    add("feishu:lark-cli auth status", ok, out[-1000:])

    ok, out = run(["glab", "auth", "status", "--hostname", cfg.get("GITLAB_URL", "").replace("https://", "")], timeout=30) if command_exists("glab") else (False, "glab missing")
    add("gitlab:glab auth status", ok, out[-1000:])

    ok, out = run(["agent", "-p", "--yolo", "--output-format", "json", '只输出这个 JSON：{"ok":true}'], timeout=60) if command_exists("agent") else (False, "agent missing")
    add("cursor:agent cli json smoke", ok and "ok" in out, out[-1000:])

    add("config:private exists", private_config_path().exists(), str(private_config_path()))
    add("config:gitlab token", bool((cfg.get("GITLAB_TOKEN") or "").strip()), "GITLAB_TOKEN or gitlab.token")
    add("config:feishu base token", bool((cfg.get("FEISHU_BASE_TOKEN") or "").strip()), "FEISHU_BASE_TOKEN or feishu.baseToken")

    payload = {
        "ok": all(item["ok"] for item in checks),
        "config_path": str(private_config_path()),
        "checks": checks,
        "docs": {
            "feishu_cli_install": "https://open.feishu.cn/document/no_class/mcp-archive/feishu-cli-installation-guide.md",
            "feishu_cli_docs": "https://open.feishu.cn/document/mcp_open_tools/feishu-cli-let-ai-actually-do-your-work-in-feishu",
        },
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload["ok"] else 2


def run_script(script_name: str, argv: list[str]) -> int:
    script_path = SCRIPT_DIR / script_name
    sys.argv = [str(script_path), *argv]
    spec = importlib.util.spec_from_file_location(script_path.stem, script_path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if hasattr(module, "main"):
        return int(module.main())
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="telemetry-suite utility CLI")
    sub = parser.add_subparsers(dest="cmd", required=True)

    setup = sub.add_parser("setup", help="print or write local telemetry-suite config")
    setup.add_argument("--write", action="store_true")
    setup.add_argument("--gitlab-url", default="")
    setup.add_argument("--gitlab-token", default="")
    setup.add_argument("--feishu-base-token", default="")
    setup.add_argument("--feishu-table-id", default="")
    setup.add_argument("--feishu-view-id", default="")
    setup.add_argument("--workspace-root", default="")
    setup.set_defaults(func=cmd_setup)

    doctor = sub.add_parser("doctor", help="check local dependencies and credentials")
    doctor.add_argument("--workspace-root", default="")
    doctor.set_defaults(func=cmd_doctor)

    passthrough = {
        "fetch-service-inventory": "fetch_service_inventory.py",
        "resolve-repos": "resolve_repos.py",
        "audit-from-csv": "audit_from_csv.py",
        "instrument-from-csv": "instrument_from_csv.py",
    }
    for name, script in passthrough.items():
        p = sub.add_parser(name, help=f"pass through to {script}", add_help=False)
        p.add_argument("args", nargs=argparse.REMAINDER)
        p.set_defaults(func=lambda args, s=script: run_script(s, args.args))

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
