#!/usr/bin/env python3
"""
instrument_from_csv.py

telemetry 第三阶段的机械调度层工具。
负责候选筛选、计划文档与 worker manifest 生成、可写仓库准备、结果回填与 GitLab MR 创建辅助。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime
from pathlib import Path

from telemetry_config import private_config_path

PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = PLUGIN_ROOT / "skills" / "telemetry-instrument-from-csv"
AUDIT_SCRIPT_PATH = Path(__file__).with_name("audit_from_csv.py")
RESOLVE_CONFIG_PATH = private_config_path()
DEFAULT_GITLAB_URL = "https://gitlab.yc345.tv"
TEMPLATE_BLACKLIST = {"Unknown", "Go-Unknown", "Node-Unknown", "Java-Unknown", "NonTarget-Skipped"}
DEFAULT_WORKER_CONCURRENCY = 3
TERMINAL_EXECUTION_STATUSES = {"已提MR", "已完成", "无需接入", "已跳过", "阻塞", "待确认方案"}
VALID_EXECUTION_STATUSES = TERMINAL_EXECUTION_STATUSES | {"", "执行中", "待验证", "待提MR"}
VALID_VERIFY_STATUSES = {"", "未开始", "验证中", "验证通过", "验证失败", "无需验证", "阻塞"}
VERIFY_STATUS_ALIASES = {
    "部分验证通过": "验证通过",
}


def load_audit_module():
    spec = importlib.util.spec_from_file_location("telemetry_audit_from_csv", AUDIT_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"无法加载 audit 调度脚本: {AUDIT_SCRIPT_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIT = load_audit_module()
RESULT_COLUMNS = AUDIT.RESULT_COLUMNS
EXECUTION_TRACKING_FIELDS = AUDIT.EXECUTION_TRACKING_FIELDS
APPLICABILITY_FIELDS = AUDIT.APPLICABILITY_FIELDS


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def load_config() -> dict:
    cfg = load_json(RESOLVE_CONFIG_PATH)
    token = (cfg.get("GITLAB_TOKEN") or "").strip()
    gitlab_url = (cfg.get("GITLAB_URL") or DEFAULT_GITLAB_URL).strip()
    workspace_root = Path((cfg.get("workspaceRoot") or Path.cwd())).expanduser().resolve()
    return {
        "token": token,
        "gitlab_url": gitlab_url,
        "workspace_root": workspace_root,
    }


def row_key(service_name: str, namespace: str) -> tuple[str, str]:
    return AUDIT.row_key(service_name, namespace)


def load_csv_rows(path: Path) -> list[dict]:
    return AUDIT.load_csv_rows(path)


def write_results(path: Path, rows: list[dict]) -> None:
    AUDIT.write_results(path, rows)


def load_existing_results(path: Path) -> dict[tuple[str, str], dict]:
    return AUDIT.load_existing_results(path)


def merge_result_row(existing_row: dict | None, new_row: dict) -> dict:
    return AUDIT.merge_result_row(existing_row, new_row)


def parse_repo_url(repo_url: str) -> tuple[str, str]:
    return AUDIT.parse_repo_url(repo_url)


def sanitize_repo_dir(repo_path: str) -> str:
    return AUDIT.sanitize_repo_dir(repo_path)


def merge_results(output_csv: Path, result_rows: list[dict]) -> dict:
    existing = load_existing_results(output_csv)
    for row in result_rows:
        normalized = normalize_worker_result(row)
        service_name = (normalized.get("服务名称") or "").strip()
        namespace = (normalized.get("命名空间") or "").strip()
        if not service_name:
            continue
        key = row_key(service_name, namespace)
        existing[key] = merge_result_row(existing.get(key), normalized)

    merged_rows = [existing[key] for key in sorted(existing.keys())]
    write_results(output_csv, merged_rows)
    status_counter = Counter((row.get("执行状态") or "").strip() for row in merged_rows)
    verify_counter = Counter((row.get("验证状态") or "").strip() for row in merged_rows)
    mr_counter = Counter("已创建" if (row.get("MR地址") or "").strip() else "未创建" for row in merged_rows)
    return {
        "rows": len(merged_rows),
        "执行状态": dict(status_counter),
        "验证状态": dict(verify_counter),
        "MR统计": dict(mr_counter),
        "output_csv": str(output_csv),
    }


def api_request_json(url: str, token: str, method: str = "GET", payload: dict | None = None) -> dict | list:
    data = None
    headers = {"PRIVATE-TOKEN": token, "Accept": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, headers=headers, data=data, method=method)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_project_info(gitlab_url: str, token: str, repo_path: str) -> dict:
    encoded = urllib.parse.quote_plus(repo_path)
    return api_request_json(f"{gitlab_url.rstrip('/')}/api/v4/projects/{encoded}", token)


def run_git(args: list[str], cwd: Path | None = None, token: str = "") -> str:
    command = ["git"]
    if token:
        command.extend(["-c", f"http.extraHeader=PRIVATE-TOKEN: {token}"])
    command.extend(args)
    proc = subprocess.run(
        command,
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"git {' '.join(args)} 失败: {stderr}")
    output_parts = []
    if (proc.stdout or "").strip():
        output_parts.append(proc.stdout.strip())
    if (proc.stderr or "").strip():
        output_parts.append(proc.stderr.strip())
    return "\n".join(output_parts).strip()


def default_branch_name() -> str:
    return f"telemetry-auto-{datetime.now().strftime('%Y%m%d%H%M%S')}"


def slugify(value: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_-]+", "-", value.strip())
    text = re.sub(r"-{2,}", "-", text).strip("-")
    return text or "unknown"


def plan_doc_path(plan_dir: Path, service_name: str, namespace: str) -> Path:
    return plan_dir / f"{slugify(service_name)}__{slugify(namespace)}.md"


def worker_result_path(result_dir: Path, service_name: str, namespace: str) -> Path:
    return result_dir / f"{slugify(service_name)}__{slugify(namespace)}.json"


def default_local_repo_path(artifact_dir: Path, repo_path: str) -> Path:
    return artifact_dir / "writable-repos" / sanitize_repo_dir(repo_path)


def filter_service_names(raw_values: list[str]) -> set[str]:
    names: set[str] = set()
    for raw in raw_values:
        for part in raw.split(","):
            value = part.strip()
            if value:
                names.add(value)
    return names


def append_execution_note(existing_note: str, extra_note: str) -> str:
    left = (existing_note or "").strip()
    right = (extra_note or "").strip()
    if not right:
        return left
    if not left:
        return right
    if right in left:
        return left
    return f"{left}；{right}"


def normalize_worker_result(row: dict) -> dict:
    normalized = dict(row)
    execution_status = (normalized.get("执行状态") or "").strip()
    verify_status = (normalized.get("验证状态") or "").strip()
    mr_url = (normalized.get("MR地址") or "").strip()
    note = (normalized.get("执行备注") or "").strip()

    if "merge_requests/new?" in mr_url:
        note = append_execution_note(note, f"调度器规范化：`MR地址` 是手动新建页面而非已创建 MR，已移入备注：{mr_url}")
        mr_url = ""
        normalized["MR地址"] = ""

    if verify_status in VERIFY_STATUS_ALIASES:
        verify_status = VERIFY_STATUS_ALIASES[verify_status]
        normalized["验证状态"] = verify_status

    if execution_status not in VALID_EXECUTION_STATUSES:
        execution_status = "阻塞"
        verify_status = "阻塞"
        note = append_execution_note(note, f"调度器规范化：收到未知执行状态 `{(normalized.get('执行状态') or '').strip() or '空'}`。")

    if verify_status not in VALID_VERIFY_STATUSES:
        execution_status = "阻塞"
        verify_status = "阻塞"
        note = append_execution_note(note, f"调度器规范化：收到未知验证状态 `{(normalized.get('验证状态') or '').strip() or '空'}`。")

    if execution_status == "已提MR" and not mr_url:
        execution_status = "阻塞"
        note = append_execution_note(note, "调度器规范化：声明 `已提MR` 但未提供 MR地址，已转为阻塞。")

    normalized["执行状态"] = execution_status
    normalized["验证状态"] = verify_status
    normalized["执行备注"] = note
    return normalized


def should_select_row(row: dict, service_filter: set[str]) -> tuple[bool, str]:
    service_name = (row.get("服务名称") or "").strip()
    template = (row.get("接入模板") or "").strip()
    audit_status = (row.get("审计结论") or "").strip()
    execution_status = (row.get("执行状态") or "").strip()
    repo_url = (row.get("仓库地址") or "").strip()

    if service_filter and service_name not in service_filter:
        return False, "filtered_service"
    if audit_status != "发现问题":
        return False, "not_problem"
    if execution_status in TERMINAL_EXECUTION_STATUSES:
        return False, "execution_terminal"
    if template in TEMPLATE_BLACKLIST:
        return False, "template_skip"
    if not repo_url:
        return False, "missing_repo_url"
    return True, ""


def make_change_item(title: str, details: list[str], source_fields: list[str]) -> dict:
    return {
        "title": title,
        "details": details,
        "source_fields": source_fields,
    }


def build_change_sets(row: dict) -> tuple[list[dict], list[dict], list[dict]]:
    template = (row.get("接入模板") or "").strip()
    runtime_shape = (row.get("运行形态") or "").strip()
    changes: list[dict] = []
    pending: list[dict] = []
    skips: list[dict] = []

    def missing(field: str) -> bool:
        return (row.get(field) or "").strip() == "是"

    def applicability(field: str) -> str:
        return (row.get(field) or "").strip()

    if missing("链路追踪缺失"):
        tracing_details: list[str] = []
        pending_details: list[str] = []
        if applicability("链路初始化适用性") == "适用":
            if template.startswith("Go-"):
                tracing_details.append("在 main 入口最前面补 `tracingcommon.Init(...)`，并 `defer tracingcommon.Shotdown()`。")
            elif template.startswith("Node-"):
                tracing_details.append("在服务启动最前面初始化 tracing，确保 serviceName 使用 `应用名.命名空间`。")
        if applicability("服务端Tracing适用性") == "适用":
            if template == "Go-Kratos-Web":
                tracing_details.append("HTTP/gRPC 中间件顺序补齐为 `tracing -> metrics -> log -> recovery`。")
            elif template == "Go-Gin-Web":
                tracing_details.append("Gin router 补 `EnableTrace()`，并检查日志中间件顺序。")
            elif template == "Go-Echo-Web":
                tracing_details.append("Echo router 补 `EnableTrace()`，并检查日志中间件顺序。")
            elif template.startswith("Node-"):
                tracing_details.append("补齐服务端 tracing 中间件或等价拦截器，确保请求上下文能进入链路。")
        if applicability("日志链路适用性") == "适用":
            if template.startswith("Go-"):
                tracing_details.append("关键日志点补 `logger.WithContext(ctx)`，把 trace_id 串到日志。")
            else:
                tracing_details.append("检查日志链路，确保日志输出能带上 trace 上下文。")
        if applicability("客户端透传适用性") == "适用":
            tracing_details.append("若有出站 HTTP/gRPC/Resty 客户端，补齐 tracing 透传。")
        elif applicability("客户端透传适用性") == "待确认":
            pending_details.append("确认仓库是否存在出站 HTTP/gRPC/MQ 调用，需要时再补客户端透传。")

        if tracing_details:
            changes.append(make_change_item("补齐链路追踪接入", tracing_details, ["链路追踪缺失"]))
        if pending_details:
            pending.append(make_change_item("链路透传待确认", pending_details, ["客户端透传适用性"]))

    if missing("Metrics缺失"):
        metric_details: list[str] = []
        if applicability("服务端Metrics适用性") == "适用":
            if template == "Go-Kratos-Web":
                metric_details.append("服务端补 `metrics.KratosMiddleware()`。")
            elif template == "Go-Gin-Web":
                metric_details.append("Gin router 补 `metrics.GinMiddleware()`。")
            elif template == "Go-Echo-Web":
                metric_details.append("Echo router 补 `metrics.EchoMiddleware()`。")
            elif template.startswith("Node-"):
                metric_details.append("补 `prom-client` 注册、HTTP metrics middleware 与 `GET /metrics` 暴露。")
        if applicability("Observer适用性") == "适用":
            if template == "Go-Kratos-Web":
                metric_details.append("Kratos App 注册 `observer.NewServer()`，暴露 runtime / pprof / metrics。")
            elif runtime_shape == "WebServer":
                metric_details.append("补独立 observer 服务，并随主服务一起启动与优雅关闭。")
        if metric_details:
            changes.append(make_change_item("补齐服务端 Metrics 接入", metric_details, ["Metrics缺失"]))

    if missing("Redis指标缺失"):
        redis_applicability = applicability("Redis指标适用性")
        if redis_applicability == "适用":
            changes.append(
                make_change_item(
                    "补齐 Redis 指标注册",
                    ["在实际 Redis client 初始化后补 `redis.MustRegisterMetrics(...)` 或等价注册逻辑。"],
                    ["Redis指标缺失", "Redis指标适用性"],
                )
            )
        elif redis_applicability == "待确认":
            pending.append(
                make_change_item(
                    "Redis 指标待确认",
                    ["先确认运行链路是否真实使用 Redis；若确认使用，再补指标注册。"],
                    ["Redis指标缺失", "Redis指标适用性"],
                )
            )
        else:
            skips.append(
                make_change_item(
                    "Redis 指标不适用",
                    ["当前模板判定 Redis 指标不适用，本次不改。"],
                    ["Redis指标适用性"],
                )
            )

    if missing("Pg指标缺失"):
        pg_applicability = applicability("Pg指标适用性")
        if pg_applicability == "适用":
            changes.append(
                make_change_item(
                    "补齐 Pg / Gorm 指标注册",
                    ["在实际 Gorm/PG client 初始化后补 `orm.MustRegisterMetrics(...)` 或等价注册逻辑。"],
                    ["Pg指标缺失", "Pg指标适用性"],
                )
            )
        elif pg_applicability == "待确认":
            pending.append(
                make_change_item(
                    "Pg 指标待确认",
                    ["先确认运行链路是否真实使用 PG/Gorm；若确认使用，再补指标注册。"],
                    ["Pg指标缺失", "Pg指标适用性"],
                )
            )
        else:
            skips.append(
                make_change_item(
                    "Pg 指标不适用",
                    ["当前模板判定 Pg 指标不适用，本次不改。"],
                    ["Pg指标适用性"],
                )
            )

    for field in APPLICABILITY_FIELDS:
        if (row.get(field) or "").strip() == "不适用":
            skips.append(
                make_change_item(
                    f"{field} 不适用",
                    [f"按当前模板 `{template}`，`{field}` 判定为不适用。"],
                    [field],
                )
            )

    deduped_skips: list[dict] = []
    seen_skip_titles: set[str] = set()
    for item in skips:
        if item["title"] in seen_skip_titles:
            continue
        deduped_skips.append(item)
        seen_skip_titles.add(item["title"])

    return changes, pending, deduped_skips


def build_verification_plan(row: dict) -> list[str]:
    language = (row.get("编程语言") or "").strip()
    template = (row.get("接入模板") or "").strip()
    if language == "Go":
        return [
            "优先执行 `go test ./...`；若仓库过大，可先按改动包范围执行并补充构建验证。",
            "确认服务入口编译通过，且新增 tracing / metrics / observer 引用无未使用依赖。",
            "若改到 data 层，确认 Redis / PG 初始化路径能正常编译并完成指标注册。",
        ]
    if language == "Node":
        return [
            "优先识别 package manager，并执行现成的 `test` / `lint` / `build` 脚本。",
            "若无自动测试，至少验证 `GET /metrics` 暴露和服务启动无 tracing 初始化异常。",
            "确认中间件顺序和 metrics 注册逻辑不会破坏既有路由。",
        ]
    return [f"按模板 `{template}` 自行补充验证命令。"]


def render_plan_markdown(row: dict, branch_name: str, changes: list[dict], pending: list[dict], skips: list[dict]) -> str:
    def render_items(items: list[dict], empty_text: str) -> str:
        if not items:
            return f"- {empty_text}"
        blocks = []
        for item in items:
            lines = [f"- {item['title']}"]
            for detail in item["details"]:
                lines.append(f"  - {detail}")
            blocks.append("\n".join(lines))
        return "\n".join(blocks)

    verification_plan = render_items(
        [make_change_item("验证步骤", build_verification_plan(row), ["验证状态"])],
        "暂无验证计划",
    )
    applicability_lines = "\n".join(
        f"- `{field}`：{(row.get(field) or '').strip() or '空'}" for field in APPLICABILITY_FIELDS
    )
    return "\n".join(
        [
            f"# {(row.get('服务名称') or '').strip()} telemetry 接入计划",
            "",
            "## 服务信息",
            f"- 服务名称：`{(row.get('服务名称') or '').strip()}`",
            f"- 命名空间：`{(row.get('命名空间') or '').strip()}`",
            f"- 编程语言：`{(row.get('编程语言') or '').strip()}`",
            f"- 接入模板：`{(row.get('接入模板') or '').strip()}`",
            f"- 运行形态：`{(row.get('运行形态') or '').strip()}`",
            f"- 仓库地址：`{(row.get('仓库地址') or '').strip()}`",
            f"- 统一分支名：`{branch_name}`",
            "",
            "## 当前审计结论",
            f"- 审计结论：`{(row.get('审计结论') or '').strip()}`",
            f"- 缺失维度：`Metrics={(row.get('Metrics缺失') or '').strip()}` / `Tracing={(row.get('链路追踪缺失') or '').strip()}` / `Redis={(row.get('Redis指标缺失') or '').strip()}` / `Pg={(row.get('Pg指标缺失') or '').strip()}`",
            f"- 检查摘要：{(row.get('检查摘要') or '').strip() or '无'}",
            f"- 备注：{(row.get('备注') or '').strip() or '无'}",
            "",
            "## 接入模板与适用性矩阵",
            applicability_lines,
            "",
            "## 本次要改项",
            render_items(changes, "暂无明确需要改动的代码项。"),
            "",
            "## 本次明确不改项",
            render_items(skips, "无明确不改项。"),
            "",
            "## 待确认项",
            render_items(pending, "无待确认项。"),
            "",
            "## 验证方案",
            verification_plan,
            "",
            "## 风险与回滚点",
            "- 若验证失败、commit 失败或 MR 创建失败，当前仓标记为 `阻塞`，其余仓继续执行。",
            "- 计划文档为执行留痕，不作为人工审批关卡。",
            "- 改造完成后仍需由人工审阅 MR 并决定是否合并。",
            "",
        ]
    )


def build_candidate_item(row: dict, artifact_dir: Path, branch_name: str) -> dict:
    service_name = (row.get("服务名称") or "").strip()
    namespace = (row.get("命名空间") or "").strip()
    repo_url = (row.get("仓库地址") or "").strip()
    repo_path, _ = parse_repo_url(repo_url)
    changes, pending, skips = build_change_sets(row)
    plan_path = plan_doc_path(artifact_dir / "instrument-plans", service_name, namespace)
    local_repo_path = default_local_repo_path(artifact_dir, repo_path)
    result_path = worker_result_path(artifact_dir / "instrument-worker-results", service_name, namespace)
    return {
        "服务名称": service_name,
        "命名空间": namespace,
        "业务归属": (row.get("业务归属") or "").strip(),
        "编程语言": (row.get("编程语言") or "").strip(),
        "仓库地址": repo_url,
        "仓库名": (row.get("仓库名") or "").strip(),
        "repo_path": repo_path,
        "本地仓库路径": str(local_repo_path),
        "接入模板": (row.get("接入模板") or "").strip(),
        "运行形态": (row.get("运行形态") or "").strip(),
        "统一分支名": branch_name,
        "计划文档路径": str(plan_path),
        "worker_result_path": str(result_path),
        "change_items": changes,
        "pending_items": pending,
        "skip_items": skips,
    }


def cmd_plan(args: argparse.Namespace) -> int:
    input_csv = Path(args.input_csv).expanduser().resolve()
    output_csv = Path(args.output_csv).expanduser().resolve() if args.output_csv else input_csv
    artifact_dir = Path(args.artifact_dir).expanduser().resolve() if args.artifact_dir else input_csv.parent
    branch_name = args.branch_name.strip() or default_branch_name()
    service_filter = filter_service_names(args.service_name)
    plan_dir = artifact_dir / "instrument-plans"
    worker_result_dir = artifact_dir / "instrument-worker-results"
    plan_dir.mkdir(parents=True, exist_ok=True)
    worker_result_dir.mkdir(parents=True, exist_ok=True)

    rows = load_csv_rows(input_csv)
    existing_rows = {
        row_key(row.get("服务名称", ""), row.get("命名空间", "")): row
        for row in rows
        if row.get("服务名称")
    }
    candidates: list[dict] = []
    stats = Counter()
    for row in rows:
        selected, reason = should_select_row(row, service_filter)
        if not selected:
            stats[reason] += 1
            continue
        existing = existing_rows.get(row_key(row.get("服务名称", ""), row.get("命名空间", "")), {})
        branch_for_item = (existing.get("统一分支名") or "").strip() or branch_name
        candidates.append(build_candidate_item(row, artifact_dir, branch_for_item))

    if args.limit > 0:
        candidates = candidates[: args.limit]

    dispatch_limit = args.dispatch_limit if args.dispatch_limit > 0 else args.worker_concurrency
    dispatch_items = candidates[:dispatch_limit]

    writeback_rows = []
    for item in candidates:
        matching_row = next(
            row
            for row in rows
            if row_key(row.get("服务名称", ""), row.get("命名空间", ""))
            == row_key(item["服务名称"], item["命名空间"])
        )
        plan_path = Path(item["计划文档路径"])
        content = render_plan_markdown(
            matching_row,
            branch_name=item["统一分支名"],
            changes=item["change_items"],
            pending=item["pending_items"],
            skips=item["skip_items"],
        )
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(content)

        writeback_rows.append(
            {
                "服务名称": item["服务名称"],
                "命名空间": item["命名空间"],
                "统一分支名": item["统一分支名"],
                "计划文档路径": item["计划文档路径"],
            }
        )

    summary = merge_results(output_csv, writeback_rows) if writeback_rows else {
        "rows": len(rows),
        "output_csv": str(output_csv),
    }
    payload = {
        "input_csv": str(input_csv),
        "output_csv": str(output_csv),
        "artifact_dir": str(artifact_dir),
        "plan_dir": str(plan_dir),
        "worker_result_dir": str(worker_result_dir),
        "worker_contract_path": str(SKILL_ROOT / "references" / "single-repo-worker.md"),
        "checkpoints_path": str(SKILL_ROOT / "references" / "checkpoints.md"),
        "worker_concurrency": args.worker_concurrency,
        "dispatch_limit": dispatch_limit,
        "terminal_execution_statuses": sorted(TERMINAL_EXECUTION_STATUSES),
        "统一分支名": branch_name,
        "candidate_count": len(candidates),
        "dispatch_count": len(dispatch_items),
        "stats": dict(stats),
        "items": candidates,
        "dispatch_items": dispatch_items,
        "writeback_summary": summary,
    }
    if args.output_manifest:
        write_json(Path(args.output_manifest).expanduser().resolve(), payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def clone_or_refresh_repo(
    gitlab_url: str,
    token: str,
    repo_url: str,
    local_repo_path: Path,
    branch_name: str,
    fresh_clone: bool,
) -> dict:
    repo_path, parsed_repo_name = parse_repo_url(repo_url)
    project = fetch_project_info(gitlab_url, token, repo_path)
    base_branch = (project.get("default_branch") or "master").strip()
    repo_name = (project.get("path") or parsed_repo_name).strip()
    local_repo_path.parent.mkdir(parents=True, exist_ok=True)

    source = "clone"
    if fresh_clone and local_repo_path.exists():
        shutil.rmtree(local_repo_path)
    if not local_repo_path.exists():
        run_git(["clone", repo_url, str(local_repo_path)], token=token)
        source = "cloned"
    else:
        if not (local_repo_path / ".git").exists():
            raise RuntimeError(f"目标目录不是 git 仓库: {local_repo_path}")
        run_git(["fetch", "origin"], cwd=local_repo_path, token=token)
        source = "reused"

    run_git(["checkout", "-B", branch_name, f"origin/{base_branch}"], cwd=local_repo_path, token=token)
    head = run_git(["rev-parse", "HEAD"], cwd=local_repo_path)
    return {
        "repo_path": repo_path,
        "仓库名": repo_name,
        "本地仓库路径": str(local_repo_path),
        "基础分支": base_branch,
        "统一分支名": branch_name,
        "head_commit": head,
        "source": source,
        "project_id": project.get("id"),
    }


def cmd_prepare_repo(args: argparse.Namespace) -> int:
    cfg = load_config()
    token = cfg["token"]
    if not token:
        raise RuntimeError("缺少 GITLAB_TOKEN，无法准备可写仓库。")

    artifact_dir = Path(args.artifact_dir).expanduser().resolve()
    writable_dir = artifact_dir / "writable-repos"
    repo_url = args.repo_url.strip()
    repo_path, _ = parse_repo_url(repo_url)
    local_repo_path = writable_dir / sanitize_repo_dir(repo_path)
    branch_name = args.branch_name.strip() or default_branch_name()

    payload = clone_or_refresh_repo(
        gitlab_url=cfg["gitlab_url"],
        token=token,
        repo_url=repo_url,
        local_repo_path=local_repo_path,
        branch_name=branch_name,
        fresh_clone=args.fresh_clone,
    )
    payload.update(
        {
            "服务名称": args.service_name.strip(),
            "命名空间": args.namespace.strip(),
            "仓库地址": repo_url,
        }
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_mr_payload(args: argparse.Namespace, project: dict) -> dict:
    body = args.description.strip()
    payload = {
        "source_branch": args.source_branch.strip(),
        "target_branch": args.target_branch.strip() or (project.get("default_branch") or "master"),
        "title": args.title.strip(),
        "description": body,
        "remove_source_branch": False,
    }
    return payload


def encode_git_push_option_text(text: str) -> str:
    value = (text or "").strip()
    return value.replace("%", "%25").replace("\r\n", "%0A").replace("\n", "%0A")


def find_open_mr(gitlab_url: str, token: str, project_id: int, source_branch: str, target_branch: str) -> dict | None:
    query = urllib.parse.urlencode(
        {
            "state": "opened",
            "source_branch": source_branch,
            "target_branch": target_branch,
            "per_page": 20,
        }
    )
    rows = api_request_json(f"{gitlab_url.rstrip('/')}/api/v4/projects/{project_id}/merge_requests?{query}", token)
    return rows[0] if rows else None


def run_glab(args: list[str], cwd: Path | None = None) -> str:
    proc = subprocess.run(
        ["glab", *args],
        cwd=str(cwd) if cwd else None,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        stderr = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"glab {' '.join(args)} 失败: {stderr}")
    return "\n".join(part.strip() for part in [proc.stdout, proc.stderr] if part.strip()).strip()


def glab_find_open_mr(repo_url: str, source_branch: str, target_branch: str) -> dict | None:
    output = run_glab(
        [
            "mr",
            "list",
            "-R",
            repo_url,
            "--source-branch",
            source_branch,
            "--target-branch",
            target_branch,
            "--output",
            "json",
            "--per-page",
            "20",
        ]
    )
    rows = json.loads(output or "[]")
    return rows[0] if rows else None


def glab_create_or_reuse_mr(args: argparse.Namespace, target_branch: str) -> dict:
    repo_url = args.repo_url.strip()
    source_branch = args.source_branch.strip()
    existing = glab_find_open_mr(repo_url, source_branch, target_branch)
    if existing:
        return {
            "mr_url": existing.get("web_url") or existing.get("webUrl") or "",
            "iid": existing.get("iid") or existing.get("reference") or "",
            "title": existing.get("title", ""),
            "target_branch": existing.get("target_branch") or existing.get("targetBranch") or target_branch,
            "source_branch": existing.get("source_branch") or existing.get("sourceBranch") or source_branch,
            "reused": True,
            "creation_mode": "glab",
        }

    output = run_glab(
        [
            "mr",
            "create",
            "-R",
            repo_url,
            "--source-branch",
            source_branch,
            "--target-branch",
            target_branch,
            "--title",
            args.title.strip(),
            "--description",
            args.description.strip(),
            "--yes",
        ],
        cwd=Path(args.local_repo_path).expanduser().resolve() if args.local_repo_path.strip() else None,
    )
    match = re.search(r"https?://\S+/merge_requests/(\d+)", output)
    return {
        "mr_url": match.group(0) if match else "",
        "iid": match.group(1) if match else "",
        "title": args.title.strip(),
        "target_branch": target_branch,
        "source_branch": source_branch,
        "reused": False,
        "creation_mode": "glab",
        "glab_output": output,
    }


def cmd_create_mr(args: argparse.Namespace) -> int:
    cfg = load_config()
    token = cfg["token"]
    if not token:
        raise RuntimeError("缺少 GITLAB_TOKEN，无法创建 MR。")

    repo_path, _ = parse_repo_url(args.repo_url.strip())
    project = fetch_project_info(cfg["gitlab_url"], token, repo_path)
    project_id = int(project["id"])
    target_branch = args.target_branch.strip() or (project.get("default_branch") or "master")
    existing = find_open_mr(cfg["gitlab_url"], token, project_id, args.source_branch.strip(), target_branch)
    if existing:
        payload = {
            "mr_url": existing.get("web_url", ""),
            "iid": existing.get("iid"),
            "title": existing.get("title", ""),
            "target_branch": existing.get("target_branch", ""),
            "source_branch": existing.get("source_branch", ""),
            "reused": True,
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    mr_payload = build_mr_payload(args, project)
    try:
        result = api_request_json(
            f"{cfg['gitlab_url'].rstrip('/')}/api/v4/projects/{project_id}/merge_requests",
            token,
            method="POST",
            payload=mr_payload,
        )
        payload = {
            "mr_url": result.get("web_url", ""),
            "iid": result.get("iid"),
            "title": result.get("title", ""),
            "target_branch": result.get("target_branch", ""),
            "source_branch": result.get("source_branch", ""),
            "reused": False,
            "creation_mode": "api",
        }
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0
    except urllib.error.HTTPError as exc:
        if exc.code not in {401, 403}:
            raise

    push_output = ""
    if args.local_repo_path.strip():
        local_repo_path = Path(args.local_repo_path).expanduser().resolve()
        push_output = run_git(
            [
                "push",
                "origin",
                args.source_branch.strip(),
                "-o",
                "merge_request.create",
                "-o",
                f"merge_request.target={target_branch}",
                "-o",
                f"merge_request.title={args.title.strip()}",
                "-o",
                f"merge_request.description={encode_git_push_option_text(args.description)}",
            ],
            cwd=local_repo_path,
            token=token,
        )
    match = re.search(r"https?://\\S+/merge_requests/(\\d+)", push_output)
    if not match:
        glab_payload = glab_create_or_reuse_mr(args, target_branch)
        if glab_payload.get("mr_url"):
            print(json.dumps(glab_payload, ensure_ascii=False, indent=2))
            return 0

    payload = {
        "mr_url": match.group(0) if match else "",
        "iid": match.group(1) if match else "",
        "title": args.title.strip(),
        "target_branch": target_branch,
        "source_branch": args.source_branch.strip(),
        "reused": False,
        "creation_mode": "git_push_option",
        "push_output": push_output,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def cmd_merge_json(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).expanduser().resolve()
    payload = json.loads(args.result_json)
    rows = payload if isinstance(payload, list) else [payload]
    summary = merge_results(output_csv, rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def normalize_escaped_worker_text(text: str) -> str:
    return text.replace("\\n", "\n").replace('\\"', '"')


def iter_balanced_json_objects(text: str):
    in_string = False
    escaped = False
    start = None
    depth = 0
    for index, char in enumerate(text):
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            if depth == 0:
                start = index
            depth += 1
        elif char == "}" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                yield text[start : index + 1]
                start = None


def extract_worker_json_from_text(text: str) -> dict | None:
    variants = [text]
    if "输出片段：" in text:
        variants.append(text.split("输出片段：", 1)[1])
    variants.extend(normalize_escaped_worker_text(value) for value in list(variants))

    found: list[dict] = []
    for value in variants:
        for match in re.finditer(r"```json\s*(\{.*?\})\s*```", value, flags=re.S):
            try:
                obj = json.loads(match.group(1))
            except json.JSONDecodeError:
                continue
            if isinstance(obj, dict) and "服务名称" in obj:
                found.append(obj)

        for candidate in iter_balanced_json_objects(value):
            try:
                obj = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if not isinstance(obj, dict):
                continue
            if "服务名称" in obj:
                found.append(obj)
            elif isinstance(obj.get("result"), str):
                inner = extract_worker_json_from_text(obj["result"])
                if inner:
                    found.append(inner)

    return found[-1] if found else None


def cmd_parse_worker_output(args: argparse.Namespace) -> int:
    if args.input_file:
        raw_output = Path(args.input_file).expanduser().read_text(encoding="utf-8")
    else:
        raw_output = args.raw_output
    result = extract_worker_json_from_text(raw_output)
    if not result:
        raise RuntimeError("无法从 worker 输出中解析出包含 `服务名称` 的 JSON 对象。")
    print(json.dumps(normalize_worker_result(result), ensure_ascii=False, indent=2))
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    output_csv = Path(args.output_csv).expanduser().resolve()
    rows = load_csv_rows(output_csv)
    remaining_candidates = sum(1 for row in rows if should_select_row(row, set())[0])
    payload = {
        "rows": len(rows),
        "可执行候选数": remaining_candidates,
        "执行状态": dict(Counter((row.get("执行状态") or "").strip() for row in rows)),
        "验证状态": dict(Counter((row.get("验证状态") or "").strip() for row in rows)),
        "已创建MR": sum(1 for row in rows if (row.get("MR地址") or "").strip()),
        "已生成计划": sum(1 for row in rows if (row.get("计划文档路径") or "").strip()),
        "output_csv": str(output_csv),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="telemetry 第三阶段自动接入调度器")
    subparsers = parser.add_subparsers(dest="command", required=True)

    plan_parser = subparsers.add_parser("plan", help="筛选候选服务并生成单仓计划文档")
    plan_parser.add_argument("--input-csv", required=True)
    plan_parser.add_argument("--output-csv", default="")
    plan_parser.add_argument("--artifact-dir", default="")
    plan_parser.add_argument("--branch-name", default="")
    plan_parser.add_argument("--limit", type=int, default=0)
    plan_parser.add_argument("--dispatch-limit", type=int, default=0)
    plan_parser.add_argument("--output-manifest", default="")
    plan_parser.add_argument("--worker-concurrency", type=int, default=DEFAULT_WORKER_CONCURRENCY)
    plan_parser.add_argument("--service-name", action="append", default=[])
    plan_parser.set_defaults(func=cmd_plan)

    prepare_parser = subparsers.add_parser("prepare-repo", help="准备单仓可写 git clone 并切统一分支")
    prepare_parser.add_argument("--service-name", required=True)
    prepare_parser.add_argument("--namespace", required=True)
    prepare_parser.add_argument("--repo-url", required=True)
    prepare_parser.add_argument("--artifact-dir", required=True)
    prepare_parser.add_argument("--branch-name", required=True)
    prepare_parser.add_argument("--fresh-clone", action="store_true")
    prepare_parser.set_defaults(func=cmd_prepare_repo)

    create_mr_parser = subparsers.add_parser("create-mr", help="为指定仓库创建或复用 GitLab MR")
    create_mr_parser.add_argument("--repo-url", required=True)
    create_mr_parser.add_argument("--source-branch", required=True)
    create_mr_parser.add_argument("--target-branch", default="")
    create_mr_parser.add_argument("--title", required=True)
    create_mr_parser.add_argument("--description", default="")
    create_mr_parser.add_argument("--local-repo-path", default="")
    create_mr_parser.set_defaults(func=cmd_create_mr)

    merge_json_parser = subparsers.add_parser("merge-json", help="把执行结果 JSON 合并回 telemetry-audit-results.csv")
    merge_json_parser.add_argument("--output-csv", required=True)
    merge_json_parser.add_argument("--result-json", required=True)
    merge_json_parser.set_defaults(func=cmd_merge_json)

    parse_worker_output_parser = subparsers.add_parser(
        "parse-worker-output",
        help="从 Cursor CLI / subagent 输出中抽取单仓 worker JSON",
    )
    parse_worker_output_input = parse_worker_output_parser.add_mutually_exclusive_group(required=True)
    parse_worker_output_input.add_argument("--input-file", default="")
    parse_worker_output_input.add_argument("--raw-output", default="")
    parse_worker_output_parser.set_defaults(func=cmd_parse_worker_output)

    summary_parser = subparsers.add_parser("summary", help="汇总接入阶段执行状态")
    summary_parser.add_argument("--output-csv", required=True)
    summary_parser.set_defaults(func=cmd_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
