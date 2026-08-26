#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import io
import json
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock

import onion_state


class OnionLocalStateTests(unittest.TestCase):
    def test_gitignore_append_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)

            onion_state.write_state(repo, change_id="demo", phase="openspec")
            onion_state.write_state(repo, change_id="demo", phase="implement")

            entries = [
                line.strip()
                for line in (repo / ".gitignore").read_text(encoding="utf-8").splitlines()
                if line.strip() in {".onion-sdd", ".onion-sdd/"}
            ]
            self.assertEqual(entries, [".onion-sdd/"])
            self.assertTrue((repo / ".onion-sdd" / "current.json").is_file())

    def test_equivalent_gitignore_entry_is_not_duplicated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / ".gitignore").write_text(".onion-sdd\n", encoding="utf-8")

            onion_state.write_state(repo, change_id="demo", phase="openspec")

            self.assertEqual((repo / ".gitignore").read_text(encoding="utf-8"), ".onion-sdd\n")

    def test_tracked_state_is_removed_from_index_but_kept_locally(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            subprocess.run(["git", "init"], cwd=repo, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Onion Test"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "onion@example.com"], cwd=repo, check=True)
            state_dir = repo / ".onion-sdd"
            state_dir.mkdir()
            state_file = state_dir / "current.json"
            state_file.write_text('{"active_change_id":"old"}\n', encoding="utf-8")
            subprocess.run(["git", "add", ".onion-sdd/current.json"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-m", "track state"], cwd=repo, check=True, capture_output=True)

            stderr = io.StringIO()
            with redirect_stderr(stderr):
                onion_state.write_state(repo, change_id="demo", phase="openspec")

            tracked = subprocess.run(
                ["git", "ls-files", "--", ".onion-sdd"],
                cwd=repo,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertEqual(tracked.stdout, "")
            self.assertTrue(state_file.is_file())
            self.assertEqual(json.loads(state_file.read_text(encoding="utf-8"))["active_change_id"], "demo")
            self.assertIn("本地文件保留", stderr.getvalue())

    def test_git_failure_warns_without_blocking_state_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            stderr = io.StringIO()

            with mock.patch.object(onion_state.subprocess, "run", side_effect=OSError("git unavailable")):
                with redirect_stderr(stderr):
                    result = onion_state.write_state(repo, change_id="demo", phase="openspec")

            self.assertTrue(result["ok"])
            self.assertTrue((repo / ".onion-sdd" / "current.json").is_file())
            self.assertIn("警告", stderr.getvalue())
            self.assertIn("git unavailable", stderr.getvalue())

    def test_non_git_directory_warns_without_blocking_state_write(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                result = onion_state.write_state(repo, change_id="demo", phase="openspec")

            self.assertTrue(result["ok"])
            self.assertTrue((repo / ".onion-sdd" / "current.json").is_file())
            self.assertIn("警告", stderr.getvalue())

    def test_nested_repo_root_does_not_untrack_parent_onion_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            git_root = Path(tmp)
            subprocess.run(["git", "init"], cwd=git_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Onion Test"], cwd=git_root, check=True)
            subprocess.run(["git", "config", "user.email", "onion@example.com"], cwd=git_root, check=True)
            state_file = git_root / ".onion-sdd" / "current.json"
            state_file.parent.mkdir()
            state_file.write_text('{"active_change_id":"parent"}\n', encoding="utf-8")
            subprocess.run(["git", "add", ".onion-sdd/current.json"], cwd=git_root, check=True)
            subprocess.run(["git", "commit", "-m", "track parent state"], cwd=git_root, check=True, capture_output=True)

            nested = git_root / "pkg"
            nested.mkdir()
            stderr = io.StringIO()
            with redirect_stderr(stderr):
                onion_state.write_state(nested, change_id="nested", phase="openspec")

            tracked = subprocess.run(
                ["git", "ls-files", "--", ".onion-sdd"],
                cwd=git_root,
                check=True,
                capture_output=True,
                text=True,
            )
            self.assertIn(".onion-sdd/current.json", tracked.stdout)
            self.assertTrue(state_file.is_file())
            self.assertTrue((nested / ".onion-sdd" / "current.json").is_file())
            self.assertIn("不是 Git 仓库根", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
