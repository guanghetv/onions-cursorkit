#!/usr/bin/env python3
"""
resolve_repos.py - 读取 service-inventory.json，调用 GitLab API 批量解析仓库，
并生成中文列的 repo-resolution.csv。
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from telemetry_config import private_config_path, load_config as load_suite_config

CONFIG_PATH = private_config_path()
DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
CSV_COLUMNS = [
    "服务名称",
    "命名空间",
    "业务归属",
    "编程语言",
    "运行环境",
    "包含正式环境",
    "仓库检索词",
    "匹配状态",
    "匹配仓库名",
    "匹配仓库地址",
    "候选仓库地址",
    "置信度",
    "人工确认仓库名",
    "人工确认仓库地址",
    "本地仓库路径",
    "备注",
]


def row_key(service_name: str, namespace: str) -> tuple[str, str]:
    return ((service_name or "").strip(), (namespace or "").strip())


def load_config() -> dict:
    return load_suite_config()


def load_inventory(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    return payload.get("records", [])


def load_existing_csv(path: Path) -> dict[tuple[str, str], dict]:
    if not path.exists():
        return {}
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = {}
        for row in reader:
            key = row_key(row.get("服务名称", ""), row.get("命名空间", ""))
            if key[0]:
                rows[key] = row
        return rows


def api_get_json(gitlab_url: str, token: str, path: str) -> list[dict]:
    req = urllib.request.Request(
        f"{gitlab_url}{path}",
        headers={"PRIVATE-TOKEN": token, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def search_projects(gitlab_url: str, token: str, service_name: str) -> list[dict]:
    query = urllib.parse.quote(service_name)
    path = (
        "/api/v4/projects"
        f"?search={query}"
        "&simple=true"
        "&per_page=100"
        "&order_by=last_activity_at"
        "&sort=desc"
    )
    return api_get_json(gitlab_url, token, path)


def normalize(text: str) -> str:
    return (text or "").strip().lower()


def dedupe_candidates(projects: list[dict]) -> list[dict]:
    seen = set()
    result = []
    for project in projects:
        url = project.get("web_url") or ""
        if not url or url in seen:
            continue
        seen.add(url)
        result.append(project)
    return result


def rank_projects(service_name: str, projects: list[dict]) -> tuple[list[dict], list[dict]]:
    key = normalize(service_name)
    exact = []
    partial = []
    others = []
    for project in dedupe_candidates(projects):
        name = normalize(project.get("name", ""))
        path = normalize(project.get("path", ""))
        namespace_path = normalize(project.get("path_with_namespace", ""))
        if key in {name, path}:
            exact.append(project)
        elif key in name or key in path or key in namespace_path:
            partial.append(project)
        else:
            others.append(project)
    return exact, partial + others


def build_base_row(item: dict) -> dict:
    return {
        "服务名称": (item.get("service_name") or "").strip(),
        "命名空间": (item.get("namespace") or "").strip(),
        "业务归属": (item.get("business_owner") or "").strip(),
        "编程语言": (item.get("programming_language") or "").strip(),
        "运行环境": (item.get("runtime_environment") or "").strip(),
        "包含正式环境": (item.get("contains_production_env") or "").strip(),
        "仓库检索词": (item.get("service_name") or "").strip(),
        "匹配状态": "",
        "匹配仓库名": "",
        "匹配仓库地址": "",
        "候选仓库地址": "",
        "置信度": "",
        "人工确认仓库名": "",
        "人工确认仓库地址": "",
        "本地仓库路径": "",
        "备注": "",
    }


def build_row(item: dict, projects: list[dict]) -> dict:
    row = build_base_row(item)
    exact, ranked_candidates = rank_projects(row["服务名称"], projects)
    if len(exact) == 1:
        project = exact[0]
        row.update(
            {
                "匹配状态": "自动匹配",
                "匹配仓库名": project.get("path") or project.get("name") or "",
                "匹配仓库地址": project.get("web_url") or "",
                "置信度": "高",
                "备注": "唯一完全同名仓库，自动通过",
            }
        )
        return row

    candidates = ranked_candidates[:5]
    if exact and len(exact) > 1:
        candidates = exact[:5]
        row["备注"] = "存在多个完全同名仓库候选，需人工确认"
        row["置信度"] = "中"
    elif candidates:
        row["备注"] = "未找到唯一完全同名仓库，已给出候选"
        row["置信度"] = "中"
    else:
        row["备注"] = "GitLab API 搜索未命中可信候选"
        row["置信度"] = "无"

    row["匹配状态"] = "待确认" if candidates else "未找到"
    row["候选仓库地址"] = " | ".join(
        project.get("web_url", "") for project in candidates if project.get("web_url")
    )
    return row


def maybe_reuse_existing(existing: dict | None, item: dict) -> dict | None:
    if not existing:
        return None
    merged = build_base_row(item)
    for column in CSV_COLUMNS:
        if column in {"服务名称", "命名空间", "业务归属", "编程语言", "运行环境", "包含正式环境", "仓库检索词"}:
            continue
        merged[column] = existing.get(column, merged.get(column, ""))
    if existing.get("人工确认仓库地址"):
        return merged
    if existing.get("匹配状态") == "自动匹配" and existing.get("匹配仓库地址"):
        return merged
    return None


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for row in rows:
            writer.writerow({column: row.get(column, "") for column in CSV_COLUMNS})


def main() -> int:
    parser = argparse.ArgumentParser(description="读取 service-inventory.json 并生成中文 repo-resolution.csv")
    parser.add_argument("--inventory-file", required=True, help="service-inventory.json 路径")
    parser.add_argument("--output-csv", required=True, help="repo-resolution.csv 输出路径")
    parser.add_argument("--gitlab-url", default="", help="覆盖 GitLab URL")
    parser.add_argument("--limit", type=int, default=0, help="仅处理前 N 个服务，0 表示全部")
    args = parser.parse_args()

    cfg = load_config()
    gitlab_url = args.gitlab_url or cfg.get("GITLAB_URL", DEFAULT_GITLAB_URL)
    token = (cfg.get("GITLAB_TOKEN") or "").strip()
    if not token:
        print("[ERROR] Missing GITLAB_TOKEN in ~/.cursor/telemetry-suite/config.json or environment", file=sys.stderr)
        return 2

    inventory_file = Path(args.inventory_file).expanduser().resolve()
    output_csv = Path(args.output_csv).expanduser().resolve()

    records = load_inventory(inventory_file)
    if args.limit > 0:
        records = records[: args.limit]

    existing_rows = load_existing_csv(output_csv)
    result_rows = []
    auto_matched = 0
    needs_confirm = 0
    not_found = 0
    reused = 0

    for item in records:
        service_name = (item.get("service_name") or "").strip()
        namespace = (item.get("namespace") or "").strip()
        if not service_name:
            continue

        reused_row = maybe_reuse_existing(existing_rows.get(row_key(service_name, namespace)), item)
        if reused_row:
            result_rows.append(reused_row)
            reused += 1
            if reused_row.get("匹配状态") == "自动匹配":
                auto_matched += 1
            elif reused_row.get("匹配状态") == "待确认":
                needs_confirm += 1
            elif reused_row.get("匹配状态") == "未找到":
                not_found += 1
            continue

        try:
            projects = search_projects(gitlab_url, token, service_name)
        except urllib.error.HTTPError as e:
            detail = e.read().decode("utf-8", "ignore")
            row = build_base_row(item)
            row.update(
                {
                    "匹配状态": "未找到",
                    "置信度": "无",
                    "备注": f"GitLab API 错误: HTTP {e.code} {detail[:120]}",
                }
            )
        except Exception as e:
            row = build_base_row(item)
            row.update(
                {
                    "匹配状态": "未找到",
                    "置信度": "无",
                    "备注": f"GitLab API 请求失败: {e}",
                }
            )
        else:
            row = build_row(item, projects)

        result_rows.append(row)
        if row["匹配状态"] == "自动匹配":
            auto_matched += 1
        elif row["匹配状态"] == "待确认":
            needs_confirm += 1
        elif row["匹配状态"] == "未找到":
            not_found += 1

    write_csv(output_csv, result_rows)
    print(
        json.dumps(
            {
                "服务总数": len(result_rows),
                "自动匹配": auto_matched,
                "待确认": needs_confirm,
                "未找到": not_found,
                "复用旧结果": reused,
                "output_csv": str(output_csv),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
