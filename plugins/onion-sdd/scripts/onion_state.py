#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Onion SDD runtime state helper.

Read priority: Trellis task meta.onion → .onion-sdd/current.json → idle
Write priority: bound Trellis task → primary meta.onion + mirror current.json;
                else → current.json only.

Does not modify Trellis source or .trellis/scripts/**. Only updates
task.json.meta.onion on an existing task when bound.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

META_VERSION = 1
CURRENT_VERSION = 1


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_iso(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        # Support trailing Z
        normalized = value.replace("Z", "+00:00")
        dt = datetime.fromisoformat(normalized)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.astimezone()
    return dt


def atomic_write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.is_file():
        return None
    try:
        with path.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def idle_state(last_action: str = "当前无活跃 Onion change") -> Dict[str, Any]:
    return {
        "version": CURRENT_VERSION,
        "active_change_id": None,
        "tier": None,
        "phase": "idle",
        "last_action": last_action,
        "last_action_at": now_iso(),
        "upgrade_risk": False,
        "trellis_task": None,
        "tier0pp_deadline": None,
        "tier0pp_openspec_pending": False,
        "source": "idle",
        "warnings": [],
    }


def current_path(repo_root: Path) -> Path:
    return repo_root / ".onion-sdd" / "current.json"


def resolve_repo_root(start: Path) -> Path:
    """Resolve repo root by walking up from `start` to the nearest dir with `.trellis/`.

    Falls back to `start` when no ancestor (including `start` itself) has `.trellis/`,
    preserving standalone-mode behavior. Used only when neither `--repo-root` nor
    `ONION_SDD_ROOT` is provided, so monorepo subpackage cwd finds the outer root.
    """
    try:
        start = start.resolve()
    except OSError:
        return start
    for cand in (start, *start.parents):
        if (cand / ".trellis").is_dir():
            return cand
    return start


def ensure_onion_gitignored(repo_root: Path) -> None:
    """Ensure .onion-sdd/ is ignored by git (local runtime state, not for the repo).

    Idempotent: appends `.onion-sdd/` to root .gitignore only if no equivalent
    active entry exists. Notes the append on stderr so the action is visible
    without polluting stdout JSON.
    """
    gitignore = repo_root / ".gitignore"
    target = ".onion-sdd/"
    raw = ""
    if gitignore.is_file():
        try:
            raw = gitignore.read_text(encoding="utf-8")
        except OSError:
            return
    for line in raw.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped in (target, target.rstrip("/")):
            return
    comment = "# Onion SDD 本地运行态（兜底指针，无需同步到仓库）"
    prefix = "" if raw == "" or raw.endswith("\n") else "\n"
    block = f"{prefix}{comment}\n{target}\n"
    try:
        with gitignore.open("a", encoding="utf-8") as fh:
            fh.write(block)
    except OSError as exc:
        print(f"[onion_state] 无法追加 .gitignore: {exc}", file=sys.stderr)
        return
    print(
        f"[onion_state] 已将 {target} 追加到 .gitignore（本地运行态，无需同步仓库）",
        file=sys.stderr,
    )


def _run_git(repo_root: Path, git_args: list) -> Optional[subprocess.CompletedProcess]:
    try:
        return subprocess.run(
            ["git", *git_args],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"[onion_state] 警告：Git 命令失败: {exc}", file=sys.stderr)
        return None


def _git_warn(action: str, proc: subprocess.CompletedProcess) -> None:
    detail = (proc.stderr or proc.stdout or "").strip()
    suffix = f": {detail}" if detail else ""
    print(f"[onion_state] 警告：无法{action}{suffix}", file=sys.stderr)


def clear_tracked_onion_state(repo_root: Path) -> None:
    """Remove tracked .onion-sdd files from the Git index, preserving local files."""
    toplevel = _run_git(repo_root, ["rev-parse", "--show-toplevel"])
    if toplevel is None:
        return
    if toplevel.returncode != 0:
        _git_warn("检测 .onion-sdd/ Git 跟踪状态", toplevel)
        return
    try:
        git_root = Path(toplevel.stdout.strip()).resolve()
        if git_root != repo_root.resolve():
            print(
                "[onion_state] 警告：--repo-root 不是 Git 仓库根，跳过 .onion-sdd/ index 清理",
                file=sys.stderr,
            )
            return
    except OSError as exc:
        print(f"[onion_state] 警告：无法解析 Git 仓库根: {exc}", file=sys.stderr)
        return

    tracked = _run_git(repo_root, ["ls-files", "--", ".onion-sdd"])
    if tracked is None:
        return
    if tracked.returncode != 0:
        _git_warn("检测 .onion-sdd/ Git 跟踪状态", tracked)
        return

    tracked_files = [line for line in tracked.stdout.splitlines() if line.strip()]
    if not tracked_files:
        return

    removed = _run_git(
        repo_root,
        ["rm", "-r", "--cached", "--ignore-unmatch", "--", ".onion-sdd"],
    )
    if removed is None:
        return
    if removed.returncode != 0:
        _git_warn("清理 .onion-sdd/ Git index", removed)
        return

    print(
        f"[onion_state] 已从 Git index 移除 .onion-sdd/ 下 {len(tracked_files)} 个已跟踪文件，本地文件保留",
        file=sys.stderr,
    )


def ensure_onion_local_state(repo_root: Path) -> None:
    """Keep .onion-sdd ignored and untracked before writing runtime state."""
    ensure_onion_gitignored(repo_root)
    clear_tracked_onion_state(repo_root)


def resolve_trellis_active_task(repo_root: Path) -> Optional[Path]:
    """Best-effort resolve Trellis active task without importing Trellis modules."""
    task_py = repo_root / ".trellis" / "scripts" / "task.py"
    if not task_py.is_file():
        return None
    try:
        proc = subprocess.run(
            [sys.executable, str(task_py), "current"],
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if proc.returncode != 0:
        return None
    line = (proc.stdout or "").strip().splitlines()
    if not line:
        return None
    raw = line[0].strip()
    if not raw or raw == "(none)":
        return None
    path = Path(raw)
    if not path.is_absolute():
        path = repo_root / path
    if path.is_dir() and (path / "task.json").is_file():
        return path
    return None


def normalize_task_dir(repo_root: Path, task_dir: Optional[str]) -> Optional[Path]:
    if not task_dir:
        return None
    path = Path(task_dir)
    if not path.is_absolute():
        path = repo_root / path
    return path


def read_meta_onion(task_dir: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    task_json_path = task_dir / "task.json"
    data = load_json(task_json_path)
    if data is None:
        return None, f"cannot read task.json: {task_json_path}"
    meta = data.get("meta")
    if not isinstance(meta, dict):
        return None, "task.json.meta missing or not an object"
    onion = meta.get("onion")
    if not isinstance(onion, dict):
        return None, "task.json.meta.onion missing or not an object"
    return onion, None


def write_meta_onion(task_dir: Path, onion: Dict[str, Any]) -> Optional[str]:
    task_json_path = task_dir / "task.json"
    data = load_json(task_json_path)
    if data is None:
        return f"cannot read task.json: {task_json_path}"
    if task_json_path.exists() and not os.access(task_json_path, os.W_OK):
        return f"task.json not writable: {task_json_path}"
    if not os.access(task_dir, os.W_OK):
        return f"task dir not writable: {task_dir}"
    meta = data.get("meta")
    if not isinstance(meta, dict):
        meta = {}
    meta["onion"] = onion
    data["meta"] = meta
    try:
        atomic_write_json(task_json_path, data)
    except OSError as exc:
        return f"failed to write meta.onion: {exc}"
    return None


def meta_to_state(onion: Dict[str, Any], task_dir: Path, task_status: Optional[str]) -> Dict[str, Any]:
    change_id = onion.get("change_id")
    phase = onion.get("phase") or ("idle" if not change_id else None)
    rel_task = str(task_dir)
    return {
        "version": onion.get("version", META_VERSION),
        "active_change_id": change_id,
        "change_path": onion.get("change_path"),
        "tier": onion.get("tier"),
        "phase": phase if phase else ("idle" if not change_id else "unknown"),
        "last_action": onion.get("last_action"),
        "last_action_at": onion.get("last_action_at"),
        "upgrade_risk": bool(onion.get("upgrade_risk", False)),
        "source_hashes": onion.get("source_hashes") or {},
        "parent_change_id": onion.get("parent_change_id"),
        "tier0pp_deadline": onion.get("tier0pp_deadline"),
        "tier0pp_openspec_pending": bool(onion.get("tier0pp_openspec_pending", False)),
        "trellis_task": {
            "task_dir": rel_task,
            "status": task_status,
        },
        "source": "trellis",
        "warnings": [],
    }


def current_to_state(current: Dict[str, Any]) -> Dict[str, Any]:
    change_id = current.get("active_change_id")
    phase = current.get("phase") or ("idle" if not change_id else "unknown")
    return {
        "version": current.get("version", CURRENT_VERSION),
        "active_change_id": change_id,
        "change_path": current.get("change_path"),
        "tier": current.get("tier"),
        "phase": phase,
        "last_action": current.get("last_action"),
        "last_action_at": current.get("last_action_at"),
        "upgrade_risk": bool(current.get("upgrade_risk", False)),
        "source_hashes": current.get("source_hashes") or {},
        "parent_change_id": current.get("parent_change_id"),
        "tier0pp_deadline": current.get("tier0pp_deadline"),
        "tier0pp_openspec_pending": bool(current.get("tier0pp_openspec_pending", False)),
        "trellis_task": current.get("trellis_task"),
        "metrics": current.get("metrics"),
        "notes": current.get("notes"),
        "source": "current",
        "warnings": [],
    }


def resolve_bound_task(
    repo_root: Path,
    explicit: Optional[str] = None,
    current: Optional[Dict[str, Any]] = None,
) -> Tuple[Optional[Path], list]:
    warnings: list = []
    if explicit:
        path = normalize_task_dir(repo_root, explicit)
        if path and path.is_dir() and (path / "task.json").is_file():
            return path, warnings
        warnings.append(f"explicit trellis task dir not usable: {explicit}")

    if current and isinstance(current.get("trellis_task"), dict):
        td = current["trellis_task"].get("task_dir")
        path = normalize_task_dir(repo_root, td)
        if path and path.is_dir() and (path / "task.json").is_file():
            return path, warnings
        if td:
            warnings.append(f"current.json trellis_task.task_dir missing or stale: {td}")

    active = resolve_trellis_active_task(repo_root)
    if active:
        return active, warnings
    return None, warnings


def cmd_get(repo_root: Path, args: argparse.Namespace) -> int:
    warnings: list = []
    current = load_json(current_path(repo_root))

    task_dir, w = resolve_bound_task(repo_root, getattr(args, "trellis_task_dir", None), current)
    warnings.extend(w)

    if task_dir:
        onion, err = read_meta_onion(task_dir)
        task_data = load_json(task_dir / "task.json") or {}
        status = task_data.get("status")
        if onion and onion.get("change_id"):
            state = meta_to_state(onion, task_dir, status)
            # Prefer repo-relative task_dir in output
            try:
                rel = str(task_dir.relative_to(repo_root))
            except ValueError:
                rel = str(task_dir)
            state["trellis_task"]["task_dir"] = rel
            state["warnings"] = warnings
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        if onion and not onion.get("change_id"):
            # Bound task exists but idle onion — fall through to current
            warnings.append("trellis meta.onion present but active_change_id/change_id empty")
        elif err:
            warnings.append(err)

    if current:
        phase = current.get("phase")
        change_id = current.get("active_change_id")
        if change_id is None or phase == "idle":
            state = idle_state(current.get("last_action") or "当前无活跃 Onion change")
            state["last_action_at"] = current.get("last_action_at") or state["last_action_at"]
            state["trellis_task"] = current.get("trellis_task")
            state["tier0pp_deadline"] = current.get("tier0pp_deadline")
            state["tier0pp_openspec_pending"] = bool(current.get("tier0pp_openspec_pending", False))
            state["warnings"] = warnings
            # Keep source as idle when explicitly idle
            print(json.dumps(state, ensure_ascii=False, indent=2))
            return 0
        state = current_to_state(current)
        state["warnings"] = warnings
        print(json.dumps(state, ensure_ascii=False, indent=2))
        return 0

    state = idle_state()
    state["warnings"] = warnings
    print(json.dumps(state, ensure_ascii=False, indent=2))
    return 0


def build_onion_from_fields(
    existing: Optional[Dict[str, Any]],
    *,
    change_id: Optional[str],
    change_path: Optional[str],
    tier: Optional[str],
    phase: Optional[str],
    last_action: Optional[str],
    upgrade_risk: Optional[bool],
    parent_change_id: Optional[str],
    source_hashes: Optional[Dict[str, Any]],
    tier0pp_deadline: Optional[str],
    tier0pp_openspec_pending: Optional[bool],
    clear_tier0pp: bool = False,
    idle: bool = False,
) -> Dict[str, Any]:
    base = dict(existing or {})
    base["version"] = META_VERSION
    if idle:
        base["change_id"] = None
        base["change_path"] = None
        base["tier"] = None
        base["phase"] = "idle"
        base["upgrade_risk"] = False
        base["tier0pp_openspec_pending"] = False
        # keep deadline history optional — clear pending semantics
        if "tier0pp_deadline" not in base:
            base["tier0pp_deadline"] = None
        if last_action is not None:
            base["last_action"] = last_action
        else:
            base["last_action"] = base.get("last_action") or "OpenSpec change 已归档 / idle"
        base["last_action_at"] = now_iso()
        return base

    if change_id is not None:
        base["change_id"] = change_id
        if change_path is None and change_id:
            base["change_path"] = f"openspec/changes/{change_id}"
    if change_path is not None:
        base["change_path"] = change_path
    if tier is not None:
        base["tier"] = tier
    if phase is not None:
        base["phase"] = phase
    if last_action is not None:
        base["last_action"] = last_action
        base["last_action_at"] = now_iso()
    elif "last_action_at" not in base:
        base["last_action_at"] = now_iso()
    if upgrade_risk is not None:
        base["upgrade_risk"] = upgrade_risk
    if parent_change_id is not None:
        base["parent_change_id"] = parent_change_id
    if source_hashes is not None:
        base["source_hashes"] = source_hashes
    if tier0pp_deadline is not None:
        base["tier0pp_deadline"] = tier0pp_deadline
    if tier0pp_openspec_pending is not None:
        base["tier0pp_openspec_pending"] = tier0pp_openspec_pending
    if clear_tier0pp:
        base["tier0pp_openspec_pending"] = False
    return base


def build_current_from_fields(
    existing: Optional[Dict[str, Any]],
    onion_like: Dict[str, Any],
    trellis_task: Optional[Dict[str, Any]],
    *,
    idle: bool = False,
) -> Dict[str, Any]:
    base = dict(existing or {})
    base["version"] = CURRENT_VERSION
    if idle:
        base["active_change_id"] = None
        base["tier"] = None
        base["phase"] = "idle"
        base["upgrade_risk"] = False
        base["tier0pp_openspec_pending"] = False
        base["last_action"] = onion_like.get("last_action") or "当前无活跃 Onion change"
        base["last_action_at"] = onion_like.get("last_action_at") or now_iso()
        if trellis_task is not None:
            base["trellis_task"] = trellis_task
        elif "trellis_task" not in base:
            base["trellis_task"] = None
        metrics = base.get("metrics") if isinstance(base.get("metrics"), dict) else {}
        metrics["finished_at"] = now_iso()
        base["metrics"] = metrics
        return base

    base["active_change_id"] = onion_like.get("change_id")
    if onion_like.get("change_path"):
        base["change_path"] = onion_like.get("change_path")
    base["tier"] = onion_like.get("tier")
    base["phase"] = onion_like.get("phase")
    base["last_action"] = onion_like.get("last_action")
    base["last_action_at"] = onion_like.get("last_action_at") or now_iso()
    base["upgrade_risk"] = bool(onion_like.get("upgrade_risk", False))
    if "source_hashes" in onion_like:
        base["source_hashes"] = onion_like.get("source_hashes")
    if "parent_change_id" in onion_like:
        base["parent_change_id"] = onion_like.get("parent_change_id")
    base["tier0pp_deadline"] = onion_like.get("tier0pp_deadline")
    base["tier0pp_openspec_pending"] = bool(onion_like.get("tier0pp_openspec_pending", False))
    if trellis_task is not None:
        base["trellis_task"] = trellis_task
    return base


def write_state(
    repo_root: Path,
    *,
    change_id: Optional[str] = None,
    change_path: Optional[str] = None,
    tier: Optional[str] = None,
    phase: Optional[str] = None,
    last_action: Optional[str] = None,
    upgrade_risk: Optional[bool] = None,
    trellis_task_dir: Optional[str] = None,
    parent_change_id: Optional[str] = None,
    source_hashes: Optional[Dict[str, Any]] = None,
    tier0pp_deadline: Optional[str] = None,
    tier0pp_openspec_pending: Optional[bool] = None,
    clear_tier0pp: bool = False,
    idle: bool = False,
    bind_only: bool = False,
) -> Dict[str, Any]:
    ensure_onion_local_state(repo_root)
    warnings: list = []
    cur_path = current_path(repo_root)
    current = load_json(cur_path) or {}

    task_dir, w = resolve_bound_task(repo_root, trellis_task_dir, current if current else None)
    warnings.extend(w)

    # bind-trellis: ensure trellis_task recorded even before meta write
    trellis_ref: Optional[Dict[str, Any]] = None
    if task_dir:
        try:
            rel = str(task_dir.relative_to(repo_root))
        except ValueError:
            rel = str(task_dir)
        task_data = load_json(task_dir / "task.json") or {}
        trellis_ref = {"task_dir": rel, "status": task_data.get("status")}

    if bind_only:
        if not task_dir:
            raise SystemExit("bind-trellis requires a usable --trellis-task-dir or active Trellis task")
        existing_onion, _ = read_meta_onion(task_dir)
        onion = dict(existing_onion or {"version": META_VERSION})
        onion.setdefault("version", META_VERSION)
        err = write_meta_onion(task_dir, onion)
        if err:
            warnings.append(err)
            warnings.append("meta write failed; writing current.json only")
            primary = "current"
        else:
            primary = "trellis"
        new_current = build_current_from_fields(
            current,
            {
                "change_id": onion.get("change_id") or current.get("active_change_id"),
                "change_path": onion.get("change_path") or current.get("change_path"),
                "tier": onion.get("tier") if onion.get("tier") is not None else current.get("tier"),
                "phase": onion.get("phase") or current.get("phase") or "idle",
                "last_action": last_action or onion.get("last_action") or current.get("last_action") or "bound Trellis task",
                "last_action_at": now_iso(),
                "upgrade_risk": onion.get("upgrade_risk", current.get("upgrade_risk", False)),
                "tier0pp_deadline": onion.get("tier0pp_deadline", current.get("tier0pp_deadline")),
                "tier0pp_openspec_pending": onion.get(
                    "tier0pp_openspec_pending", current.get("tier0pp_openspec_pending", False)
                ),
                "source_hashes": onion.get("source_hashes") or current.get("source_hashes") or {},
            },
            trellis_ref,
            idle=False,
        )
        if last_action:
            new_current["last_action"] = last_action
            new_current["last_action_at"] = now_iso()
        atomic_write_json(cur_path, new_current)
        return {
            "ok": True,
            "primary_write": primary,
            "mirrored_current": True,
            "trellis_task_dir": trellis_ref["task_dir"] if trellis_ref else None,
            "warnings": warnings,
            "state": current_to_state(new_current),
        }

    existing_onion: Optional[Dict[str, Any]] = None
    if task_dir:
        existing_onion, err = read_meta_onion(task_dir)
        if err and existing_onion is None:
            # missing onion is fine; start fresh
            pass

    onion = build_onion_from_fields(
        existing_onion,
        change_id=change_id,
        change_path=change_path,
        tier=tier,
        phase=phase,
        last_action=last_action,
        upgrade_risk=upgrade_risk,
        parent_change_id=parent_change_id,
        source_hashes=source_hashes,
        tier0pp_deadline=tier0pp_deadline,
        tier0pp_openspec_pending=tier0pp_openspec_pending,
        clear_tier0pp=clear_tier0pp,
        idle=idle,
    )

    primary = "current"
    if task_dir:
        err = write_meta_onion(task_dir, onion)
        if err:
            warnings.append(err)
            warnings.append("meta write failed; degrading to current.json only")
            primary = "current"
        else:
            primary = "trellis"

    # On idle with bound task, keep trellis_task ref for finish-work continuity
    keep_trellis = trellis_ref if (idle or trellis_ref) else trellis_ref
    if idle and trellis_ref is None and isinstance(current.get("trellis_task"), dict):
        keep_trellis = current.get("trellis_task")

    new_current = build_current_from_fields(current, onion, keep_trellis, idle=idle)
    atomic_write_json(cur_path, new_current)

    result_state = current_to_state(new_current)
    if primary == "trellis":
        result_state["source"] = "trellis"
    result_state["warnings"] = warnings
    return {
        "ok": True,
        "primary_write": primary,
        "mirrored_current": primary == "trellis",
        "trellis_task_dir": keep_trellis.get("task_dir") if isinstance(keep_trellis, dict) else None,
        "warnings": warnings,
        "state": result_state,
    }


def cmd_set(repo_root: Path, args: argparse.Namespace) -> int:
    source_hashes = None
    if getattr(args, "source_hashes_json", None):
        try:
            source_hashes = json.loads(args.source_hashes_json)
        except json.JSONDecodeError as exc:
            print(f"error: invalid --source-hashes-json: {exc}", file=sys.stderr)
            return 2

    result = write_state(
        repo_root,
        change_id=args.change_id,
        change_path=args.change_path,
        tier=args.tier,
        phase=args.phase,
        last_action=args.last_action,
        upgrade_risk=args.upgrade_risk,
        trellis_task_dir=args.trellis_task_dir,
        parent_change_id=args.parent_change_id,
        source_hashes=source_hashes,
        idle=bool(args.idle),
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_bind_trellis(repo_root: Path, args: argparse.Namespace) -> int:
    result = write_state(
        repo_root,
        trellis_task_dir=args.trellis_task_dir,
        last_action=args.last_action or "bound Trellis task for onion state",
        bind_only=True,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_mark_tier0pp(repo_root: Path, args: argparse.Namespace) -> int:
    hours = args.deadline_hours if args.deadline_hours is not None else 24
    if args.deadline:
        deadline = args.deadline
    else:
        deadline = (datetime.now().astimezone() + timedelta(hours=hours)).isoformat(timespec="seconds")
    result = write_state(
        repo_root,
        change_id=args.change_id,
        change_path=args.change_path,
        tier="0++",
        phase=args.phase or "implement",
        last_action=args.last_action or "marked Tier 0++; OpenSpec pending within 24h",
        upgrade_risk=args.upgrade_risk,
        trellis_task_dir=args.trellis_task_dir,
        tier0pp_deadline=deadline,
        tier0pp_openspec_pending=True,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def cmd_clear_tier0pp(repo_root: Path, args: argparse.Namespace) -> int:
    result = write_state(
        repo_root,
        change_id=args.change_id,
        phase=args.phase,
        last_action=args.last_action or "Tier 0++ mini OpenSpec completed; pending cleared",
        trellis_task_dir=args.trellis_task_dir,
        clear_tier0pp=True,
        tier0pp_openspec_pending=False,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Onion SDD state helper (Trellis meta.onion primary + current.json mirror/fallback)",
    )
    parser.add_argument(
        "--repo-root",
        default=None,
        help="Repository root (default: ONION_SDD_ROOT, else auto-resolve upward to nearest .trellis/, else cwd)",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_get = sub.add_parser("get", help="Read merged state (JSON)")
    p_get.add_argument("--trellis-task-dir", default=None)
    p_get.set_defaults(func=cmd_get)

    p_set = sub.add_parser("set", help="Write state by write priority")
    p_set.add_argument("--change-id", default=None)
    p_set.add_argument("--change-path", default=None)
    p_set.add_argument("--tier", default=None)
    p_set.add_argument("--phase", default=None)
    p_set.add_argument("--last-action", default=None)
    p_set.add_argument("--upgrade-risk", dest="upgrade_risk", action="store_true", default=None)
    p_set.add_argument("--no-upgrade-risk", dest="upgrade_risk", action="store_false")
    p_set.add_argument("--trellis-task-dir", default=None)
    p_set.add_argument("--parent-change-id", default=None)
    p_set.add_argument("--source-hashes-json", default=None)
    p_set.add_argument("--idle", action="store_true", help="Clear active change; phase=idle")
    p_set.set_defaults(func=cmd_set)

    p_bind = sub.add_parser("bind-trellis", help="Bind trellis_task.task_dir for subsequent primary meta writes")
    p_bind.add_argument("--trellis-task-dir", required=True)
    p_bind.add_argument("--last-action", default=None)
    p_bind.set_defaults(func=cmd_bind_trellis)

    p_mark = sub.add_parser("mark-tier0pp", help="Mark Tier 0++ with 24h OpenSpec pending deadline")
    p_mark.add_argument("--change-id", default=None)
    p_mark.add_argument("--change-path", default=None)
    p_mark.add_argument("--phase", default=None)
    p_mark.add_argument("--last-action", default=None)
    p_mark.add_argument("--trellis-task-dir", default=None)
    p_mark.add_argument("--deadline", default=None, help="ISO 8601 deadline (default now+24h)")
    p_mark.add_argument("--deadline-hours", type=float, default=None)
    p_mark.add_argument("--upgrade-risk", dest="upgrade_risk", action="store_true", default=None)
    p_mark.add_argument("--no-upgrade-risk", dest="upgrade_risk", action="store_false")
    p_mark.set_defaults(func=cmd_mark_tier0pp)

    p_clear = sub.add_parser("clear-tier0pp-pending", help="Clear tier0pp_openspec_pending after mini OpenSpec")
    p_clear.add_argument("--change-id", default=None)
    p_clear.add_argument("--phase", default=None)
    p_clear.add_argument("--last-action", default=None)
    p_clear.add_argument("--trellis-task-dir", default=None)
    p_clear.set_defaults(func=cmd_clear_tier0pp)

    return parser


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.repo_root is None:
        args.repo_root = os.environ.get("ONION_SDD_ROOT") or str(resolve_repo_root(Path.cwd()))
    repo_root = Path(args.repo_root).resolve()
    if not repo_root.is_dir():
        print(f"error: repo root not found: {repo_root}", file=sys.stderr)
        return 2
    return args.func(repo_root, args)


if __name__ == "__main__":
    sys.exit(main())
