#!/usr/bin/env python3
"""
audit_from_csv.py

第二阶段的机械调度层工具。
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import shutil
import tarfile
import tempfile
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

from telemetry_config import private_config_path

APPLICABILITY_FIELDS = (
    "链路初始化适用性",
    "服务端Tracing适用性",
    "服务端Metrics适用性",
    "Observer适用性",
    "客户端透传适用性",
    "日志链路适用性",
    "Redis指标适用性",
    "Pg指标适用性",
    "运维配置适用性",
)
EXECUTION_TRACKING_FIELDS = (
    "负责人",
    "统一分支名",
    "计划文档路径",
    "执行状态",
    "验证状态",
    "Commit哈希",
    "MR地址",
    "执行备注",
)
RESULT_COLUMNS = [
    "服务名称",
    "命名空间",
    "业务归属",
    "编程语言",
    "仓库地址",
    "仓库名",
    "本地仓库路径",
    "分支",
    "推测框架",
    "推测置信度",
    "推测依据",
    "接入模板",
    "运行形态",
    *APPLICABILITY_FIELDS,
    "仓库准备状态",
    "审计结论",
    "Metrics缺失",
    "链路追踪缺失",
    "Redis指标缺失",
    "Pg指标缺失",
    "检查摘要",
    "备注",
    *EXECUTION_TRACKING_FIELDS,
]
FINAL_AUDIT_STATUSES = {"通过", "发现问题", "跳过"}
FRAMEWORK_INFERENCE_FIELDS = ("推测框架", "推测置信度", "推测依据")
DERIVED_RESULT_FIELDS = ("接入模板", "运行形态", *APPLICABILITY_FIELDS)
RESULT_SCHEMA_FIELDS = (
    "编程语言",
    *FRAMEWORK_INFERENCE_FIELDS,
    *DERIVED_RESULT_FIELDS,
    *EXECUTION_TRACKING_FIELDS,
)
UNKNOWN_TEMPLATES = {"Unknown", "Go-Unknown", "Node-Unknown", "Java-Unknown"}
AUTO_PENDING_EXECUTION_NOTE = "接入模板仍需人工确认，确认后再生成单仓计划。"
PROGRESS_TRACKING_FIELDS = ("负责人", "统一分支名", "计划文档路径", "Commit哈希", "MR地址")
RESOLVE_CONFIG_PATH = private_config_path()
DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
SUPPORTED_EXECUTION_LANGUAGES = {
    "go": "Go",
    "golang": "Go",
    "node": "Node",
    "node.js": "Node",
    "nodejs": "Node",
}
NON_TARGET_TEMPLATE = "NonTarget-Skipped"


def row_key(service_name: str, namespace: str) -> tuple[str, str]:
    return ((service_name or "").strip(), (namespace or "").strip())


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_csv_rows(path: Path) -> list[dict]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_results(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        for row in rows:
            normalized = normalize_result_row(row)
            writer.writerow({key: normalized.get(key, "") for key in RESULT_COLUMNS})


def load_existing_results(path: Path) -> dict[tuple[str, str], dict]:
    if not path.exists():
        return {}
    rows = load_csv_rows(path)
    return {
        row_key(row.get("服务名称", ""), row.get("命名空间", "")): row
        for row in rows
        if row.get("服务名称")
    }


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urllib.parse.urlparse(repo_url)
    repo_path = parsed.path.lstrip("/").removesuffix(".git")
    repo_name = repo_path.rsplit("/", 1)[-1]
    return repo_path, repo_name


def sanitize_repo_dir(repo_path: str) -> str:
    return repo_path.replace("/", "__")


def compact_text(*parts: str) -> str:
    return " ".join((part or "").strip() for part in parts if (part or "").strip())


def contains_any(text: str, needles: tuple[str, ...]) -> bool:
    lowered = (text or "").lower()
    return any(needle.lower() in lowered for needle in needles)


def canonical_execution_language(value: str) -> str:
    normalized = (value or "").strip().lower()
    return SUPPORTED_EXECUTION_LANGUAGES.get(normalized, "")


def has_framework_inference(row: dict) -> bool:
    return all((row.get(field) or "").strip() for field in FRAMEWORK_INFERENCE_FIELDS)


def has_result_schema_fields(row: dict) -> bool:
    return all(field in row for field in RESULT_SCHEMA_FIELDS)


def should_reuse_result(row: dict, rerun_blocked: bool, current_language: str) -> bool:
    status = (row.get("审计结论") or "").strip()
    if not has_result_schema_fields(row):
        return False
    if not has_framework_inference(row):
        return False
    if (row.get("编程语言") or "").strip() != (current_language or "").strip():
        return False
    if status in FINAL_AUDIT_STATUSES:
        return True
    if status == "阻塞" and not rerun_blocked:
        return True
    return False


def derive_runtime_shape(row: dict) -> str:
    framework = (row.get("推测框架") or "").strip()
    language = (row.get("编程语言") or "").strip()
    context = compact_text(row.get("检查摘要", ""), row.get("备注", ""), row.get("推测依据", ""))
    if framework == "FrontendStatic":
        return "FrontendStatic"
    if framework == "TaskWorker":
        return "TaskWorker"
    if framework in {"Kratos", "Gin", "Echo", "Koa", "Nest", "SpringBoot"}:
        return "WebServer"
    if contains_any(context, ("consumer", "cron", "job", "worker", "queue", "mqtt")):
        return "TaskWorker"
    if contains_any(context, ("vite", "react", "vue", "webpack", "nginx", "前端", "静态")):
        return "FrontendStatic"
    if language in {"Go", "Node", "Java"}:
        return "Unknown"
    return "Unknown"


def derive_instrument_template(row: dict, runtime_shape: str) -> str:
    language = (row.get("编程语言") or "").strip()
    framework = (row.get("推测框架") or "").strip()
    audit_status = (row.get("审计结论") or "").strip()
    if audit_status == "跳过":
        return NON_TARGET_TEMPLATE
    if runtime_shape == "FrontendStatic":
        if language == "Node":
            return "Node-FrontendStatic"
        return "FrontendStatic"
    if language == "Go":
        if framework == "Kratos" and runtime_shape == "WebServer":
            return "Go-Kratos-Web"
        if framework == "Gin" and runtime_shape == "WebServer":
            return "Go-Gin-Web"
        if framework == "Echo" and runtime_shape == "WebServer":
            return "Go-Echo-Web"
        if runtime_shape == "TaskWorker":
            return "Go-TaskWorker"
        return "Go-Unknown"
    if language == "Node":
        if framework == "Koa" and runtime_shape == "WebServer":
            return "Node-Koa-Web"
        if framework == "Nest" and runtime_shape == "WebServer":
            return "Node-Nest-Web"
        if runtime_shape == "TaskWorker":
            return "Node-TaskWorker"
        return "Node-Unknown"
    if language == "Java":
        if framework == "SpringBoot" and runtime_shape == "WebServer":
            return "Java-SpringBoot-Web"
        return "Java-Unknown"
    return "Unknown"


def explicit_non_usage(text: str, kind: str) -> bool:
    if kind == "redis":
        return contains_any(
            text,
            (
                "未使用 redis",
                "未见 redis 运行链路",
                "未见 redis 使用",
                "未见 redis 客户端使用",
                "全仓未见 redis",
                "未使用redis",
            ),
        )
    return contains_any(
        text,
        (
            "未使用 pg",
            "未见 pg 运行链路",
            "未见 pg 使用",
            "未见 pg 客户端使用",
            "未实际访问 pg",
            "未见 redis 或 pg 运行链路",
            "未使用pg",
        ),
    )


def explicit_usage(text: str, kind: str) -> bool:
    if kind == "redis":
        return contains_any(
            text,
            (
                "redis.mustreregistermetrics",
                "redis.newclient",
                "go-redis",
                "redis 缓存",
                "使用 redis",
                "app.redis",
                "ycredis",
                "utilsredis",
                "oredis",
                "newgoredis",
                "redis_pkg",
            ),
        )
    return contains_any(
        text,
        (
            "orm.mustreregistermetrics",
            "orm.mustreregistergormv1metrics",
            "gorm.open",
            "gorm prometheus",
            "pgx",
            "sqlx",
            "postgres",
            "opg.",
            "访问 pg",
            "实际访问 pg",
        ),
    )


def derive_storage_applicability(row: dict, kind: str, template: str) -> str:
    if template == NON_TARGET_TEMPLATE or template in {"FrontendStatic", "Node-FrontendStatic"}:
        return "不适用"
    if template.startswith("Node-"):
        return "不适用"
    field = "Redis指标缺失" if kind == "redis" else "Pg指标缺失"
    status = (row.get(field) or "").strip()
    context = compact_text(row.get("检查摘要", ""), row.get("备注", ""), row.get("推测依据", ""))
    if status == "是":
        return "适用"
    if explicit_non_usage(context, kind):
        return "不适用"
    if explicit_usage(context, kind):
        return "适用"
    if status == "未知":
        return "待确认"
    if status == "否":
        return "待确认"
    return "待确认"


def derive_applicability_fields(row: dict, template: str, runtime_shape: str) -> dict[str, str]:
    if template == NON_TARGET_TEMPLATE:
        return {field: "不适用" for field in APPLICABILITY_FIELDS}
    if runtime_shape == "FrontendStatic":
        return {field: "不适用" for field in APPLICABILITY_FIELDS}
    if template in {"Unknown", "Go-Unknown", "Node-Unknown", "Java-Unknown"}:
        return {field: "待确认" for field in APPLICABILITY_FIELDS}

    applicability = {field: "待确认" for field in APPLICABILITY_FIELDS}
    applicability["链路初始化适用性"] = "适用"
    applicability["日志链路适用性"] = "适用"
    applicability["客户端透传适用性"] = "待确认"
    applicability["运维配置适用性"] = "适用"

    if template.startswith("Go-") and runtime_shape == "WebServer":
        applicability["服务端Tracing适用性"] = "适用"
        applicability["服务端Metrics适用性"] = "适用"
        applicability["Observer适用性"] = "适用"
    elif template == "Go-TaskWorker":
        applicability["服务端Tracing适用性"] = "不适用"
        applicability["服务端Metrics适用性"] = "不适用"
        applicability["Observer适用性"] = "不适用"
    elif template.startswith("Node-") and runtime_shape == "WebServer":
        applicability["服务端Tracing适用性"] = "适用"
        applicability["服务端Metrics适用性"] = "适用"
        applicability["Observer适用性"] = "不适用"
    elif template == "Node-TaskWorker":
        applicability["服务端Tracing适用性"] = "不适用"
        applicability["服务端Metrics适用性"] = "不适用"
        applicability["Observer适用性"] = "不适用"
    elif template.startswith("Java-") and runtime_shape == "WebServer":
        applicability["服务端Tracing适用性"] = "适用"
        applicability["服务端Metrics适用性"] = "适用"
        applicability["Observer适用性"] = "不适用"

    applicability["Redis指标适用性"] = derive_storage_applicability(row, "redis", template)
    applicability["Pg指标适用性"] = derive_storage_applicability(row, "pg", template)
    return applicability


def default_execution_status(row: dict) -> str:
    audit_status = (row.get("审计结论") or "").strip()
    template = (row.get("接入模板") or "").strip()
    runtime_shape = (row.get("运行形态") or "").strip()
    if audit_status == "通过":
        return "无需接入"
    if audit_status == "跳过":
        return "已跳过"
    if audit_status == "阻塞":
        return "阻塞"
    if template in {"Unknown", "Go-Unknown", "Node-Unknown", "Java-Unknown"} or runtime_shape == "Unknown":
        return "待确认方案"
    return ""


def default_verify_status(row: dict) -> str:
    audit_status = (row.get("审计结论") or "").strip()
    if audit_status in {"通过", "跳过"}:
        return "无需验证"
    if audit_status == "阻塞":
        return "阻塞"
    return "未开始"


def default_execution_note(row: dict) -> str:
    audit_status = (row.get("审计结论") or "").strip()
    template = (row.get("接入模板") or "").strip()
    if audit_status == "通过":
        return "当前审计结果为通过，无需进入接入阶段。"
    if audit_status == "跳过":
        return (row.get("备注") or "").strip() or "当前服务不在本轮接入目标内。"
    if audit_status == "阻塞":
        return (row.get("备注") or "").strip() or "仓库或代码读取受阻，待人工处理。"
    if template in UNKNOWN_TEMPLATES:
        return AUTO_PENDING_EXECUTION_NOTE
    return "待根据接入模板生成单仓计划。"


def should_reset_auto_pending_execution_state(row: dict, template: str, runtime_shape: str) -> bool:
    execution_status = (row.get("执行状态") or "").strip()
    execution_note = (row.get("执行备注") or "").strip()
    verify_status = (row.get("验证状态") or "").strip()
    if execution_status != "待确认方案":
        return False
    if template in UNKNOWN_TEMPLATES or runtime_shape == "Unknown":
        return False
    if execution_note and execution_note != AUTO_PENDING_EXECUTION_NOTE:
        return False
    if verify_status not in {"", "未开始", "无需验证"}:
        return False
    if any((row.get(field) or "").strip() for field in PROGRESS_TRACKING_FIELDS):
        return False
    return True


def normalize_result_row(row: dict) -> dict:
    normalized = {key: row.get(key, "") for key in RESULT_COLUMNS}
    runtime_shape = derive_runtime_shape(normalized)
    template = derive_instrument_template(normalized, runtime_shape)
    normalized["接入模板"] = template
    normalized["运行形态"] = runtime_shape
    normalized.update(derive_applicability_fields(normalized, template, runtime_shape))
    normalized["负责人"] = (row.get("负责人") or "").strip()
    normalized["统一分支名"] = (row.get("统一分支名") or "").strip()
    normalized["计划文档路径"] = (row.get("计划文档路径") or "").strip()
    execution_status = (row.get("执行状态") or "").strip()
    verify_status = (row.get("验证状态") or "").strip()
    execution_note = (row.get("执行备注") or "").strip()
    if execution_status == "待分配":
        execution_status = ""
    if should_reset_auto_pending_execution_state(row, template, runtime_shape):
        execution_status = ""
        verify_status = ""
        execution_note = ""
    normalized["执行状态"] = execution_status or default_execution_status(normalized)
    normalized["验证状态"] = verify_status or default_verify_status(normalized)
    normalized["Commit哈希"] = (row.get("Commit哈希") or "").strip()
    normalized["MR地址"] = (row.get("MR地址") or "").strip()
    normalized["执行备注"] = execution_note or default_execution_note(normalized)
    return normalized


def merge_result_row(existing_row: dict | None, new_row: dict) -> dict:
    merged = dict(existing_row or {})
    for key, value in new_row.items():
        if key in EXECUTION_TRACKING_FIELDS and not (value or "").strip():
            continue
        merged[key] = value
    return normalize_result_row(merged)


def build_language_skip_reason(programming_language: str) -> str:
    language = (programming_language or "").strip()
    if not language:
        return "编程语言为空，本轮策略仅处理已明确标注为 Go/Node 的服务"
    return f"编程语言={language}，本轮策略仅处理 Go/Node"


def build_skipped_result_row(
    row: dict,
    repo_url: str,
    repo_name: str,
    reason: str,
) -> dict:
    programming_language = (row.get("编程语言") or "").strip()
    language_display = programming_language or "空"
    return {
        "服务名称": (row.get("服务名称") or "").strip(),
        "命名空间": (row.get("命名空间") or "").strip(),
        "业务归属": (row.get("业务归属") or "").strip(),
        "编程语言": programming_language,
        "仓库地址": repo_url,
        "仓库名": repo_name,
        "本地仓库路径": "",
        "分支": "master",
        "推测框架": "Unknown",
        "推测置信度": "低",
        "推测依据": reason,
        "仓库准备状态": "缺失",
        "审计结论": "跳过",
        "Metrics缺失": "未知",
        "链路追踪缺失": "未知",
        "Redis指标缺失": "未知",
        "Pg指标缺失": "未知",
        "检查摘要": f"语言门禁跳过；编程语言={language_display}",
        "备注": reason,
    }


def build_actionable_items(
    repo_rows: list[dict],
    cache_dir: Path,
    rerun_blocked: bool,
    existing_results: dict[tuple[str, str], dict],
    rerun_all: bool,
) -> tuple[list[dict], list[dict], dict]:
    actionable = []
    skipped_rows = []
    stats = Counter()
    for row in repo_rows:
        service_name = (row.get("服务名称") or "").strip()
        namespace = (row.get("命名空间") or "").strip()
        if not service_name:
            continue

        confirmed_url = (row.get("人工确认仓库地址") or "").strip()
        matched_url = (row.get("匹配仓库地址") or "").strip()
        match_status = (row.get("匹配状态") or "").strip()
        if confirmed_url:
            repo_url = confirmed_url
        elif match_status == "自动匹配" and matched_url:
            repo_url = matched_url
        else:
            continue

        existing = existing_results.get(row_key(service_name, namespace))
        programming_language = (row.get("编程语言") or "").strip()
        supported_language = canonical_execution_language(programming_language)
        repo_path, parsed_repo_name = parse_repo_url(repo_url)
        repo_name = (
            (row.get("人工确认仓库名") or "").strip()
            or (row.get("匹配仓库名") or "").strip()
            or parsed_repo_name
        )

        if not supported_language:
            skipped_rows.append(
                build_skipped_result_row(
                    row=row,
                    repo_url=repo_url,
                    repo_name=repo_name,
                    reason=build_language_skip_reason(programming_language),
                )
            )
            stats["skipped_by_language"] += 1
            continue

        if (not rerun_all) and existing and should_reuse_result(existing, rerun_blocked, programming_language):
            stats["reused"] += 1
            continue

        actionable.append(
            {
                "服务名称": service_name,
                "命名空间": namespace,
                "业务归属": (row.get("业务归属") or "").strip(),
                "编程语言": (row.get("编程语言") or "").strip(),
                "仓库地址": repo_url,
                "仓库名": repo_name,
                "repo_path": repo_path,
                "本地仓库路径": str(cache_dir / sanitize_repo_dir(repo_path)),
                "分支": "master",
            }
        )
        stats["actionable"] += 1

    return actionable, skipped_rows, dict(stats)


def api_get_json(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))


def api_get_bytes(url: str, token: str) -> bytes:
    req = urllib.request.Request(url, headers={"PRIVATE-TOKEN": token})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def fetch_project_info(gitlab_url: str, token: str, repo_path: str) -> dict:
    encoded = urllib.parse.quote_plus(repo_path)
    return api_get_json(f"{gitlab_url}/api/v4/projects/{encoded}", token)


def download_repo_archive(
    gitlab_url: str,
    token: str,
    repo_path: str,
    branch_hint: str,
    local_repo_path: Path,
    refresh: bool,
) -> tuple[str, str, str]:
    project = fetch_project_info(gitlab_url, token, repo_path)
    branch = project.get("default_branch") or branch_hint or "master"
    repo_name = project.get("path") or repo_path.rsplit("/", 1)[-1]

    if project.get("empty_repo"):
        return branch, repo_name, "失败"

    if local_repo_path.exists() and not refresh:
        return branch, repo_name, "就绪"

    encoded = urllib.parse.quote_plus(repo_path)
    archive_url = (
        f"{gitlab_url}/api/v4/projects/{encoded}/repository/archive.tar.gz"
        f"?sha={urllib.parse.quote_plus(branch)}"
    )
    data = api_get_bytes(archive_url, token)

    tmp_extract_root = Path(tempfile.mkdtemp(prefix="telemetry-audit-"))
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as tar:
            tar.extractall(tmp_extract_root, filter="data")
        children = [p for p in tmp_extract_root.iterdir()]
        extracted_root = children[0] if len(children) == 1 and children[0].is_dir() else tmp_extract_root
        if local_repo_path.exists():
            shutil.rmtree(local_repo_path)
        local_repo_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(extracted_root), str(local_repo_path))
        if tmp_extract_root.exists():
            shutil.rmtree(tmp_extract_root, ignore_errors=True)
    except Exception:
        shutil.rmtree(tmp_extract_root, ignore_errors=True)
        raise

    return branch, repo_name, "已更新" if refresh else "已克隆"


def merge_results(output_csv: Path, result_rows: list[dict]) -> dict:
    existing = load_existing_results(output_csv)
    for row in result_rows:
        service_name = (row.get("服务名称") or "").strip()
        namespace = (row.get("命名空间") or "").strip()
        if not service_name:
            continue
        key = row_key(service_name, namespace)
        existing[key] = merge_result_row(existing.get(key), row)

    merged_rows = [normalize_result_row(existing[key]) for key in sorted(existing.keys())]
    write_results(output_csv, merged_rows)

    status_counter = Counter(row.get("审计结论", "") for row in merged_rows)
    clone_counter = Counter(row.get("仓库准备状态", "") for row in merged_rows)
    execution_counter = Counter(row.get("执行状态", "") for row in merged_rows)
    template_counter = Counter(row.get("接入模板", "") for row in merged_rows)
    return {
        "rows": len(merged_rows),
        "审计结论": dict(status_counter),
        "仓库准备状态": dict(clone_counter),
        "执行状态": dict(execution_counter),
        "接入模板": dict(template_counter),
        "output_csv": str(output_csv),
    }


def cmd_plan(args: argparse.Namespace) -> int:
    repo_resolution_csv = Path(args.repo_resolution_csv).expanduser().resolve()
    output_csv = Path(args.output_csv).expanduser().resolve()
    artifact_dir = (
        Path(args.artifact_dir).expanduser().resolve()
        if args.artifact_dir
        else output_csv.parent
    )
    cache_dir = artifact_dir / "repo-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)

    repo_rows = load_csv_rows(repo_resolution_csv)
    existing_results = load_existing_results(output_csv)
    actionable, skipped_rows, stats = build_actionable_items(
        repo_rows=repo_rows,
        cache_dir=cache_dir,
        rerun_blocked=args.rerun_blocked,
        existing_results=existing_results,
        rerun_all=args.rerun_all,
    )
    if skipped_rows:
        merge_results(output_csv=output_csv, result_rows=skipped_rows)
    if args.limit > 0:
        actionable = actionable[: args.limit]

    payload = {
        "repo_resolution_csv": str(repo_resolution_csv),
        "output_csv": str(output_csv),
        "artifact_dir": str(artifact_dir),
        "cache_dir": str(cache_dir),
        "worker_concurrency": args.worker_concurrency,
        "actionable_count": len(actionable),
        "reused_count": stats.get("reused", 0),
        "skipped_count": stats.get("skipped_by_language", 0),
        "rerun_all": args.rerun_all,
        "items": actionable,
    }
    if args.output_manifest:
        write_json(Path(args.output_manifest).expanduser().resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_prepare_repo(args: argparse.Namespace) -> int:
    cfg = load_json(RESOLVE_CONFIG_PATH)
    token = (cfg.get("GITLAB_TOKEN") or "").strip()
    gitlab_url = (cfg.get("GITLAB_URL") or DEFAULT_GITLAB_URL).strip()
    if not token:
        print("[ERROR] Missing GITLAB_TOKEN in telemetry-resolve-repos config.")
        return 2

    repo_url = args.repo_url.strip()
    repo_path, parsed_repo_name = parse_repo_url(repo_url)
    repo_name = args.repo_name.strip() or parsed_repo_name
    artifact_dir = Path(args.artifact_dir).expanduser().resolve()
    cache_dir = artifact_dir / "repo-cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_repo_path = cache_dir / sanitize_repo_dir(repo_path)

    branch, repo_name, clone_status = download_repo_archive(
        gitlab_url=gitlab_url,
        token=token,
        repo_path=repo_path,
        branch_hint=args.branch.strip() or "master",
        local_repo_path=local_repo_path,
        refresh=args.refresh,
    )

    payload = {
        "服务名称": args.service_name,
        "仓库地址": repo_url,
        "仓库名": repo_name,
        "repo_path": repo_path,
        "本地仓库路径": str(local_repo_path),
        "分支": branch,
        "仓库准备状态": clone_status,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_merge_results(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).expanduser().resolve()
    result_file = Path(args.result_file).expanduser().resolve()
    payload = load_json(result_file)
    rows = payload if isinstance(payload, list) else [payload]
    summary = merge_results(output_csv=output_csv, result_rows=rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_merge_json(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).expanduser().resolve()
    payload = json.loads(args.result_json)
    rows = payload if isinstance(payload, list) else [payload]
    summary = merge_results(output_csv=output_csv, result_rows=rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).expanduser().resolve()
    rows = load_csv_rows(output_csv)
    status_counter = Counter(row.get("审计结论", "") for row in rows)
    clone_counter = Counter(row.get("仓库准备状态", "") for row in rows)
    execution_counter = Counter(row.get("执行状态", "") for row in rows)
    template_counter = Counter(row.get("接入模板", "") for row in rows)
    payload = {
        "rows": len(rows),
        "审计结论": dict(status_counter),
        "仓库准备状态": dict(clone_counter),
        "执行状态": dict(execution_counter),
        "接入模板": dict(template_counter),
        "output_csv": str(output_csv),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="telemetry 第二阶段机械调度层工具")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="读取 repo-resolution.csv 并生成待执行清单")
    plan_parser.add_argument("--repo-resolution-csv", required=True)
    plan_parser.add_argument("--output-csv", required=True)
    plan_parser.add_argument("--artifact-dir", default="")
    plan_parser.add_argument("--limit", type=int, default=0)
    plan_parser.add_argument("--rerun-blocked", action="store_true")
    plan_parser.add_argument("--rerun-all", action="store_true")
    plan_parser.add_argument("--worker-concurrency", type=int, default=2)
    plan_parser.add_argument("--output-manifest", default="")
    plan_parser.set_defaults(func=cmd_plan)

    prepare_parser = subparsers.add_parser("prepare-repo", help="准备单仓本地 repo cache")
    prepare_parser.add_argument("--service-name", required=True)
    prepare_parser.add_argument("--repo-url", required=True)
    prepare_parser.add_argument("--repo-name", default="")
    prepare_parser.add_argument("--artifact-dir", required=True)
    prepare_parser.add_argument("--branch", default="master")
    prepare_parser.add_argument("--refresh", action="store_true")
    prepare_parser.set_defaults(func=cmd_prepare_repo)

    merge_parser = subparsers.add_parser("merge-results", help="合并 worker 结果到总 CSV")
    merge_parser.add_argument("--output-csv", required=True)
    merge_parser.add_argument("--result-file", required=True)
    merge_parser.set_defaults(func=cmd_merge_results)

    merge_json_parser = subparsers.add_parser("merge-json", help="直接合并 JSON 字符串结果到总 CSV")
    merge_json_parser.add_argument("--output-csv", required=True)
    merge_json_parser.add_argument("--result-json", required=True)
    merge_json_parser.set_defaults(func=cmd_merge_json)

    summary_parser = subparsers.add_parser("summary", help="统计 telemetry-audit-results.csv")
    summary_parser.add_argument("--output-csv", required=True)
    summary_parser.set_defaults(func=cmd_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
