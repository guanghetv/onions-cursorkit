#!/usr/bin/env python3
"""
state.py — 任务状态持久化（SQLite）
支持：任务状态读写、锁管理、检查点、断点恢复
"""
import sqlite3
import json
import time
import sys
import os
from pathlib import Path
from typing import Optional

DEFAULT_DB = os.path.expanduser("~/work/openclaw-runner/state/tasks.db")


def get_db(db_path: str = DEFAULT_DB) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    _init_schema(conn)
    return conn


def _init_schema(conn: sqlite3.Connection):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS tasks (
        task_id       TEXT PRIMARY KEY,
        batch_id      TEXT NOT NULL,
        status        TEXT NOT NULL DEFAULT 'queued',
        attempt       INTEGER NOT NULL DEFAULT 0,
        started_at    REAL,
        finished_at   REAL,
        last_heartbeat REAL,
        report_path   TEXT,
        repos_touched TEXT,
        commit_shas   TEXT,
        error_type    TEXT,
        error_msg     TEXT,
        raw_json      TEXT
    );

    CREATE TABLE IF NOT EXISTS locks (
        repo      TEXT NOT NULL,
        branch    TEXT NOT NULL,
        task_id   TEXT NOT NULL,
        acquired  REAL NOT NULL,
        PRIMARY KEY (repo, branch)
    );

    CREATE TABLE IF NOT EXISTS batches (
        batch_id      TEXT PRIMARY KEY,
        status        TEXT NOT NULL DEFAULT 'batchQueued',
        total         INTEGER NOT NULL DEFAULT 0,
        succeeded     INTEGER NOT NULL DEFAULT 0,
        failed        INTEGER NOT NULL DEFAULT 0,
        blocked       INTEGER NOT NULL DEFAULT 0,
        created_at    REAL,
        finished_at   REAL,
        description   TEXT
    );

    CREATE TABLE IF NOT EXISTS heartbeats (
        task_id   TEXT PRIMARY KEY,
        beat_at   REAL NOT NULL
    );
    """)


def _row_to_dict(row: sqlite3.Row) -> dict:
    r = dict(row)
    for key in ("repos_touched", "commit_shas"):
        if r.get(key):
            r[key] = json.loads(r[key])
    if r.get("raw_json"):
        r["raw_json"] = json.loads(r["raw_json"])
    return r


def upsert_task(conn: sqlite3.Connection, task_id: str, batch_id: str,
                raw_json: dict, status: str = "queued"):
    conn.execute("""
        INSERT INTO tasks (task_id, batch_id, status, attempt, raw_json)
        VALUES (?, ?, ?, 0, ?)
        ON CONFLICT(task_id) DO UPDATE SET
            batch_id=excluded.batch_id,
            status=excluded.status,
            raw_json=excluded.raw_json
    """, (task_id, batch_id, status, json.dumps(raw_json, ensure_ascii=False)))


def get_task(conn: sqlite3.Connection, task_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM tasks WHERE task_id=?", (task_id,)
    ).fetchone()
    return _row_to_dict(row) if row else None


def update_task_status(conn: sqlite3.Connection, task_id: str,
                       status: str, error_type: str = None,
                       error_msg: str = None, report_path: str = None,
                       repos_touched: list = None, commit_shas: list = None):
    finished = time.time() if status in ("succeeded", "failed", "blocked", "cancelled") else None
    conn.execute("""
        UPDATE tasks SET
            status=?,
            error_type=?,
            error_msg=?,
            report_path=?,
            repos_touched=?,
            commit_shas=?,
            finished_at=?
        WHERE task_id=?
    """, (
        status, error_type, error_msg, report_path,
        json.dumps(repos_touched, ensure_ascii=False) if repos_touched else None,
        json.dumps(commit_shas, ensure_ascii=False) if commit_shas else None,
        finished, task_id
    ))


def set_task_running(conn: sqlite3.Connection, task_id: str):
    conn.execute("""
        UPDATE tasks SET status='running', started_at=?,
            attempt=attempt+1
        WHERE task_id=?
    """, (time.time(), task_id))


def heartbeat(conn: sqlite3.Connection, task_id: str):
    conn.execute(
        "INSERT OR REPLACE INTO heartbeats (task_id, beat_at) VALUES (?, ?)",
        (task_id, time.time())
    )


def get_stale_running(conn: sqlite3.Connection, max_age: float = 3600) -> list:
    cutoff = time.time() - max_age
    rows = conn.execute(
        "SELECT t.* FROM tasks t JOIN heartbeats h ON t.task_id=h.task_id "
        "WHERE t.status='running' AND h.beat_at<?", (cutoff,)
    ).fetchall()
    return [_row_to_dict(r) for r in rows]


def recover_stale(conn: sqlite3.Connection, max_age: float = 3600,
                  new_status: str = "failed"):
    stale = get_stale_running(conn, max_age)
    for t in stale:
        conn.execute(
            "UPDATE tasks SET status=? WHERE task_id=?",
            (new_status, t["task_id"])
        )
    return [t["task_id"] for t in stale]


def acquire_lock(conn: sqlite3.Connection, repo: str, branch: str,
                 task_id: str) -> bool:
    try:
        conn.execute(
            "INSERT INTO locks (repo, branch, task_id, acquired) VALUES (?,?,?,?)",
            (repo, branch, task_id, time.time())
        )
        return True
    except sqlite3.IntegrityError:
        return False


def release_lock(conn: sqlite3.Connection, repo: str, branch: str,
                 task_id: str):
    conn.execute(
        "DELETE FROM locks WHERE repo=? AND branch=? AND task_id=?",
        (repo, branch, task_id)
    )


def get_lock_holder(conn: sqlite3.Connection, repo: str,
                    branch: str) -> Optional[str]:
    row = conn.execute(
        "SELECT task_id FROM locks WHERE repo=? AND branch=?",
        (repo, branch)
    ).fetchone()
    return row["task_id"] if row else None


def upsert_batch(conn: sqlite3.Connection, batch_id: str,
                 description: str = "", total: int = 0):
    conn.execute("""
        INSERT INTO batches (batch_id, description, total, created_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(batch_id) DO UPDATE SET
            description=excluded.description,
            total=excluded.total
    """, (batch_id, description, total, time.time()))


def get_batch(conn: sqlite3.Connection, batch_id: str) -> Optional[dict]:
    row = conn.execute(
        "SELECT * FROM batches WHERE batch_id=?", (batch_id,)
    ).fetchone()
    return dict(row) if row else None


def update_batch_counts(conn: sqlite3.Connection, batch_id: str):
    row = conn.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status='succeeded' THEN 1 ELSE 0 END) as succeeded,
            SUM(CASE WHEN status='failed' THEN 1 ELSE 0 END) as failed,
            SUM(CASE WHEN status='blocked' THEN 1 ELSE 0 END) as blocked
        FROM tasks WHERE batch_id=?
    """, (batch_id,)).fetchone()
    conn.execute(
        "UPDATE batches SET succeeded=?, failed=?, blocked=? WHERE batch_id=?",
        (row["succeeded"], row["failed"], row["blocked"], batch_id)
    )


def finish_batch(conn: sqlite3.Connection, batch_id: str, status: str):
    conn.execute(
        "UPDATE batches SET status=?, finished_at=? WHERE batch_id=?",
        (status, time.time(), batch_id)
    )


if __name__ == "__main__":
    db = os.environ.get("STATE_DB", DEFAULT_DB)
    conn = get_db(db)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "help"

    if cmd == "task-get":
        t = get_task(conn, sys.argv[2])
        print(json.dumps(t, ensure_ascii=False, indent=2))
    elif cmd == "task-update":
        task_id, status = sys.argv[2], sys.argv[3]
        update_task_status(conn, task_id, status)
        conn.commit()
        print("ok")
    elif cmd == "lock-acquire":
        ok = acquire_lock(conn, sys.argv[2], sys.argv[3], sys.argv[4])
        print("acquired" if ok else "locked")
    elif cmd == "lock-release":
        release_lock(conn, sys.argv[2], sys.argv[3], sys.argv[4])
        conn.commit()
        print("ok")
    elif cmd == "batch-status":
        b = get_batch(conn, sys.argv[2])
        print(json.dumps(b, ensure_ascii=False, indent=2))
    elif cmd == "recover-stale":
        recovered = recover_stale(conn)
        conn.commit()
        print(json.dumps(recovered))
    else:
        print("Commands: task-get, task-update, lock-acquire, lock-release, batch-status, recover-stale")
