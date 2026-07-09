#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onion SDD /onsf-finish precheck.

Hard fail (exit != 0): missing change dir; incomplete tasks; Tier 2+ missing
e2e-report ## 验收结论; Tier 0++ overdue pending without ## 带债项.

Soft: openspec validate (skip if CLI unavailable) — never sole hard fail.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Import sibling helper without package install
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

import onion_state  # noqa: E402

WONT_DO_MARKERS = (
    "不做",
    "won't do",
    "wont do",
    "cancelled",
    "canceled",
    "skip",
    "skipped",
    "won't-do",
)

TASK_ITEM_RE = re.compile(r"^(\s*)[-*]\s+\[([ xX])\]\s+(.*)$")
HEADING_DEBT_RE = re.compile(r"^##\s+带债项\s*$", re.MULTILINE)
HEADING_ACCEPT_RE = re.compile(r"^##\s+验收结论\s*$", re.MULTILINE)


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    # Compare safely against aware "now": treat naive timestamps as local time.
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt


def is_wont_do(text: str) -> bool:
    lower = text.lower()
    for marker in WONT_DO_MARKERS:
        if marker.lower() in lower:
            return True
    return False


def find_incomplete_tasks(tasks_md: Path) -> List[str]:
    if not tasks_md.is_file():
        return ["tasks.md missing"]
    incomplete: List[str] = []
    text = tasks_md.read_text(encoding="utf-8")
    for line in text.splitlines():
        m = TASK_ITEM_RE.match(line)
        if not m:
            continue
        checked = m.group(2).lower() == "x"
        body = m.group(3).strip()
        if checked:
            continue
        if is_wont_do(body):
            continue
        incomplete.append(body)
    return incomplete


def infer_tier_from_proposal(proposal: Path) -> Optional[str]:
    if not proposal.is_file():
        return None
    text = proposal.read_text(encoding="utf-8")
    # Look for explicit tier markers
    m = re.search(r"(?i)\bTier\s*[:：]?\s*(0\+\+|0\+|0|1|2|3)\b", text)
    if m:
        return m.group(1)
    m = re.search(r"(?i)\btier\s*=\s*[\"']?(0\+\+|0\+|0|1|2|3)", text)
    if m:
        return m.group(1)
    return None


def normalize_tier(tier: Optional[str]) -> Optional[str]:
    if tier is None:
        return None
    t = str(tier).strip()
    return t


def is_tier2_plus(tier: Optional[str]) -> bool:
    t = normalize_tier(tier)
    if t is None:
        return False
    return t in ("2", "3") or t.startswith("2") or t.startswith("3")


def is_tier0pp(tier: Optional[str]) -> bool:
    return normalize_tier(tier) == "0++"


def has_debt_section(proposal: Path) -> bool:
    if not proposal.is_file():
        return False
    return bool(HEADING_DEBT_RE.search(proposal.read_text(encoding="utf-8")))


def has_acceptance_section(e2e_report: Path) -> bool:
    if not e2e_report.is_file():
        return False
    return bool(HEADING_ACCEPT_RE.search(e2e_report.read_text(encoding="utf-8")))


def run_openspec_validate(repo_root: Path, change_id: str) -> Dict[str, Any]:
    openspec = shutil.which("openspec")
    if not openspec:
        return {
            "status": "skipped",
            "reason": "openspec CLI unavailable",
        }
    try:
        proc = subprocess.run(
            [openspec, "validate", change_id],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"status": "skipped", "reason": f"openspec validate error: {exc}"}
    return {
        "status": "passed" if proc.returncode == 0 else "failed",
        "exit_code": proc.returncode,
        "stdout": (proc.stdout or "").strip()[-2000:],
        "stderr": (proc.stderr or "").strip()[-2000:],
    }


def resolve_change_id(repo_root: Path, args: argparse.Namespace) -> Tuple[Optional[str], Dict[str, Any], List[str]]:
    warnings: List[str] = []
    if args.change_id:
        # Still load state for tier0pp fields
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    str(_SCRIPTS_DIR / "onion_state.py"),
                    "--repo-root",
                    str(repo_root),
                    "get",
                ],
                capture_output=True,
                text=True,
                timeout=15,
                check=False,
            )
            state = json.loads(proc.stdout) if proc.stdout.strip() else onion_state.idle_state()
        except Exception:
            state = onion_state.idle_state()
        return args.change_id, state, warnings

    # Use onion_state.get logic in-process
    class NS:
        trellis_task_dir = getattr(args, "trellis_task_dir", None)

    # Capture get output
    import io
    from contextlib import redirect_stdout

    buf = io.StringIO()
    with redirect_stdout(buf):
        onion_state.cmd_get(repo_root, NS())
    try:
        state = json.loads(buf.getvalue())
    except json.JSONDecodeError:
        state = onion_state.idle_state()
        warnings.append("failed to parse onion_state get output")

    change_id = state.get("active_change_id")
    if not change_id:
        warnings.append("no active_change_id in state; pass --change-id")
    return change_id, state, warnings


def run_check(repo_root: Path, args: argparse.Namespace) -> Tuple[int, Dict[str, Any]]:
    hard_failures: List[str] = []
    soft: List[Dict[str, Any]] = []
    notes: List[str] = []

    change_id, state, warnings = resolve_change_id(repo_root, args)
    notes.extend(warnings)

    if not change_id:
        report = {
            "ok": False,
            "change_id": None,
            "hard_failures": ["missing change-id (no active state and --change-id not provided)"],
            "soft": soft,
            "notes": notes,
            "state_source": state.get("source"),
        }
        return 1, report

    change_dir = repo_root / "openspec" / "changes" / change_id
    if not change_dir.is_dir():
        hard_failures.append(f"change directory not found: openspec/changes/{change_id}")

    tier = normalize_tier(args.tier) if args.tier else normalize_tier(state.get("tier"))
    proposal = change_dir / "proposal.md"
    if tier is None and change_dir.is_dir():
        tier = infer_tier_from_proposal(proposal)
        if tier:
            notes.append(f"tier inferred from proposal.md: {tier}")

    # tasks.md
    if change_dir.is_dir():
        incomplete = find_incomplete_tasks(change_dir / "tasks.md")
        if incomplete:
            if incomplete == ["tasks.md missing"]:
                hard_failures.append("tasks.md missing")
            else:
                hard_failures.append(
                    "incomplete tasks (not marked 不做/won't do/cancelled): "
                    + "; ".join(incomplete[:10])
                    + (" ..." if len(incomplete) > 10 else "")
                )

    # Tier 2+ e2e
    if change_dir.is_dir() and is_tier2_plus(tier):
        e2e = change_dir / "e2e-report.md"
        if not e2e.is_file():
            hard_failures.append("Tier 2+ requires e2e-report.md")
        elif not has_acceptance_section(e2e):
            hard_failures.append("Tier 2+ e2e-report.md missing ## 验收结论")

    # Tier 0++ overdue pending
    pending = bool(state.get("tier0pp_openspec_pending"))
    deadline = parse_iso(state.get("tier0pp_deadline"))
    # Also treat explicit tier 0++ from args/state
    tier_is_0pp = is_tier0pp(tier) or pending
    if tier_is_0pp and pending and deadline is not None:
        now = datetime.now().astimezone()
        if now > deadline:
            if change_dir.is_dir() and has_debt_section(proposal):
                notes.append(
                    "Tier 0++ overdue with pending OpenSpec, but proposal has ## 带债项 "
                    "(follow-up exception); hard check waived for this item"
                )
            else:
                hard_failures.append(
                    f"Tier 0++ OpenSpec pending overdue (deadline {state.get('tier0pp_deadline')}); "
                    "补 mini OpenSpec 并 clear-tier0pp-pending，或在 proposal.md 落盘 ## 带债项"
                )

    # Soft validate
    if change_dir.is_dir():
        soft.append({"check": "openspec validate", **run_openspec_validate(repo_root, change_id)})

    ok = len(hard_failures) == 0
    report = {
        "ok": ok,
        "change_id": change_id,
        "tier": tier,
        "change_dir": str(change_dir.relative_to(repo_root)) if change_dir.is_dir() else f"openspec/changes/{change_id}",
        "hard_failures": hard_failures,
        "soft": soft,
        "notes": notes,
        "state_source": state.get("source"),
        "tier0pp_deadline": state.get("tier0pp_deadline"),
        "tier0pp_openspec_pending": state.get("tier0pp_openspec_pending"),
    }
    return (0 if ok else 1), report


def format_human(report: Dict[str, Any]) -> str:
    lines = [
        "## Onion Finish Precheck",
        f"- ok: {report.get('ok')}",
        f"- change-id: {report.get('change_id')}",
        f"- tier: {report.get('tier')}",
        f"- state source: {report.get('state_source')}",
        f"- change dir: {report.get('change_dir')}",
    ]
    if report.get("tier0pp_openspec_pending"):
        lines.append(f"- tier0pp pending: {report.get('tier0pp_openspec_pending')}")
        lines.append(f"- tier0pp deadline: {report.get('tier0pp_deadline')}")
    hard = report.get("hard_failures") or []
    if hard:
        lines.append("- hard failures:")
        for item in hard:
            lines.append(f"  - {item}")
    else:
        lines.append("- hard failures: none")
    soft = report.get("soft") or []
    if soft:
        lines.append("- soft checks:")
        for item in soft:
            status = item.get("status")
            reason = item.get("reason")
            extra = f" ({reason})" if reason else ""
            lines.append(f"  - {item.get('check')}: {status}{extra}")
    notes = report.get("notes") or []
    if notes:
        lines.append("- notes:")
        for n in notes:
            lines.append(f"  - {n}")
    if report.get("ok"):
        lines.append("- next: may proceed to openspec archive")
    else:
        lines.append("- next: STOP — do not archive until hard failures are resolved")
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Onion SDD finish precheck (hard gate before archive)")
    parser.add_argument(
        "--repo-root",
        default=os.environ.get("ONION_SDD_ROOT") or ".",
        help="Repository root (default: ONION_SDD_ROOT or .)",
    )
    parser.add_argument("--change-id", default=None)
    parser.add_argument("--tier", default=None, help="Override tier (else from state / proposal)")
    parser.add_argument("--trellis-task-dir", default=None)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"error: repo root not found: {repo_root}", file=sys.stderr)
        return 2
    code, report = run_check(repo_root, args)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(format_human(report))
        if args.json is False:
            # also print a compact JSON footer for agents? design says optional --json
            pass
    return code


if __name__ == "__main__":
    sys.exit(main())
