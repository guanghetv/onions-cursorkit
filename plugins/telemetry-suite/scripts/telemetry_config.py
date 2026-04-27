#!/usr/bin/env python3
"""Shared local configuration helpers for telemetry-suite.

Config precedence:
1. ~/.cursor/telemetry-suite/config.json (private machine config, may contain secrets)
2. ./.cursor/telemetry-suite.local.json (workspace override, should stay uncommitted)

The returned config keeps backward-compatible top-level keys used by legacy stage scripts:
GITLAB_URL, GITLAB_TOKEN, workspaceRoot, FEISHU_BASE_TOKEN, FEISHU_TABLE_ID, FEISHU_VIEW_ID.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
DEFAULT_ARTIFACT_DIR = "./telemetry-audit"
DEFAULT_FEISHU_TABLE_ID = "tblBJH3FuUHuhrGO"
DEFAULT_FEISHU_VIEW_ID = "vewOpKcL8Y"


def private_config_path() -> Path:
    return Path.home() / ".cursor" / "telemetry-suite" / "config.json"


def workspace_config_path(workspace_root: str | Path | None = None) -> Path:
    root = Path(workspace_root or os.getcwd()).expanduser().resolve()
    return root / ".cursor" / "telemetry-suite.local.json"


def load_json_if_exists(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def normalize_config(cfg: dict[str, Any]) -> dict[str, Any]:
    gitlab = cfg.get("gitlab") if isinstance(cfg.get("gitlab"), dict) else {}
    feishu = cfg.get("feishu") if isinstance(cfg.get("feishu"), dict) else {}
    workspace = cfg.get("workspace") if isinstance(cfg.get("workspace"), dict) else {}

    normalized = dict(cfg)
    normalized.setdefault("GITLAB_URL", gitlab.get("url") or DEFAULT_GITLAB_URL)
    normalized.setdefault("GITLAB_TOKEN", gitlab.get("token") or os.environ.get("GITLAB_TOKEN", ""))
    normalized.setdefault("workspaceRoot", workspace.get("root") or str(Path.cwd()))
    normalized.setdefault("artifactDir", workspace.get("artifactDir") or DEFAULT_ARTIFACT_DIR)
    normalized.setdefault("FEISHU_BASE_TOKEN", feishu.get("baseToken") or os.environ.get("FEISHU_BASE_TOKEN", ""))
    normalized.setdefault("FEISHU_TABLE_ID", feishu.get("tableId") or DEFAULT_FEISHU_TABLE_ID)
    normalized.setdefault("FEISHU_VIEW_ID", feishu.get("viewId") or DEFAULT_FEISHU_VIEW_ID)
    return normalized


def load_config(workspace_root: str | Path | None = None) -> dict[str, Any]:
    cfg = load_json_if_exists(private_config_path())
    workspace_cfg = load_json_if_exists(workspace_config_path(workspace_root))
    return normalize_config(deep_merge(cfg, workspace_cfg))


def save_private_config(cfg: dict[str, Any]) -> Path:
    path = private_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")
    try:
        path.chmod(0o600)
    except OSError:
        pass
    return path


def example_config() -> dict[str, Any]:
    return {
        "gitlab": {
            "url": DEFAULT_GITLAB_URL,
            "token": "",
        },
        "feishu": {
            "baseToken": "",
            "tableId": DEFAULT_FEISHU_TABLE_ID,
            "viewId": DEFAULT_FEISHU_VIEW_ID,
        },
        "workspace": {
            "root": str(Path.cwd()),
            "artifactDir": DEFAULT_ARTIFACT_DIR,
        },
        "runtime": {
            "auditWorkerConcurrency": 3,
            "instrumentWorkerConcurrency": 1,
        },
    }
