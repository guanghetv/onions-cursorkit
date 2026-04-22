#!/usr/bin/env python3
"""
alert.py — 飞书告警发送器
"""
import urllib.request
import json
import os
import sys

FEISHU_APP_ID = "cli_a924cd48e1fd9bd1"
FEISHU_APP_SECRET = os.environ.get("QCLAW_FEISHU_APP_SECRET", "")


def get_token(app_id: str, app_secret: str) -> str:
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
        data=json.dumps({"app_id": app_id, "app_secret": app_secret}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read())
    return data["tenant_access_token"]


def send_text(token: str, open_id: str, text: str) -> dict:
    payload = {
        "receive_id": open_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def alert_task_failed(task: dict, reason: str, report_path: str = "") -> str:
    return (
        f"【接口切换失败】\n"
        f"批次: {task.get('batchId', '-')}\n"
        f"任务: {task.get('taskId', '-')}\n"
        f"老路由: {task.get('oldRoute', '-')}\n"
        f"新路由: {task.get('newRoute', '-')}\n"
        f"方法: {task.get('method', '-')}\n"
        f"服务: {task.get('oldServiceName', '-')} -> {task.get('newServiceName', '-')}\n"
        f"分支: {task.get('branch', '-')}\n"
        f"原因: {reason}\n"
        + (f"报告: {report_path}\n" if report_path else "")
        + "建议: 需要人工复核"
    )


def alert_task_blocked(task: dict, reason: str) -> str:
    return (
        f"【接口切换阻塞】\n"
        f"批次: {task.get('batchId', '-')}\n"
        f"任务: {task.get('taskId', '-')}\n"
        f"老路由: {task.get('oldRoute', '-')}\n"
        f"新路由: {task.get('newRoute', '-')}\n"
        f"状态: blocked\n"
        f"原因: {reason}\n"
        f"建议: 人工确认接口契约"
    )


def alert_batch_summary(batch_id: str, total: int, succeeded: int,
                        failed: int, blocked: int, started_at: str,
                        finished_at: str = "") -> str:
    return (
        f"【接口切换批次完成】\n"
        f"批次: {batch_id}\n"
        f"总数: {total}\n"
        f"成功: {succeeded}\n"
        f"失败: {failed}\n"
        f"阻塞: {blocked}\n"
        f"开始: {started_at}\n"
        + (f"结束: {finished_at}\n" if finished_at else "")
        + "摘要: 请查看失败与阻塞任务报告"
    )


def send(token: str, open_id: str, msg: str) -> bool:
    try:
        result = send_text(token, open_id, msg)
        return result.get("code") == 0
    except Exception as e:  # noqa: BLE001
        print(f"[alert] send failed: {e}", file=sys.stderr)
        return False


def send_alert(kind: str, open_id: str, **kwargs) -> bool:
    token = get_token(FEISHU_APP_ID, FEISHU_APP_SECRET)

    if kind == "task_failed":
        msg = alert_task_failed(kwargs["task"], kwargs["reason"], kwargs.get("report", ""))
    elif kind == "task_blocked":
        msg = alert_task_blocked(kwargs["task"], kwargs["reason"])
    elif kind == "batch_summary":
        msg = alert_batch_summary(**kwargs)
    else:
        print(f"[alert] unknown kind: {kind}", file=sys.stderr)
        return False

    return send(token, open_id, msg)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: alert.py <task_failed|task_blocked|batch_summary> <open_id> ...")
        sys.exit(1)

    kind = sys.argv[1]
    open_id = sys.argv[2]
    ok = False

    if kind == "task_failed":
        task = json.loads(sys.argv[3])
        reason = sys.argv[4] if len(sys.argv) > 4 else ""
        report = sys.argv[5] if len(sys.argv) > 5 else ""
        ok = send_alert("task_failed", open_id, task=task, reason=reason, report=report)
    elif kind == "task_blocked":
        task = json.loads(sys.argv[3])
        reason = sys.argv[4] if len(sys.argv) > 4 else ""
        ok = send_alert("task_blocked", open_id, task=task, reason=reason)
    elif kind == "batch_summary":
        ok = send_alert(
            "batch_summary",
            open_id,
            batch_id=sys.argv[3],
            total=int(sys.argv[4]),
            succeeded=int(sys.argv[5]),
            failed=int(sys.argv[6]),
            blocked=int(sys.argv[7]),
            started_at=sys.argv[8],
            finished_at=sys.argv[9] if len(sys.argv) > 9 else "",
        )

    sys.exit(0 if ok else 1)
