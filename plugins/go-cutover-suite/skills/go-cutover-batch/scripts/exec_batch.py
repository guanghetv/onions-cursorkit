#!/usr/bin/env python3
"""
exec_batch.py — 批量任务执行器
按顺序执行每个任务，每次调用一次 agent CLI。
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

SCRIPT_DIR = Path(__file__).resolve().parent
PLUGIN_SKILLS_DIR = SCRIPT_DIR.parents[2] / "skills"
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import state  # noqa: E402

try:
    import alert as alert_mod  # noqa: E402
except Exception:  # noqa: BLE001
    alert_mod = None


DEFAULT_REPORT_DIR = str(Path(os.path.expanduser("~/work/_ai_reports/go-cutover")))
CONFIG_PATH = SCRIPT_DIR.parent / "references" / "config.json"
DEFAULT_GATEWAY_REPOS = [
    "onions-school",
    "channel-platform-server",
    "channel",
    "teacher-tenant",
]
SUCCESS_EXECUTION_STATUSES = {
    "success",
    "succeeded",
    "already_cut_over",
    "already-cut-over",
    "no_code_change",
    "no-code-change",
    "noop",
}
NO_CODE_EXECUTION_STATUSES = {
    "already_cut_over",
    "already-cut-over",
    "no_code_change",
    "no-code-change",
    "noop",
}
FAILURE_EXECUTION_STATUSES = {"failed", "blocked", "error", "cancelled"}
RETRYABLE_REASONS = {"timeout", "process_exit", "process_exception"}
REPORT_PATH_PATTERN = re.compile(rf"{re.escape(DEFAULT_REPORT_DIR)}/\d{{8}}-\d{{6}}")
SOURCEGRAPH_TOKEN_PATTERN = re.compile(r"\b[0-9a-f]{40}\b", re.I)
REQUIRED_REPORT_FILES = [
    "summary.md",
    "route-locator.md",
    "backend-changes.md",
    "gateway-trace.md",
    "frontend-entrypoints.md",
    "artifacts/execution.json",
]

def resolve_sourcegraph_token_script() -> Path:
    env_path = os.environ.get("SOURCEGRAPH_TOKEN_SCRIPT", "").strip()
    candidates = [
        Path(env_path).expanduser() if env_path else None,
        PLUGIN_SKILLS_DIR / "sourcegraph-token" / "scripts" / "get_token.py",
        Path.home() / ".cursor" / "skills" / "sourcegraph-token" / "scripts" / "get_token.py",
    ]
    for candidate in candidates:
        if candidate and candidate.exists():
            return candidate
    return PLUGIN_SKILLS_DIR / "sourcegraph-token" / "scripts" / "get_token.py"


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


def unique_strings(values: List[str]) -> List[str]:
    seen = set()
    ordered = []
    for value in values:
        value = value.strip()
        if not value or value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def normalize_multi_value(value) -> List[str]:
    if not value:
        return []
    if isinstance(value, list):
        return unique_strings([str(item) for item in value if str(item).strip()])
    if isinstance(value, str):
        return unique_strings([item.strip() for item in value.split(",") if item.strip()])
    return []


def extract_token_from_output(output_text: str) -> str:
    matches = SOURCEGRAPH_TOKEN_PATTERN.findall(output_text or "")
    return matches[-1] if matches else ""


def ensure_sourcegraph_token(sourcegraph_url: str) -> Tuple[bool, str, str]:
    sourcegraph_token_script = resolve_sourcegraph_token_script()
    if not sourcegraph_token_script.exists():
        return False, "", f"sourcegraph token script missing: {sourcegraph_token_script}"
    cmd = ["python3", str(sourcegraph_token_script)]
    if sourcegraph_url:
        cmd.extend(["--sourcegraph-url", sourcegraph_url])
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "", "sourcegraph token refresh timeout"
    output_text = (completed.stdout or "") + (completed.stderr or "")
    token = extract_token_from_output(output_text)
    if completed.returncode == 0 and token:
        return True, token, output_text.strip()
    reason = output_text.strip() or f"sourcegraph token command failed with exit {completed.returncode}"
    return False, "", reason


def build_single_prompt(task: dict, batch_id: str, task_index: int, total: int) -> str:
    lines = [
        "/go-cutover-orchestrator",
        "",
        f"任务 {task_index}/{total}：{task['method']} {task['oldRoute']} → {task['newRoute']}",
        "执行要求：这是批量无交互执行任务，不要向用户追问，不要等待用户确认，不要在中途停下。",
        "执行要求：遇到非硬阻塞问题时自行推断并继续，直到任务完成。",
        "执行要求：如果产生代码改动，自动完成 commit、push，并为改动仓库创建一个指向 dev 的 Merge Request；把 MR 状态和链接写进报告与 execution.json。",
        "执行要求：如果 MR 不能自动创建，至少记录 mergeRequestStatus、失败原因和可直达的创建链接。",
        "执行要求：把这一批当成全新任务，从头开始做，不要复用旧批次、旧报告、旧状态里的结论来跳过步骤。",
        "执行要求：如果判断 already cut over，也必须基于本次重新检查当前代码后的结论，而不是沿用上次结果。",
        "",
        f"SOURCEGRAPH_URL: {task.get('SOURCEGRAPH_URL', '')}",
        f"SOURCEGRAPH_TOKEN: {task.get('SOURCEGRAPH_TOKEN', '')}",
        f"GITLAB_URL: {task.get('GITLAB_URL', '')}",
        f"GITLAB_TOKEN: {task.get('GITLAB_TOKEN', '')}",
        "",
        f"oldRoute: {task['oldRoute']}",
        f"newRoute: {task['newRoute']}",
        f"method: {task['method']}",
        f"branch: {task['branch']}",
        f"oldServiceName: {task.get('oldServiceName', '')}",
        f"newServiceName: {task.get('newServiceName', '')}",
        f"oldNamespace: {task.get('oldNamespace', '')}",
        f"newNamespace: {task.get('newNamespace', '')}",
        f"oldServiceHint: {task.get('oldServiceHint', '')}",
        f"newServiceHint: {task.get('newServiceHint', '')}",
        f"workspaceRoot: {task['workspaceRoot']}",
    ]
    optional_fields = [
        ("gatewayRepos", task.get("gatewayRepos", [])),
        ("apisixAdminURL", task.get("apisixAdminURL", "")),
        ("apisixAdminURLs", task.get("apisixAdminURLs", [])),
        ("apisixAdminKeyEnvVar", task.get("apisixAdminKeyEnvVar", "")),
    ]
    for key, value in optional_fields:
        if isinstance(value, list) and value:
            lines.append(f"{key}: {', '.join(value)}")
        elif isinstance(value, str) and value.strip():
            lines.append(f"{key}: {value.strip()}")
    return "\n".join(lines) + "\n"


def snapshot_report_dirs(report_dir: str) -> Dict[str, float]:
    report_path = Path(report_dir)
    if not report_path.exists():
        return {}
    return {
        str(child): child.stat().st_mtime
        for child in report_path.iterdir()
        if child.is_dir()
    }


def extract_report_dirs_from_output(output_text: str) -> List[str]:
    return unique_strings(REPORT_PATH_PATTERN.findall(output_text))


def find_task_report(report_dir: str, before_snapshot: Dict[str, float], task_start_time: float, output_text: str) -> str:
    candidates = []
    for path in extract_report_dirs_from_output(output_text):
        if Path(path).exists():
            candidates.append(Path(path))
    report_path = Path(report_dir)
    if report_path.exists():
        for child in report_path.iterdir():
            if not child.is_dir():
                continue
            current_mtime = child.stat().st_mtime
            previous_mtime = before_snapshot.get(str(child))
            if (previous_mtime is None or current_mtime > previous_mtime) and current_mtime >= task_start_time - 5:
                candidates.append(child)
    if not candidates:
        return ""
    deduped = {str(path): path for path in candidates}
    return str(sorted(deduped.values(), key=lambda item: item.stat().st_mtime, reverse=True)[0])


def read_json_file(path: Path) -> Optional[dict]:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:  # noqa: BLE001
        return None


def has_execution_evidence(value) -> bool:
    if value is None:
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, dict):
        return any(has_execution_evidence(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(has_execution_evidence(item) for item in value)
    return bool(value)


def has_merge_request_results(value) -> bool:
    if not isinstance(value, list) or not value:
        return False
    for item in value:
        if not isinstance(item, dict):
            continue
        if item.get("repo") and item.get("status") and (item.get("url") or item.get("createUrl")):
            return True
    return False


def validate_report_dir(report_dir: str) -> Tuple[bool, str, dict]:
    if not report_dir:
        return False, "report_missing", {}
    path = Path(report_dir)
    if not path.exists() or not path.is_dir():
        return False, "report_missing", {}
    missing_files = [rel for rel in REQUIRED_REPORT_FILES if not (path / rel).exists()]
    if missing_files:
        return False, f"report_incomplete: missing {', '.join(missing_files)}", {}
    execution = read_json_file(path / "artifacts" / "execution.json")
    if not execution:
        return False, "execution_json_invalid", {}
    status = str(execution.get("status", "")).strip().lower()
    if not status:
        return False, "execution_status_missing", execution
    if status in FAILURE_EXECUTION_STATUSES:
        return False, f"execution_status_{status}", execution
    if status not in SUCCESS_EXECUTION_STATUSES:
        return False, f"execution_status_unknown:{status}", execution
    if status not in NO_CODE_EXECUTION_STATUSES:
        commit_evidence = execution.get("commitsCreated") or execution.get("commitShas") or execution.get("commit_shas")
        push_evidence = execution.get("pushesCompleted") or execution.get("pushes_completed") or execution.get("pushStatus") or execution.get("push_status")
        mr_evidence = execution.get("mergeRequests") or execution.get("merge_requests")
        if not has_execution_evidence(commit_evidence):
            return False, "execution_commit_missing", execution
        if not has_execution_evidence(push_evidence):
            return False, "execution_push_missing", execution
        if not has_merge_request_results(mr_evidence):
            return False, "execution_merge_request_missing", execution
    return True, status, execution


def classify_retry_reason(reason: str) -> bool:
    return reason in RETRYABLE_REASONS


def task_lock_repos(task: dict) -> List[str]:
    gateway_repos = task.get("gatewayRepos", [])
    target_repos = task.get("targetRepos", [])
    return unique_strings(gateway_repos + target_repos)


def acquire_task_locks(conn, task: dict) -> Tuple[bool, List[str], str]:
    branch = task["branch"]
    task_id = task["taskId"]
    acquired = []
    for repo in task_lock_repos(task):
        if state.acquire_lock(conn, repo, branch, task_id):
            acquired.append(repo)
            continue
        holder = state.get_lock_holder(conn, repo, branch)
        for held_repo in acquired:
            state.release_lock(conn, held_repo, branch, task_id)
        conn.commit()
        return False, [], f"repo+branch locked by {holder or 'unknown'}: {repo}@{branch}"
    conn.commit()
    return True, acquired, ""


def release_task_locks(conn, repos: List[str], branch: str, task_id: str):
    for repo in repos:
        state.release_lock(conn, repo, branch, task_id)
    conn.commit()


def send_alert_if_possible(kind: str, open_id: str, **kwargs):
    if not open_id or not alert_mod:
        return
    if not os.environ.get("QCLAW_FEISHU_APP_SECRET", "").strip():
        return
    try:
        alert_mod.send_alert(kind, open_id, **kwargs)
    except Exception:  # noqa: BLE001
        pass


def exec_single_task(task: dict, batch_id: str, task_index: int, total: int, timeout: int, report_dir: str) -> dict:
    task_id = task["taskId"]
    workspace_root = task["workspaceRoot"]
    log_dir = Path(workspace_root) / "openclaw-runner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"task-{task_id}.log"
    prompt_file = log_dir / f"prompt-{task_id}.txt"
    prompt = build_single_prompt(task, batch_id, task_index, total)
    prompt_file.write_text(prompt, encoding="utf-8")

    before_snapshot = snapshot_report_dirs(report_dir)
    task_start_time = time.time()
    start = task_start_time
    cmd = ["agent", "-p", "--yolo", "--output-format", "stream-json", prompt]
    env = os.environ.copy()
    for key in ("SOURCEGRAPH_URL", "SOURCEGRAPH_TOKEN", "GITLAB_URL", "GITLAB_TOKEN"):
        value = str(task.get(key, "")).strip()
        if value:
            env[key] = value

    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, cwd=workspace_root, timeout=timeout, env=env)
        elapsed = time.time() - start
        output_text = (completed.stdout or "") + (completed.stderr or "")
        tool_calls = 0
        for line in output_text.splitlines():
            try:
                data = json.loads(line)
            except Exception:  # noqa: BLE001
                continue
            if data.get("type") == "tool_call" and data.get("subtype") == "started":
                tool_calls += 1
        report_path = find_task_report(report_dir, before_snapshot, task_start_time, output_text)
        report_ok, execution_state, execution_data = validate_report_dir(report_path)

        with open(log_file, "w", encoding="utf-8") as log_f:
            log_f.write(f"[TASK] {task_id}\n")
            log_f.write(f"[PROGRESS] {task_index}/{total}\n")
            log_f.write(f"[ROUTE] {task['method']} {task['oldRoute']} → {task['newRoute']}\n")
            log_f.write(f"[CMD] {' '.join(cmd[:-1])}\n")
            log_f.write(f"[START] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_start_time))}\n")
            log_f.write(f"[EXIT] {completed.returncode}\n")
            log_f.write(f"[ELAPSED] {elapsed:.1f}s\n")
            log_f.write(f"[TOOL_CALLS] {tool_calls}\n")
            log_f.write(f"[REPORT] {report_path or '-'}\n")
            log_f.write(f"[REPORT_VALID] {report_ok}\n")
            log_f.write(f"[EXECUTION_STATE] {execution_state}\n\n")
            log_f.write(output_text)

        if completed.returncode != 0:
            return {
                "taskId": task_id,
                "taskIndex": task_index,
                "exitCode": completed.returncode,
                "elapsed": elapsed,
                "success": False,
                "reason": "process_exit",
                "reportDir": report_path,
                "logFile": str(log_file),
                "promptFile": str(prompt_file),
                "toolCalls": tool_calls,
                "executionState": execution_state,
                "execution": execution_data,
            }
        if not report_ok:
            return {
                "taskId": task_id,
                "taskIndex": task_index,
                "exitCode": completed.returncode,
                "elapsed": elapsed,
                "success": False,
                "reason": execution_state,
                "reportDir": report_path,
                "logFile": str(log_file),
                "promptFile": str(prompt_file),
                "toolCalls": tool_calls,
                "executionState": execution_state,
                "execution": execution_data,
            }
        return {
            "taskId": task_id,
            "taskIndex": task_index,
            "total": total,
            "oldRoute": task["oldRoute"],
            "newRoute": task["newRoute"],
            "method": task["method"],
            "exitCode": completed.returncode,
            "elapsed": elapsed,
            "success": True,
            "mode": "agent-sequential",
            "logFile": str(log_file),
            "promptFile": str(prompt_file),
            "toolCalls": tool_calls,
            "reportDir": report_path,
            "executionState": execution_state,
            "execution": execution_data,
        }
    except subprocess.TimeoutExpired as exc:
        elapsed = time.time() - start
        output_text = (exc.stdout or "") + (exc.stderr or "")
        report_path = find_task_report(report_dir, before_snapshot, task_start_time, output_text)
        with open(log_file, "w", encoding="utf-8") as log_f:
            log_f.write(f"[TASK] {task_id}\n")
            log_f.write(f"[START] {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(task_start_time))}\n")
            log_f.write(f"[ELAPSED] {elapsed:.1f}s\n")
            log_f.write("[TIMEOUT] true\n")
            log_f.write(output_text)
        return {
            "taskId": task_id,
            "taskIndex": task_index,
            "exitCode": -1,
            "elapsed": elapsed,
            "success": False,
            "reason": "timeout",
            "reportDir": report_path,
            "logFile": str(log_file),
            "promptFile": str(prompt_file),
            "toolCalls": 0,
            "executionState": "",
            "execution": {},
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "taskId": task_id,
            "taskIndex": task_index,
            "exitCode": -2,
            "elapsed": time.time() - start,
            "success": False,
            "reason": "process_exception",
            "error": str(exc),
            "reportDir": "",
            "logFile": str(log_file),
            "promptFile": str(prompt_file),
            "toolCalls": 0,
            "executionState": "",
            "execution": {},
        }


def exec_task_with_retries(task: dict, batch_id: str, task_index: int, total: int, report_dir: str) -> dict:
    timeout = int(task.get("timeout", 1800))
    retry_limit = int(task.get("retryLimit", 2))
    attempts = 0
    backoffs = [60, 300]
    last_result = {}
    while True:
        attempts += 1
        last_result = exec_single_task(task, batch_id, task_index, total, timeout, report_dir)
        last_result["attempt"] = attempts
        if last_result["success"]:
            return last_result
        if attempts > retry_limit or not classify_retry_reason(last_result.get("reason", "")):
            return last_result
        wait_seconds = backoffs[min(attempts - 1, len(backoffs) - 1)]
        last_result["retryScheduledIn"] = wait_seconds
        time.sleep(wait_seconds)


def normalize_task(batch_data: dict, task: dict, index: int, config: dict) -> dict:
    workspace_root = task.get("workspaceRoot") or batch_data.get("workspaceRoot") or config.get("workspaceRoot") or os.path.expanduser("~/work")
    sourcegraph_url = batch_data.get("SOURCEGRAPH_URL") or config.get("SOURCEGRAPH_URL", "")
    sourcegraph_token = task.get("SOURCEGRAPH_TOKEN") or batch_data.get("SOURCEGRAPH_TOKEN") or os.environ.get("SOURCEGRAPH_TOKEN") or config.get("SOURCEGRAPH_TOKEN", "")
    gitlab_url = batch_data.get("GITLAB_URL") or config.get("GITLAB_URL", "")
    gitlab_token = task.get("GITLAB_TOKEN") or batch_data.get("GITLAB_TOKEN") or os.environ.get("GITLAB_TOKEN") or config.get("GITLAB_TOKEN", "")
    return {
        "taskId": task.get("taskId") or f"{batch_data['batchId']}-task-{index:04d}",
        "batchId": batch_data["batchId"],
        "oldRoute": task["oldRoute"],
        "newRoute": task["newRoute"],
        "method": task["method"],
        "branch": task["branch"],
        "workspaceRoot": workspace_root,
        "SOURCEGRAPH_URL": sourcegraph_url,
        "SOURCEGRAPH_TOKEN": sourcegraph_token,
        "GITLAB_URL": gitlab_url,
        "GITLAB_TOKEN": gitlab_token,
        "oldServiceName": task.get("oldServiceName") or batch_data.get("oldServiceName", ""),
        "newServiceName": task.get("newServiceName") or batch_data.get("newServiceName", ""),
        "oldNamespace": task.get("oldNamespace") or batch_data.get("oldNamespace", ""),
        "newNamespace": task.get("newNamespace") or batch_data.get("newNamespace", ""),
        "oldServiceHint": task.get("oldServiceHint") or batch_data.get("oldServiceHint", ""),
        "newServiceHint": task.get("newServiceHint") or batch_data.get("newServiceHint", ""),
        "targetRepos": normalize_multi_value(task.get("targetRepos", [])),
        "gatewayRepos": normalize_multi_value(task.get("gatewayRepos", [])) or list(DEFAULT_GATEWAY_REPOS),
        "apisixAdminURL": str(task.get("apisixAdminURL", "")).strip(),
        "apisixAdminURLs": normalize_multi_value(task.get("apisixAdminURLs", [])),
        "apisixAdminKeyEnvVar": str(task.get("apisixAdminKeyEnvVar", "")).strip(),
        "timeout": int(task.get("timeout", batch_data.get("defaultTimeout", 1800))),
        "retryLimit": int(task.get("retryLimit", batch_data.get("retryLimit", 2))),
    }


def load_batch_file(batch_path: str) -> dict:
    with open(batch_path, encoding="utf-8") as f:
        batch_data = json.load(f)
    config = load_config()
    normalized_batch = {
        "batchId": batch_data.get("batchId", f"batch-{datetime.now().strftime('%Y%m%d-%H%M%S')}"),
        "description": batch_data.get("description", ""),
        "feishuAlertOpenId": batch_data.get("feishuAlertOpenId") or config.get("feishuAlertOpenId", ""),
        "SOURCEGRAPH_URL": batch_data.get("SOURCEGRAPH_URL") or config.get("SOURCEGRAPH_URL", ""),
        "SOURCEGRAPH_TOKEN": batch_data.get("SOURCEGRAPH_TOKEN") or os.environ.get("SOURCEGRAPH_TOKEN") or config.get("SOURCEGRAPH_TOKEN", ""),
        "GITLAB_URL": batch_data.get("GITLAB_URL") or config.get("GITLAB_URL", ""),
        "GITLAB_TOKEN": batch_data.get("GITLAB_TOKEN") or os.environ.get("GITLAB_TOKEN") or config.get("GITLAB_TOKEN", ""),
        "workspaceRoot": batch_data.get("workspaceRoot") or config.get("workspaceRoot") or os.path.expanduser("~/work"),
        "oldServiceName": batch_data.get("oldServiceName", ""),
        "newServiceName": batch_data.get("newServiceName", ""),
        "oldNamespace": batch_data.get("oldNamespace", ""),
        "newNamespace": batch_data.get("newNamespace", ""),
        "oldServiceHint": batch_data.get("oldServiceHint", ""),
        "newServiceHint": batch_data.get("newServiceHint", ""),
        "maxConcurrent": 1,
        "defaultTimeout": int(batch_data.get("defaultTimeout", 1800)),
        "retryLimit": int(batch_data.get("retryLimit", 2)),
        "tasks": [],
    }
    for index, task in enumerate(batch_data.get("tasks", []), start=1):
        normalized_batch["tasks"].append(normalize_task(normalized_batch, task, index, config))
    return normalized_batch


def determine_batch_status(summary: dict) -> str:
    if summary["blocked"] > 0:
        return "batchPartialFailed" if summary["success"] > 0 else "batchFailed"
    if summary["failed"] > 0:
        return "batchPartialFailed" if summary["success"] > 0 else "batchFailed"
    return "batchSucceeded"


def exec_batch_sequential(batch_data: dict, report_dir: str, db_path: Optional[str] = None) -> dict:
    report_dir = report_dir or DEFAULT_REPORT_DIR
    batch_id = batch_data["batchId"]
    tasks = batch_data["tasks"]
    total = len(tasks)
    start = time.time()
    conn = state.get_db(db_path or state.DEFAULT_DB)

    state.upsert_batch(conn, batch_id, batch_data.get("description", ""), total)
    for task in tasks:
        state.upsert_task(conn, task["taskId"], batch_id, task, status="queued")
    conn.commit()

    print(f"\n{'=' * 60}")
    print(f"批次执行开始: {batch_id}")
    print(f"任务数: {total}")
    print(f"{'=' * 60}\n")

    results = []
    succeeded = 0
    failed = 0
    blocked = 0
    merge_requests = []
    open_id = batch_data.get("feishuAlertOpenId", "")

    for index, task in enumerate(tasks, start=1):
        print(f"\n[{index}/{total}] 执行任务: {task['method']} {task['oldRoute']} → {task['newRoute']}")
        print(f"{'-' * 50}")

        ok, locked_repos, lock_reason = acquire_task_locks(conn, task)
        if not ok:
            result = {
                "taskId": task["taskId"],
                "taskIndex": index,
                "exitCode": -3,
                "elapsed": 0,
                "success": False,
                "reason": "lock_conflict",
                "detail": lock_reason,
                "reportDir": "",
                "logFile": "",
            }
            results.append(result)
            blocked += 1
            state.update_task_status(conn, task["taskId"], "blocked", error_type="lock_conflict", error_msg=lock_reason)
            state.update_batch_counts(conn, batch_id)
            conn.commit()
            send_alert_if_possible("task_blocked", open_id, task=task, reason=lock_reason)
            print(f"⛔ 阻塞: {lock_reason}")
            continue

        try:
            state.set_task_running(conn, task["taskId"])
            state.heartbeat(conn, task["taskId"])
            conn.commit()

            result = exec_task_with_retries(task, batch_id, index, total, report_dir)
            results.append(result)
            execution = result.get("execution", {}) or {}
            repos_touched = execution.get("reposTouched") or execution.get("repos_touched") or []
            commit_shas = execution.get("commitsCreated") or execution.get("commitShas") or execution.get("commit_shas") or []
            merge_requests.extend(execution.get("mergeRequests") or execution.get("merge_requests") or [])

            if result["success"]:
                succeeded += 1
                state.update_task_status(conn, task["taskId"], "succeeded", report_path=result.get("reportDir"), repos_touched=repos_touched, commit_shas=commit_shas)
                print(f"✅ 成功 ({result['elapsed']:.1f}s, {result.get('toolCalls', 0)} tool calls)")
                if result.get("reportDir"):
                    print(f"📋 报告: {result['reportDir']}")
            else:
                final_status = "blocked" if result.get("reason") == "lock_conflict" else "failed"
                failed += 1 if final_status == "failed" else 0
                blocked += 1 if final_status == "blocked" else 0
                state.update_task_status(
                    conn,
                    task["taskId"],
                    final_status,
                    error_type=result.get("reason"),
                    error_msg=result.get("detail") or result.get("error") or result.get("reason"),
                    report_path=result.get("reportDir"),
                    repos_touched=repos_touched,
                    commit_shas=commit_shas,
                )
                reason = result.get("detail") or result.get("error") or result.get("reason")
                print(f"❌ 失败: {reason}")
                send_alert_if_possible("task_failed", open_id, task=task, reason=reason, report=result.get("reportDir", ""))

            state.update_batch_counts(conn, batch_id)
            conn.commit()
        finally:
            release_task_locks(conn, locked_repos, task["branch"], task["taskId"])

    elapsed = time.time() - start
    summary = {
        "batchId": batch_id,
        "description": batch_data.get("description", ""),
        "total": total,
        "success": succeeded,
        "failed": failed,
        "blocked": blocked,
        "elapsed": elapsed,
        "mode": "sequential",
        "mergeRequests": merge_requests,
        "results": results,
    }
    batch_status = determine_batch_status(summary)
    state.finish_batch(conn, batch_id, batch_status)
    state.update_batch_counts(conn, batch_id)
    conn.commit()
    conn.close()

    print(f"\n{'=' * 60}")
    print(f"批次执行完成: {batch_id}")
    print(f"成功: {succeeded}/{total}")
    print(f"失败: {failed}")
    print(f"阻塞: {blocked}")
    print(f"耗时: {elapsed:.1f}s")
    print(f"{'=' * 60}\n")

    send_alert_if_possible(
        "batch_summary",
        open_id,
        batch_id=batch_id,
        total=total,
        succeeded=succeeded,
        failed=failed,
        blocked=blocked,
        started_at=datetime.fromtimestamp(start).strftime("%Y-%m-%d %H:%M:%S"),
        finished_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="批量执行接口路由切换任务")
    parser.add_argument("batch_file", help="批次 JSON 文件路径")
    parser.add_argument("--report-dir", default=DEFAULT_REPORT_DIR, help=f"报告目录，默认 {DEFAULT_REPORT_DIR}")
    parser.add_argument("--state-db", default=state.DEFAULT_DB, help="SQLite 状态库路径")
    args = parser.parse_args()

    batch_data = load_batch_file(args.batch_file)
    ok, token, token_detail = ensure_sourcegraph_token(batch_data.get("SOURCEGRAPH_URL", ""))
    if not ok:
        print("\n" + "=" * 60)
        print("⛔ Sourcegraph token 自动检查/刷新失败")
        print(token_detail)
        print("=" * 60 + "\n")
        sys.exit(1)
    batch_data["SOURCEGRAPH_TOKEN"] = token
    os.environ["SOURCEGRAPH_TOKEN"] = token
    for task in batch_data["tasks"]:
        task["SOURCEGRAPH_TOKEN"] = token
    print("\n" + "=" * 60)
    print("🔐 Sourcegraph token 已就绪")
    print(token_detail)
    print("=" * 60 + "\n")
    tasks = batch_data["tasks"]
    print(f"\n{'=' * 60}")
    print(f"加载 {len(tasks)} 个任务:")
    for index, task in enumerate(tasks, start=1):
        print(f"  {index}. {task['method']} {task['oldRoute']} → {task['newRoute']}")
    print(f"{'=' * 60}\n")

    result = exec_batch_sequential(batch_data, args.report_dir, args.state_db)
    result_file = Path(batch_data["workspaceRoot"]) / "openclaw-runner" / "logs" / f"result-{result['batchId']}.json"
    result_file.parent.mkdir(parents=True, exist_ok=True)
    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"📁 日志: {batch_data['workspaceRoot']}/openclaw-runner/logs/")
    print(f"📋 报告: {args.report_dir}/")
    print(f"📄 结果: {result_file}")
    report_dirs = [item.get("reportDir", "") for item in result["results"] if item.get("reportDir")]
    if report_dirs:
        print("\n任务报告:")
        for index, path in enumerate(report_dirs, start=1):
            print(f"  {index}. {path}")
    merge_request_items = []
    for item in result["results"]:
        execution = item.get("execution") or {}
        for mr in execution.get("mergeRequests") or execution.get("merge_requests") or []:
            if isinstance(mr, dict):
                merge_request_items.append(mr)
    if merge_request_items:
        print("\nMerge Requests:")
        for index, mr in enumerate(merge_request_items, start=1):
            target = mr.get("targetBranch", "dev")
            status = mr.get("status", "unknown")
            url = mr.get("url") or mr.get("createUrl") or "-"
            repo = mr.get("repo", "unknown")
            print(f"  {index}. [{status}] {repo} -> {target}: {url}")
    print(f"{'=' * 60}\n")
    sys.exit(0 if result["failed"] == 0 and result["blocked"] == 0 else 1)
