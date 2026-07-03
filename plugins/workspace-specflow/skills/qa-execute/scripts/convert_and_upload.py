#!/usr/bin/env python3
"""Convert test-spec.md (if needed) and upload to Case Flow quick mode."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from collections import OrderedDict
from pathlib import Path

DEFAULT_BASE_URL = "https://ai-case-flow.yc345.tv"


def is_case_flow_nested_list(content: str) -> bool:
    lines = [ln for ln in content.splitlines() if ln.strip()]
    if not lines or not lines[0].lstrip().startswith("- "):
        return False
    return (
        "前置条件" in content
        and ("操作步骤" in content or re.search(r"^\s+-\s+步骤[：:]", content, re.M))
        and "预期结果" in content
    )


def module_id_from_heading(line: str) -> str:
    m = re.match(r"^##\s+(MODULE-[\w-]+)", line.strip())
    if m:
        return m.group(1)
    m = re.match(r"^##\s+(.+?)(?:[：:]\s*|$)", line.strip())
    return m.group(1).strip() if m else "MODULE"


def suite_title_from_content(content: str) -> str:
    for line in content.splitlines():
        m = re.match(r"^#\s+测试用例[：:]\s*(.+)$", line.strip())
        if m:
            return m.group(1).strip()
    return "测试用例"


def join_bullets(items: list[str]) -> str:
    return "；".join(x.strip() for x in items if x.strip())


def join_steps(items: list[str]) -> str:
    cleaned: list[str] = []
    for item in items:
        text = re.sub(r"^\d+\.\s*", "", item.strip())
        if text:
            cleaned.append(text)
    return "；".join(cleaned)


def parse_test_spec(content: str) -> tuple[str, list[dict[str, str]], list[str]]:
    suite_title = suite_title_from_content(content)
    current_module = "MODULE"
    scenarios: list[dict[str, str]] = []
    warnings: list[str] = []

    lines = content.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        mod = re.match(r"^##\s+(.+)$", line.strip())
        if mod and not line.strip().startswith("###"):
            current_module = module_id_from_heading(line)
            i += 1
            continue

        scene = re.match(r"^###\s+场景[：:]\s*(.+)$", line.strip())
        if not scene:
            i += 1
            continue

        title = scene.group(1).strip()
        pre: list[str] = []
        steps: list[str] = []
        expected: list[str] = []
        section: str | None = None
        i += 1

        while i < len(lines):
            cur = lines[i]
            if re.match(r"^###\s+场景[：:]", cur.strip()) or re.match(r"^##\s+", cur.strip()):
                break
            if re.match(r"^#\s+", cur.strip()):
                break

            if re.match(r"^\*\*前置条件\*\*[：:]?\s*$", cur.strip()):
                section = "pre"
                i += 1
                continue
            if re.match(r"^\*\*操作步骤\*\*[：:]?\s*$", cur.strip()):
                section = "steps"
                i += 1
                continue
            if re.match(r"^\*\*预期结果\*\*[：:]?\s*$", cur.strip()):
                section = "expected"
                i += 1
                continue

            bullet = re.match(r"^-\s+(.+)$", cur.strip())
            numbered = re.match(r"^\d+\.\s+(.+)$", cur.strip())
            if section == "pre" and bullet:
                pre.append(bullet.group(1))
            elif section == "steps" and numbered:
                steps.append(numbered.group(1))
            elif section == "expected" and bullet:
                expected.append(bullet.group(1))
            i += 1

        if not pre or not steps or not expected:
            warnings.append(f"跳过场景「{title}」：缺少前置条件/操作步骤/预期结果")
            continue

        scenarios.append(
            {
                "module": current_module,
                "title": title,
                "pre": join_bullets(pre),
                "steps": join_steps(steps),
                "expected": join_bullets(expected),
            }
        )

    return suite_title, scenarios, warnings


def indent(level: int, text: str) -> str:
    return f"{'  ' * (level - 1)}- {text}"


def convert_test_spec_to_nested(content: str) -> tuple[str, list[str]]:
    suite_title, scenarios, warnings = parse_test_spec(content)
    if not scenarios:
        raise ValueError("未解析到任何 ### 场景: 块，无法转换")

    lines: list[str] = [indent(1, suite_title)]
    by_module: OrderedDict[str, list[dict[str, str]]] = OrderedDict()
    for sc in scenarios:
        by_module.setdefault(sc["module"], []).append(sc)

    for mod, mod_scenarios in by_module.items():
        lines.append(indent(2, mod))
        for sc in mod_scenarios:
            lines.extend(
                [
                    indent(3, sc["title"]),
                    indent(4, f"前置条件：{sc['pre']}"),
                    indent(5, f"步骤：{sc['steps']}"),
                    indent(6, f"预期结果：{sc['expected']}"),
                ]
            )

    return "\n".join(lines) + "\n", warnings


def upload(base_url: str, filename: str, content: str) -> dict:
    url = f"{base_url.rstrip('/')}/api/v1/quick/sessions/import"
    payload = json.dumps(
        {"filename": filename, "content": content, "functionFiles": []},
        ensure_ascii=False,
    )
    proc = subprocess.run(
        ["curl", "-sS", "-X", "POST", url, "-H", "Content-Type: application/json", "-d", payload, "-w", "\nHTTP_CODE:%{http_code}"],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"curl 请求失败: {proc.stderr.strip() or proc.stdout.strip()}")
    body, _, code_part = proc.stdout.rpartition("HTTP_CODE:")
    code = code_part.strip()
    if code and code != "200":
        try:
            detail = json.loads(body)
        except json.JSONDecodeError:
            detail = body.strip()
        raise RuntimeError(f"上传失败 HTTP {code}: {detail}")
    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"响应非 JSON: {body[:500]}") from exc


def maybe_open_browser(base_url: str) -> None:
    if os.environ.get("CASE_FLOW_OPEN_BROWSER", "1") not in ("1", "true", "yes"):
        return
    quick_url = f"{base_url.rstrip('/')}/quick"
    if sys.platform == "darwin":
        subprocess.run(["open", quick_url], check=False)
    elif sys.platform.startswith("linux"):
        subprocess.run(["xdg-open", quick_url], check=False)
    elif sys.platform == "win32":
        subprocess.run(["cmd", "/c", "start", "", quick_url], check=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Upload test markdown to Case Flow quick mode")
    parser.add_argument("--file", required=True, help="Path to .md file")
    parser.add_argument(
        "--base-url",
        default=os.environ.get("CASE_FLOW_BASE_URL", DEFAULT_BASE_URL),
        help="Case Flow base URL",
    )
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()
    if not path.is_file():
        print(f"错误：文件不存在 {path}", file=sys.stderr)
        return 1

    raw = path.read_text(encoding="utf-8")
    warnings: list[str] = []

    if is_case_flow_nested_list(raw):
        mode = "passthrough"
        content = raw
    else:
        mode = "converted"
        try:
            content, warnings = convert_test_spec_to_nested(raw)
        except ValueError as exc:
            print(f"错误：{exc}", file=sys.stderr)
            return 1

    try:
        result = upload(args.base_url, path.name, content)
    except RuntimeError as exc:
        print(f"错误：{exc}", file=sys.stderr)
        return 1

    session = result.get("session", {})
    cases = result.get("cases", [])
    api_warnings = result.get("warnings", [])

    session_id = session.get("session_id", "")
    case_count = session.get("case_count", len(cases))
    suite_title = session.get("suite_title", "")

    print(json.dumps(
        {
            "ok": True,
            "mode": mode,
            "source_file": str(path),
            "session_id": session_id,
            "case_count": case_count,
            "suite_title": suite_title,
            "quick_url": f"{args.base_url.rstrip('/')}/quick",
            "warnings": warnings + list(api_warnings),
        },
        ensure_ascii=False,
        indent=2,
    ))

    print()
    print("--- Case Flow 上传成功 ---")
    print(f"来源: {path}")
    print(f"模式: {'直传' if mode == 'passthrough' else 'test-spec 转换'}")
    print(f"用例集: {suite_title}")
    print(f"用例数: {case_count}")
    if warnings:
        print(f"转换警告: {len(warnings)} 条")
        for w in warnings[:5]:
            print(f"  - {w}")
    print(f"快速模式: {args.base_url.rstrip('/')}/quick")
    print(f"Session 接力 ID: {session_id}")
    print("请在页面底部「Session 接力」粘贴上述 ID 后点击「进入」。")

    maybe_open_browser(args.base_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
