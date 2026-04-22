#!/usr/bin/env python3
"""
exec_cursor.py — 单接口任务执行器
使用 Cursor GUI 或 Headless CLI 执行 go-cutover-orchestrator 任务
"""
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

PLUGIN_SKILLS_DIR = Path(__file__).resolve().parents[2]
SOURCEGRAPH_TOKEN_PATTERN = re.compile(r"\b[0-9a-f]{40}\b", re.I)


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


def build_prompt(task: dict) -> str:
    lines = [
        "/go-cutover-orchestrator",
        "执行要求：这是无交互执行任务，不要向用户追问，不要等待用户确认，不要在中途停下。",
        "执行要求：遇到非硬阻塞问题时自行推断并继续，直到任务完成。",
        "执行要求：如果产生代码改动，自动完成 commit、push，并为改动仓库创建一个指向 dev 的 Merge Request；把 MR 状态和链接写进报告与 execution.json。",
        "执行要求：如果 MR 不能自动创建，至少记录 mergeRequestStatus、失败原因和可直达的创建链接。",
        "执行要求：把这次任务当成全新任务，从头开始做，不要复用旧批次、旧报告、旧状态里的结论来跳过步骤。",
        "执行要求：如果判断 already cut over，也必须基于本次重新检查当前代码后的结论，而不是沿用上次结果。",
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


def extract_token_from_output(output_text: str) -> str:
    matches = SOURCEGRAPH_TOKEN_PATTERN.findall(output_text or "")
    return matches[-1] if matches else ""


def ensure_sourcegraph_token(task: dict) -> tuple[bool, str]:
    sourcegraph_token_script = resolve_sourcegraph_token_script()
    if not sourcegraph_token_script.exists():
        return False, f"sourcegraph token script missing: {sourcegraph_token_script}"
    cmd = ["python3", str(sourcegraph_token_script)]
    if str(task.get("SOURCEGRAPH_URL", "")).strip():
        cmd.extend(["--sourcegraph-url", str(task.get("SOURCEGRAPH_URL", "")).strip()])
    try:
        completed = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except subprocess.TimeoutExpired:
        return False, "sourcegraph token refresh timeout"
    output_text = (completed.stdout or "") + (completed.stderr or "")
    token = extract_token_from_output(output_text)
    if completed.returncode == 0 and token:
        task["SOURCEGRAPH_TOKEN"] = token
        os.environ["SOURCEGRAPH_TOKEN"] = token
        return True, output_text.strip()
    return False, output_text.strip() or f"sourcegraph token command failed with exit {completed.returncode}"


def check_binary(name: str) -> bool:
    result = subprocess.run(["which", name], capture_output=True, text=True)
    return result.returncode == 0


def exec_task_gui(task: dict) -> dict:
    task_id = task["taskId"]
    prompt = build_prompt(task)
    work_dir = task.get("workspaceRoot", os.path.expanduser("~/work"))
    log_dir = Path(work_dir) / "openclaw-runner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"worker-{task_id}.log"
    prompt_file = log_dir / f"prompt-{task_id}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")

    start = time.time()
    try:
        subprocess.Popen(
            ["cursor", work_dir],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        elapsed = time.time() - start
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"[EXEC] taskId={task_id}\n")
            f.write("[MODE] GUI\n")
            f.write(f"[PROMPT_FILE] {prompt_file}\n")
            f.write(f"[START] {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"[PROMPT]\n{prompt}\n")
            f.write("\n[NOTE] Cursor GUI 已打开，请手动执行上述 prompt\n")
        return {
            "taskId": task_id,
            "exitCode": 0,
            "elapsed": elapsed,
            "success": True,
            "mode": "gui",
            "logFile": str(log_file),
            "promptFile": str(prompt_file),
            "note": "Cursor GUI 已打开，请复制 prompt 到 Cursor 中执行",
        }
    except Exception as e:  # noqa: BLE001
        return {
            "taskId": task_id,
            "exitCode": -2,
            "elapsed": time.time() - start,
            "success": False,
            "reason": f"exception: {e}",
            "logFile": str(log_file),
        }


def exec_task_agent(task: dict, timeout: int = 3600) -> dict:
    task_id = task["taskId"]
    prompt = build_prompt(task)
    work_dir = task.get("workspaceRoot", os.path.expanduser("~/work"))
    log_dir = Path(work_dir) / "openclaw-runner" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / f"worker-{task_id}.log"
    prompt_file = log_dir / f"prompt-{task_id}.txt"
    prompt_file.write_text(prompt, encoding="utf-8")
    start = time.time()

    try:
        cmd = ["agent", "-p", "--yolo", "--output-format", "stream-json", prompt]
        with open(log_file, "w", encoding="utf-8") as log_f:
            log_f.write(f"[EXEC] taskId={task_id}\n")
            log_f.write("[MODE] AGENT HEADLESS\n")
            log_f.write(f"[WORKDIR] {work_dir}\n")
            log_f.write(f"[START] {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            log_f.flush()

            env = os.environ.copy()
            for key in ("SOURCEGRAPH_URL", "SOURCEGRAPH_TOKEN", "GITLAB_URL", "GITLAB_TOKEN"):
                value = str(task.get(key, "")).strip()
                if value:
                    env[key] = value
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                cwd=work_dir,
                env=env,
            )
            output_lines = []
            tool_calls = 0
            for line in process.stdout:
                output_lines.append(line)
                log_f.write(line)
                log_f.flush()
                try:
                    data = json.loads(line)
                except Exception:  # noqa: BLE001
                    continue
                if data.get("type") == "tool_call" and data.get("subtype") == "started":
                    tool_calls += 1

            process.wait(timeout=timeout)
            elapsed = time.time() - start
            log_f.write(f"\n[END] {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            log_f.write(f"[EXIT] {process.returncode}\n")
            log_f.write(f"[ELAPSED] {elapsed:.1f}s\n")
            log_f.write(f"[TOOL_CALLS] {tool_calls}\n")

        output = "".join(output_lines)
        return {
            "taskId": task_id,
            "exitCode": process.returncode,
            "elapsed": elapsed,
            "success": process.returncode == 0,
            "mode": "agent-headless",
            "logFile": str(log_file),
            "promptFile": str(prompt_file),
            "toolCalls": tool_calls,
            "outputPreview": output[:500] if output else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "taskId": task_id,
            "exitCode": -1,
            "elapsed": time.time() - start,
            "success": False,
            "reason": "timeout",
            "logFile": str(log_file),
        }
    except Exception as e:  # noqa: BLE001
        return {
            "taskId": task_id,
            "exitCode": -2,
            "elapsed": time.time() - start,
            "success": False,
            "reason": f"exception: {e}",
            "logFile": str(log_file),
        }


def exec_task(task: dict, timeout: int = 3600) -> dict:
    ok, detail = ensure_sourcegraph_token(task)
    if not ok:
        return {
            "taskId": task.get("taskId", "unknown"),
            "exitCode": -5,
            "elapsed": 0,
            "success": False,
            "reason": f"sourcegraph_token_refresh_failed: {detail}",
        }
    if check_binary("agent"):
        return exec_task_agent(task, timeout)
    if check_binary("cursor"):
        return exec_task_gui(task)
    return {
        "taskId": task.get("taskId", "unknown"),
        "exitCode": -4,
        "elapsed": 0,
        "success": False,
        "reason": "Cursor not found. Please install Cursor.",
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: exec_cursor.py <task_json_file>")
        sys.exit(1)

    task_file = sys.argv[1]
    with open(task_file, encoding="utf-8") as f:
        task = json.load(f)

    result = exec_task(task)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["success"] else 1)
