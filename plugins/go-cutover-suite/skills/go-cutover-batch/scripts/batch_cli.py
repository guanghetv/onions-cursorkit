#!/usr/bin/env python3
"""
batch_cli.py — 批次任务 CLI 工具
处理参数收集、校验、JSON 生成
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "references" / "config.json"
BATCHES_DIR = Path(os.path.expanduser("~/work/openclaw-runner/batches"))
DEFAULT_GATEWAY_REPOS = [
    "onions-school",
    "channel-platform-server",
    "channel",
    "teacher-tenant",
]


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def parse_csv(value: str) -> list:
    return [item.strip() for item in value.split(",") if item.strip()]


def compose_service_host(service_name: str, namespace: str) -> str:
    service_name = (service_name or "").strip()
    namespace = (namespace or "").strip()
    return f"{service_name}.{namespace}" if service_name and namespace else ""


def ask_yes_no(prompt: str, default: bool = True) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    answer = input(f"{prompt} {suffix}: ").strip().lower()
    if not answer:
        return default
    return answer in {"y", "yes"}


def save_batch_json(batch_data: dict) -> Path:
    BATCHES_DIR.mkdir(parents=True, exist_ok=True)
    file_path = BATCHES_DIR / f"{batch_data['batchId']}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(batch_data, f, indent=2, ensure_ascii=False)
    return file_path


def validate_task(task: dict) -> list:
    errors = []
    for field in ["oldRoute", "newRoute", "method", "branch"]:
        if not task.get(field):
            errors.append(f"任务缺少必填字段: {field}")
    if task.get("method") and task["method"] not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
        errors.append(f"无效的 HTTP 方法: {task['method']}")
    if task.get("gatewayRepos") is not None and not isinstance(task.get("gatewayRepos"), list):
        errors.append("gatewayRepos 必须是数组")
    if task.get("apisixAdminURLs") is not None and not isinstance(task.get("apisixAdminURLs"), list):
        errors.append("apisixAdminURLs 必须是数组")
    return errors


def effective_task_value(batch: dict, task: dict, key: str) -> str:
    value = task.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    value = batch.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return ""


def validate_batch(batch: dict) -> list:
    errors = []
    for field in ["batchId", "tasks", "feishuAlertOpenId"]:
        if not batch.get(field):
            errors.append(f"缺少必填字段: {field}")
    tasks = batch.get("tasks", [])
    if not isinstance(tasks, list) or not tasks:
        errors.append("tasks 必须是至少包含一个任务的数组")
        return errors

    for i, task in enumerate(tasks):
        for err in validate_task(task):
            errors.append(f"任务[{i}]: {err}")
        for key in ["oldServiceName", "newServiceName", "oldNamespace", "newNamespace"]:
            if not effective_task_value(batch, task, key):
                errors.append(f"任务[{i}]: 缺少 {key}（任务级或批次级至少提供一个）")
    return errors


def generate_batch_id() -> str:
    today = datetime.now().strftime("%Y%m%d")
    existing = list(BATCHES_DIR.glob(f"batch-{today}-*.json")) if BATCHES_DIR.exists() else []
    return f"batch-{today}-{len(existing) + 1:03d}"


def interactive_create():
    cfg = load_config()
    batch_id = generate_batch_id()
    description = ""
    default_openid = cfg.get("feishuAlertOpenId", "")
    sourcegraph_url = cfg.get("SOURCEGRAPH_URL", "https://sourcegraph.yc345.tv")
    sourcegraph_token = cfg.get("SOURCEGRAPH_TOKEN", os.environ.get("SOURCEGRAPH_TOKEN", ""))
    gitlab_url = cfg.get("GITLAB_URL", "https://gitlab.yc345.tv")
    workspace = cfg.get("workspaceRoot", os.path.expanduser("~/work"))
    batch_old_service = cfg.get("oldServiceName", "")
    batch_new_service = cfg.get("newServiceName", "")
    batch_old_namespace = cfg.get("oldNamespace", "")
    batch_new_namespace = cfg.get("newNamespace", "")
    batch_old_hint = cfg.get("oldServiceHint", "")
    batch_new_hint = cfg.get("newServiceHint", "")
    default_apisix_admin_urls = parse_csv(cfg.get("apisixAdminURLs", ""))
    default_apisix_admin_url = cfg.get("apisixAdminURL", "")
    default_apisix_key_env = cfg.get("apisixAdminKeyEnvVar", "APISIX_ADMIN_KEY")

    print("=" * 60)
    print("创建新的接口切换批次")
    print("=" * 60)
    print("\n【默认配置】")
    print(f"批次ID: {batch_id}")
    print(f"飞书告警 OpenID: {default_openid or '(未配置)'}")
    print(f"Sourcegraph URL: {sourcegraph_url}")
    print(f"GitLab URL: {gitlab_url}")
    print(f"工作目录: {workspace}")
    print(f"老服务: {batch_old_service or '(未配置)'}")
    print(f"新服务: {batch_new_service or '(未配置)'}")
    print(f"老 namespace: {batch_old_namespace or '(未配置)'}")
    print(f"新 namespace: {batch_new_namespace or '(未配置)'}")
    print(f"默认网关仓库: {', '.join(DEFAULT_GATEWAY_REPOS)}")
    if default_apisix_admin_url or default_apisix_admin_urls:
        merged = parse_csv(",".join(([default_apisix_admin_url] if default_apisix_admin_url else []) + default_apisix_admin_urls))
        print(f"默认 APISIX Admin URLs: {', '.join(merged)}")

    if ask_yes_no("是否覆盖批次基础配置？", default=False):
        custom_batch_id = input(f"批次ID [默认: {batch_id}]: ").strip()
        if custom_batch_id:
            batch_id = custom_batch_id
        description = input("批次描述 [可空]: ").strip()
        feishu_openid = input(f"飞书告警 OpenID [默认: {default_openid or '(空)'}]: ").strip() or default_openid
        sourcegraph_url = input(f"Sourcegraph URL [默认: {sourcegraph_url}]: ").strip() or sourcegraph_url
        gitlab_url = input(f"GitLab URL [默认: {gitlab_url}]: ").strip() or gitlab_url
        workspace = input(f"工作目录 [默认: {workspace}]: ").strip() or workspace
        batch_old_service = input(f"老服务名 [默认: {batch_old_service or '(空)'}]: ").strip() or batch_old_service
        batch_new_service = input(f"新服务名 [默认: {batch_new_service or '(空)'}]: ").strip() or batch_new_service
        batch_old_namespace = input(f"老 namespace [默认: {batch_old_namespace or '(空)'}]: ").strip() or batch_old_namespace
        batch_new_namespace = input(f"新 namespace [默认: {batch_new_namespace or '(空)'}]: ").strip() or batch_new_namespace
        batch_old_hint = input(f"老服务 hint [默认: {batch_old_hint or '(空)'}]: ").strip() or batch_old_hint
        batch_new_hint = input(f"新服务 hint [默认: {batch_new_hint or '(空)'}]: ").strip() or batch_new_hint
    else:
        description = input("批次描述 [可空，默认自动生成]: ").strip()
        feishu_openid = default_openid or input("飞书告警 OpenID: ").strip()
        batch_old_service = input(f"老服务名 [默认: {batch_old_service or '(空)'}]: ").strip() or batch_old_service
        batch_new_service = input(f"新服务名 [默认: {batch_new_service or '(空)'}]: ").strip() or batch_new_service
        batch_old_namespace = input(f"老 namespace [默认: {batch_old_namespace or '(空)'}]: ").strip() or batch_old_namespace
        batch_new_namespace = input(f"新 namespace [默认: {batch_new_namespace or '(空)'}]: ").strip() or batch_new_namespace
        if not batch_old_service:
            batch_old_service = input("老服务名（必填）: ").strip()
        if not batch_new_service:
            batch_new_service = input("新服务名（必填）: ").strip()
        if not batch_old_namespace:
            batch_old_namespace = input("老 namespace（必填）: ").strip()
        if not batch_new_namespace:
            batch_new_namespace = input("新 namespace（必填）: ").strip()

    if not batch_old_hint:
        batch_old_hint = compose_service_host(batch_old_service, batch_old_namespace)
    if not batch_new_hint:
        batch_new_hint = compose_service_host(batch_new_service, batch_new_namespace)

    print("\n【任务列表】")
    tasks = []
    while True:
        print(f"\n--- 任务 {len(tasks) + 1} ---")
        print("(直接回车结束任务添加)")
        old_route = input("老路由 (oldRoute): ").strip()
        if not old_route:
            break
        new_route = input("新路由 (newRoute): ").strip()
        method = input("HTTP 方法 [GET/POST/PUT/DELETE/PATCH] [默认: GET]: ").strip() or "GET"
        branch = input("目标分支 (branch): ").strip()

        old_service = batch_old_service
        new_service = batch_new_service
        old_namespace = batch_old_namespace
        new_namespace = batch_new_namespace
        old_hint = batch_old_hint
        new_hint = batch_new_hint
        gateway_repos = list(DEFAULT_GATEWAY_REPOS)
        apisix_admin_url = default_apisix_admin_url
        apisix_admin_urls = list(default_apisix_admin_urls)
        apisix_admin_key_env = default_apisix_key_env

        if ask_yes_no("是否设置当前任务的高级选项？", default=False):
            old_service = input("老服务名 (oldServiceName) [可空]: ").strip() or old_service
            new_service = input("新服务名 (newServiceName) [可空]: ").strip() or new_service
            old_namespace = input("老 namespace (oldNamespace) [可空]: ").strip() or old_namespace
            new_namespace = input("新 namespace (newNamespace) [可空]: ").strip() or new_namespace
            old_hint = input("老服务 hint (oldServiceHint) [可空]: ").strip() or old_hint
            new_hint = input("新服务 hint (newServiceHint) [可空]: ").strip() or new_hint
            gateway_repos_input = input(f"网关仓库 (逗号分隔，默认: {', '.join(DEFAULT_GATEWAY_REPOS)}): ").strip()
            if gateway_repos_input:
                gateway_repos = parse_csv(gateway_repos_input)
            apisix_admin_url = input(f"单个 APISIX Admin URL [默认: {default_apisix_admin_url or '(空)'}]: ").strip() or default_apisix_admin_url
            apisix_admin_urls_input = input(f"多个 APISIX Admin URLs (逗号分隔) [默认: {', '.join(default_apisix_admin_urls) or '(空)'}]: ").strip()
            if apisix_admin_urls_input:
                apisix_admin_urls = parse_csv(apisix_admin_urls_input)
            apisix_admin_key_env = input(f"APISIX Key 环境变量名 [默认: {default_apisix_key_env}]: ").strip() or default_apisix_key_env

        if not old_hint:
            old_hint = compose_service_host(old_service, old_namespace)
        if not new_hint:
            new_hint = compose_service_host(new_service, new_namespace)

        tasks.append({
            "taskId": f"route-cutover-{datetime.now().strftime('%Y%m%d')}-{len(tasks)+1:04d}",
            "oldRoute": old_route,
            "newRoute": new_route,
            "method": method,
            "branch": branch,
            "oldServiceName": old_service,
            "newServiceName": new_service,
            "oldNamespace": old_namespace,
            "newNamespace": new_namespace,
            "oldServiceHint": old_hint,
            "newServiceHint": new_hint,
            "gatewayRepos": gateway_repos,
            "apisixAdminURL": apisix_admin_url,
            "apisixAdminURLs": apisix_admin_urls,
            "apisixAdminKeyEnvVar": apisix_admin_key_env,
        })
        print(f"✓ 任务已添加: {tasks[-1]['taskId']}")

    if not tasks:
        print("\n[ERROR] 至少需要添加一个任务")
        return None

    batch_data = {
        "batchId": batch_id,
        "description": description or f"批量切换 {len(tasks)} 个接口",
        "feishuAlertOpenId": feishu_openid,
        "SOURCEGRAPH_URL": sourcegraph_url,
        "SOURCEGRAPH_TOKEN": sourcegraph_token,
        "GITLAB_URL": gitlab_url,
        "workspaceRoot": workspace,
        "oldServiceName": batch_old_service,
        "newServiceName": batch_new_service,
        "oldNamespace": batch_old_namespace,
        "newNamespace": batch_new_namespace,
        "oldServiceHint": batch_old_hint,
        "newServiceHint": batch_new_hint,
        "maxConcurrent": 1,
        "defaultTimeout": 1800,
        "retryLimit": 2,
        "tasks": tasks,
    }

    errors = validate_batch(batch_data)
    if errors:
        print("\n[ERROR] 验证失败:")
        for err in errors:
            print(f"  - {err}")
        return None

    file_path = save_batch_json(batch_data)
    print(f"\n[OK] 批次已保存: {file_path}")
    print(f"\n执行命令:\n  执行批次 {batch_id}")
    return batch_data


def quick_create(args: list):
    params = {}
    i = 0
    while i < len(args):
        if args[i].startswith("--"):
            key = args[i][2:]
            if i + 1 < len(args) and not args[i + 1].startswith("--"):
                params[key] = args[i + 1]
                i += 2
            else:
                params[key] = True
                i += 1
        else:
            i += 1

    required_single = ["oldRoute", "newRoute", "branch", "oldService", "newService", "oldNamespace", "newNamespace"]
    missing = [f for f in required_single if f not in params]
    if missing:
        print(f"[ERROR] 缺少必需参数: {', '.join(missing)}")
        print("\n使用示例:")
        print('  python3 batch_cli.py quick --oldRoute "/admin-room/list" --newRoute "/teacher-school/admin-room/list" --branch "feat/test" --oldService "teacher" --newService "teacher-school" --oldNamespace "teacherschool" --newNamespace "teacherschool"')
        print("\n完整参数:")
        print("  --oldRoute       老路由路径")
        print("  --newRoute       新路由路径")
        print("  --method         HTTP 方法 [默认: GET]")
        print("  --branch         目标分支")
        print("  --oldService     老服务名（必填）")
        print("  --newService     新服务名（必填）")
        print("  --oldNamespace   老 namespace（必填）")
        print("  --newNamespace   新 namespace（必填）")
        print("  --gatewayRepos   网关仓库 (逗号分隔)")
        print("  --apisixAdminURL 单个 APISIX Admin URL")
        print("  --apisixAdminURLs 多个 APISIX Admin URL (逗号分隔)")
        print("  --apisixKeyEnv   APISIX Key 环境变量名")
        print("  --batchId        批次ID [自动生成]")
        print("  --description    批次描述")
        return None

    cfg = load_config()
    batch_id = params.get("batchId", generate_batch_id())
    task = {
        "taskId": f"route-cutover-{datetime.now().strftime('%Y%m%d')}-0001",
        "oldRoute": params["oldRoute"],
        "newRoute": params["newRoute"],
        "method": params.get("method", "GET"),
        "branch": params["branch"],
        "oldServiceName": params.get("oldService", ""),
        "newServiceName": params.get("newService", ""),
        "oldNamespace": params.get("oldNamespace", ""),
        "newNamespace": params.get("newNamespace", ""),
        "oldServiceHint": params.get("oldHint", "") or compose_service_host(params.get("oldService", ""), params.get("oldNamespace", "")),
        "newServiceHint": params.get("newHint", "") or compose_service_host(params.get("newService", ""), params.get("newNamespace", "")),
        "gatewayRepos": parse_csv(params.get("gatewayRepos", "")) or list(DEFAULT_GATEWAY_REPOS),
        "apisixAdminURL": params.get("apisixAdminURL", ""),
        "apisixAdminURLs": parse_csv(params.get("apisixAdminURLs", "")),
        "apisixAdminKeyEnvVar": params.get("apisixKeyEnv", "APISIX_ADMIN_KEY"),
    }
    batch_data = {
        "batchId": batch_id,
        "description": params.get("description", f"接口切换: {task['oldRoute']} -> {task['newRoute']}"),
        "feishuAlertOpenId": cfg.get("feishuAlertOpenId", ""),
        "SOURCEGRAPH_URL": cfg.get("SOURCEGRAPH_URL", "https://sourcegraph.yc345.tv"),
        "SOURCEGRAPH_TOKEN": cfg.get("SOURCEGRAPH_TOKEN", os.environ.get("SOURCEGRAPH_TOKEN", "")),
        "GITLAB_URL": cfg.get("GITLAB_URL", "https://gitlab.yc345.tv"),
        "workspaceRoot": cfg.get("workspaceRoot", os.path.expanduser("~/work")),
        "oldServiceName": params.get("oldService", ""),
        "newServiceName": params.get("newService", ""),
        "oldNamespace": params.get("oldNamespace", ""),
        "newNamespace": params.get("newNamespace", ""),
        "oldServiceHint": params.get("oldHint", "") or compose_service_host(params.get("oldService", ""), params.get("oldNamespace", "")),
        "newServiceHint": params.get("newHint", "") or compose_service_host(params.get("newService", ""), params.get("newNamespace", "")),
        "maxConcurrent": 1,
        "defaultTimeout": 1800,
        "retryLimit": 2,
        "tasks": [task],
    }

    errors = validate_batch(batch_data)
    if errors:
        print("[ERROR] 验证失败:")
        for err in errors:
            print(f"  - {err}")
        return None

    file_path = save_batch_json(batch_data)
    print(f"[OK] 批次已保存: {file_path}")
    return batch_data


def list_batches():
    if not BATCHES_DIR.exists():
        print("暂无批次文件")
        return
    batches = sorted(BATCHES_DIR.glob("batch-*.json"))
    if not batches:
        print("暂无批次文件")
        return
    print(f"{'批次ID':<30} {'任务数':<10} {'描述'}")
    print("-" * 70)
    for batch_file in batches:
        try:
            with open(batch_file, encoding="utf-8") as f:
                data = json.load(f)
            print(f"{data['batchId']:<30} {len(data.get('tasks', [])):<10} {data.get('description', '')[:30]}")
        except Exception as e:  # noqa: BLE001
            print(f"{batch_file.name:<30} [读取失败: {e}]")


def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 batch_cli.py create          # 交互式创建批次")
        print("  python3 batch_cli.py quick <参数>    # 快速创建批次")
        print("  python3 batch_cli.py list            # 列出所有批次")
        print("\n快速创建示例:")
        print('  python3 batch_cli.py quick --oldRoute "/api/old" --newRoute "/api/new" --branch "feat/test" --oldService "teacher" --newService "teacher-school" --oldNamespace "teacherschool" --newNamespace "teacherschool"')
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "create":
        interactive_create()
    elif cmd == "quick":
        quick_create(sys.argv[2:])
    elif cmd == "list":
        list_batches()
    else:
        print(f"[ERROR] 未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
