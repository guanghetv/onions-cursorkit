#!/usr/bin/env python3
"""
fetch_service_inventory.py - 从飞书多维表格读取服务清单，按固定规则过滤并生成
service-inventory.json。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from telemetry_config import load_config

DEFAULT_BASE_TOKEN = "IFj7bGDJTaKxo7s7A7VcUPsqnDf"
DEFAULT_TABLE_ID = "tblBJH3FuUHuhrGO"
DEFAULT_VIEW_ID = "vewOpKcL8Y"
DEFAULT_LIMIT = 200
BASE_OUTPUT_FIELDS = [
    "服务名称",
    "命名空间",
    "服务类型",
    "业务归属",
    "状态",
    "Metrics指标采集",
    "链路追踪接入",
    "Redis连接池指标上报",
    "Pg连接池指标上报",
]
LANGUAGE_FIELD_CANDIDATES = ["编程语言", "开发语言", "语言"]
RUNTIME_ENV_FIELD_CANDIDATES = ["运行环境"]
EXCLUDED_STATUSES = {"待下线", "已下线"}
EXCLUDED_BUSINESS_OWNERS = {
    "测试技术支撑",
    "运维",
    "工程效率",
    "未知",
    "技术战共创",
    "数据中台",
    "APP组",
}
PRODUCTION_ENV_KEYWORD = "正式环境"


def normalize_scalar(value):
    if isinstance(value, list):
        if not value:
            return ""
        if len(value) == 1:
            return str(value[0]).strip()
        return " | ".join(str(item).strip() for item in value if str(item).strip())
    if value is None or isinstance(value, bool):
        return value
    return str(value).strip()


def fetch_page(
    base_token: str,
    table_id: str,
    view_id: str,
    offset: int,
    limit: int,
    output_fields: list[str],
) -> dict:
    cmd = [
        "lark-cli",
        "base",
        "+record-list",
        "--as",
        "user",
        "--base-token",
        base_token,
        "--table-id",
        table_id,
        "--view-id",
        view_id,
        "--offset",
        str(offset),
        "--limit",
        str(limit),
    ]
    for field in output_fields:
        cmd.extend(["--field-id", field])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or "lark-cli 调用失败")
    payload = json.loads(proc.stdout)
    if not payload.get("ok"):
        raise RuntimeError(f"飞书返回异常: {json.dumps(payload, ensure_ascii=False)}")
    return payload["data"]


def choose_existing_field(
    base_token: str,
    table_id: str,
    view_id: str,
    default_output_fields: list[str],
    candidates: list[str],
    preferred_field: str,
) -> str:
    probe_candidates = [preferred_field] if preferred_field else candidates
    seen = set()
    ordered_candidates = []
    for candidate in probe_candidates:
        if not candidate or candidate in seen:
            continue
        seen.add(candidate)
        ordered_candidates.append(candidate)
    for candidate in ordered_candidates:
        if not candidate:
            continue
        try:
            probe_fields = list(default_output_fields)
            if candidate not in probe_fields:
                probe_fields.append(candidate)
            fetch_page(
                base_token=base_token,
                table_id=table_id,
                view_id=view_id,
                offset=0,
                limit=1,
                output_fields=probe_fields,
            )
            return candidate
        except RuntimeError:
            continue
    return ""


def row_to_record(
    fields: list[str],
    row: list,
    base_token: str,
    table_id: str,
    view_id: str,
    language_field: str,
    runtime_env_field: str,
) -> dict:
    mapped = {field: normalize_scalar(value) for field, value in zip(fields, row, strict=False)}
    runtime_environment = mapped.get(runtime_env_field, "") if runtime_env_field else ""
    contains_production_env = "是" if PRODUCTION_ENV_KEYWORD in str(runtime_environment or "") else "否"
    return {
        "service_name": mapped.get("服务名称", ""),
        "namespace": mapped.get("命名空间", ""),
        "business_owner": mapped.get("业务归属", ""),
        "programming_language": mapped.get(language_field, "") if language_field else "",
        "runtime_environment": runtime_environment,
        "contains_production_env": contains_production_env,
        "service_type": mapped.get("服务类型", ""),
        "service_status": mapped.get("状态", ""),
        "metrics_status": mapped.get("Metrics指标采集"),
        "tracing_status": mapped.get("链路追踪接入"),
        "redis_metrics_status": mapped.get("Redis连接池指标上报"),
        "pg_metrics_status": mapped.get("Pg连接池指标上报"),
        "source_base_token": base_token,
        "source_table_id": table_id,
        "source_view_id": view_id,
    }


def should_keep(record: dict) -> bool:
    if record.get("service_type") != "后端":
        return False
    if record.get("service_status") in EXCLUDED_STATUSES:
        return False
    if record.get("business_owner") in EXCLUDED_BUSINESS_OWNERS:
        return False
    if record.get("contains_production_env") != "是":
        return False
    return True


def record_key(record: dict) -> tuple[str, str]:
    return (
        (record.get("service_name") or "").strip(),
        (record.get("namespace") or "").strip(),
    )


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="从飞书服务信息表读取服务清单并生成 service-inventory.json")
    parser.add_argument("--output-file", required=True, help="service-inventory.json 输出路径")
    parser.add_argument("--base-token", default="")
    parser.add_argument("--table-id", default="")
    parser.add_argument("--view-id", default="")
    parser.add_argument(
        "--language-field",
        default="",
        help="覆盖飞书里的编程语言字段名；默认按 编程语言 / 开发语言 / 语言 顺序自动探测",
    )
    parser.add_argument(
        "--runtime-env-field",
        default="",
        help="覆盖飞书里的运行环境字段名；默认按 运行环境 顺序自动探测",
    )
    parser.add_argument("--limit", type=int, default=0, help="仅保留前 N 条过滤后结果，0 表示全部")
    args = parser.parse_args()
    cfg = load_config()
    args.base_token = args.base_token or cfg.get("FEISHU_BASE_TOKEN") or DEFAULT_BASE_TOKEN
    args.table_id = args.table_id or cfg.get("FEISHU_TABLE_ID") or DEFAULT_TABLE_ID
    args.view_id = args.view_id or cfg.get("FEISHU_VIEW_ID") or DEFAULT_VIEW_ID

    runtime_env_field = choose_existing_field(
        base_token=args.base_token,
        table_id=args.table_id,
        view_id=args.view_id,
        default_output_fields=BASE_OUTPUT_FIELDS,
        candidates=RUNTIME_ENV_FIELD_CANDIDATES,
        preferred_field=args.runtime_env_field.strip(),
    )
    language_field = choose_existing_field(
        base_token=args.base_token,
        table_id=args.table_id,
        view_id=args.view_id,
        default_output_fields=BASE_OUTPUT_FIELDS + ([runtime_env_field] if runtime_env_field else []),
        candidates=LANGUAGE_FIELD_CANDIDATES,
        preferred_field=args.language_field.strip(),
    )
    output_fields = list(BASE_OUTPUT_FIELDS)
    if runtime_env_field and runtime_env_field not in output_fields:
        output_fields.append(runtime_env_field)
    if language_field and language_field not in output_fields:
        output_fields.append(language_field)

    all_records: list[dict] = []
    offset = 0
    while True:
        page = fetch_page(
            args.base_token,
            args.table_id,
            args.view_id,
            offset,
            DEFAULT_LIMIT,
            output_fields,
        )
        fields = page.get("fields") or []
        rows = page.get("data") or []
        all_records.extend(
            row_to_record(
                fields,
                row,
                args.base_token,
                args.table_id,
                args.view_id,
                language_field,
                runtime_env_field,
            )
            for row in rows
        )
        if not page.get("has_more"):
            break
        offset += DEFAULT_LIMIT

    filtered_records: list[dict] = []
    seen = set()
    for record in all_records:
        key = record_key(record)
        if not key[0]:
            continue
        if not should_keep(record):
            continue
        if key in seen:
            continue
        seen.add(key)
        filtered_records.append(record)

    if args.limit > 0:
        filtered_records = filtered_records[: args.limit]

    output_path = Path(args.output_file).expanduser().resolve()
    payload = {
        "filter": "service_type=后端; runtime_environment contains 正式环境; status!=待下线/已下线; business_owner not in blacklist",
        "dedupe_by": "service_name+namespace",
        "programming_language_field": language_field,
        "runtime_environment_field": runtime_env_field,
        "service_total_before_filter": len(all_records),
        "service_total_after_filter": len(filtered_records),
        "records": filtered_records,
    }
    write_json(output_path, payload)
    print(json.dumps({"output_file": str(output_path), **payload}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
