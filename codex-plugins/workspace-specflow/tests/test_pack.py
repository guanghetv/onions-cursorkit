import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "pack.py"
SPEC = importlib.util.spec_from_file_location("workspace_specflow_pack", SCRIPT)
pack = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(pack)


class RemoteMappingTests(unittest.TestCase):
    def test_normalizes_supported_git_remote_forms(self):
        expected = "teacher/backend/teacher-school"
        self.assertEqual(
            pack.normalize_remote_path(
                "git@gitlab.yc345.tv:teacher/backend/teacher-school.git"
            ),
            expected,
        )
        self.assertEqual(
            pack.normalize_remote_path(
                "https://gitlab.yc345.tv/teacher/backend/teacher-school.git"
            ),
            expected,
        )

    def test_maps_registry_by_remote_path_before_logical_name(self):
        registry = [
            {
                "name": "teacher-desk",
                "path": "../teacher-desk",
                "remote": "git@gitlab.yc345.tv:backend/teacher-desk.git",
            },
            {
                "name": "teacher-school",
                "path": "../teacher-school",
                "remote": "git@gitlab.yc345.tv:teacher/backend/teacher-school.git",
            },
        ]
        result = pack.map_registry_repos(
            registry,
            ["backend/teacher-desk", "teacher/backend/teacher-school"],
        )
        self.assertEqual(
            [item["gitnexus_repo"] for item in result],
            ["backend/teacher-desk", "teacher/backend/teacher-school"],
        )
        self.assertTrue(all(item["match"] == "remote" for item in result))

    def test_maps_all_aiclass_workspace_fixture_repositories(self):
        registry = [
            {
                "name": "teacher-desk",
                "remote": "git@gitlab.yc345.tv:backend/teacher-desk.git",
            },
            {
                "name": "teacher-ai-class",
                "remote": "git@gitlab.yc345.tv:backend/teacher-ai-class.git",
            },
            {
                "name": "teacher-school",
                "remote": "git@gitlab.yc345.tv:teacher/backend/teacher-school.git",
            },
            {
                "name": "onion-edu-manage",
                "remote": "git@gitlab.yc345.tv:teacher/fe/onion-edu-manage.git",
            },
            {
                "name": "padh5",
                "remote": "git@gitlab.yc345.tv:teacher/fe/padh5.git",
            },
            {
                "name": "teacher-workbench",
                "remote": "git@gitlab.yc345.tv:teacher/fe/teacher-workbench.git",
            },
        ]
        canonical = [
            "backend/teacher-desk",
            "backend/teacher-ai-class",
            "teacher/backend/teacher-school",
            "teacher/fe/onion-edu-manage",
            "teacher/fe/padh5",
            "teacher/fe/teacher-workbench",
        ]
        result = pack.map_registry_repos(registry, canonical)
        self.assertEqual(
            [item["gitnexus_repo"] for item in result],
            canonical,
        )
        self.assertTrue(all(item["match"] == "remote" for item in result))

    def test_does_not_guess_when_name_fallback_is_ambiguous(self):
        result = pack.map_registry_repos(
            [{"name": "school", "path": "../school", "remote": ""}],
            ["backend/school", "teacher/backend/school"],
        )
        self.assertIsNone(result[0]["gitnexus_repo"])
        self.assertEqual(result[0]["match"], "unmatched")

    def test_does_not_guess_by_name_when_remote_exists_but_unmatched(self):
        result = pack.map_registry_repos(
            [
                {
                    "name": "teacher-desk",
                    "path": "../teacher-desk",
                    "remote": "git@gitlab.yc345.tv:legacy/teacher-desk.git",
                }
            ],
            ["backend/teacher-desk"],
        )
        self.assertIsNone(result[0]["gitnexus_repo"])
        self.assertEqual(result[0]["match"], "unmatched")

    def test_unique_name_fallback_only_when_remote_is_missing(self):
        result = pack.map_registry_repos(
            [{"name": "teacher-desk", "path": "../teacher-desk", "remote": ""}],
            ["backend/teacher-desk"],
        )
        self.assertEqual(result[0]["gitnexus_repo"], "backend/teacher-desk")
        self.assertEqual(result[0]["match"], "unique-name")


class ManifestValidationTests(unittest.TestCase):
    def test_rejects_hooks_and_incomplete_interface(self):
        with tempfile.TemporaryDirectory() as temp:
            package_root = pack.build_package(Path(temp))
            path = package_root / ".codex-plugin" / "plugin.json"
            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(pack.validate_manifest(package_root), [])

            manifest["hooks"] = "./hooks.json"
            path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = pack.validate_manifest(package_root)
            self.assertTrue(any("hooks" in error for error in errors))

            del manifest["hooks"]
            manifest["version"] = "1"
            del manifest["interface"]["shortDescription"]
            path.write_text(
                json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            errors = pack.validate_manifest(package_root)
            self.assertTrue(any("semver" in error for error in errors))
            self.assertTrue(any("shortDescription" in error for error in errors))


class BuildTests(unittest.TestCase):
    def test_package_contains_manifest_adapter_and_all_source_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            package_root = pack.build_package(Path(temp))
            self.assertTrue(
                (package_root / ".codex-plugin" / "plugin.json").is_file()
            )
            self.assertFalse((package_root / "plugin.json").exists())
            manifest = json.loads(
                (package_root / ".codex-plugin" / "plugin.json").read_text(
                    encoding="utf-8"
                )
            )
            self.assertEqual(manifest["author"]["name"], "wenli")
            self.assertTrue(manifest["interface"]["displayName"])
            self.assertTrue(manifest["interface"]["shortDescription"])
            self.assertTrue(manifest["interface"]["longDescription"])
            self.assertTrue(manifest["interface"]["developerName"])
            self.assertTrue(manifest["interface"]["category"])
            self.assertTrue(manifest["interface"]["capabilities"])
            self.assertTrue(manifest["interface"]["defaultPrompt"])
            self.assertNotIn("hooks", manifest)
            self.assertTrue(
                (
                    package_root
                    / "skills"
                    / "workspace-code-context"
                    / "SKILL.md"
                ).is_file()
            )
            source_skills = {
                path.parent.name for path in pack.SOURCE_SKILLS.glob("*/SKILL.md")
            }
            packaged_skills = {
                path.parent.name
                for path in (package_root / "skills").glob("*/SKILL.md")
            }
            self.assertEqual(
                packaged_skills,
                source_skills | {"workspace-code-context"},
            )

    def test_codewiki_appendix_is_added_only_to_registry_aware_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            package_root = pack.build_package(Path(temp))
            qa_spec = (
                package_root / "skills" / "qa-spec" / "SKILL.md"
            ).read_text(encoding="utf-8")
            req_status = (
                package_root / "skills" / "req-status" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertIn(pack.APPENDIX_MARKER, qa_spec)
            self.assertNotIn(pack.APPENDIX_MARKER, req_status)

    def test_non_portable_frontmatter_is_moved_to_metadata_with_hard_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            package_root = pack.build_package(Path(temp))
            qa_execute = (
                package_root / "skills" / "qa-execute" / "SKILL.md"
            ).read_text(encoding="utf-8")
            self.assertNotRegex(qa_execute, r"(?m)^disable-model-invocation:")
            self.assertIn('disable-model-invocation: "true"', qa_execute)
            self.assertIn("<HARD-GATE>", qa_execute)
            self.assertIn("不得由模型自动触发", qa_execute)

    def test_rejects_symlink_escaping_source_tree(self):
        with tempfile.TemporaryDirectory() as temp:
            src = Path(temp) / "src"
            dest = Path(temp) / "dest"
            src.mkdir()
            outside = Path(temp) / "secret.txt"
            outside.write_text("secret", encoding="utf-8")
            (src / "link.txt").symlink_to(outside)
            with self.assertRaises(ValueError):
                pack._copy_tree(src, dest)

    def test_rejects_symlinked_source_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            allowed = root / "skills"
            allowed.mkdir()
            outside = root / "outside"
            outside.mkdir()
            (outside / "secret.txt").write_text("secret", encoding="utf-8")
            leak = allowed / "leak"
            leak.symlink_to(outside)
            dest = root / "dest"
            with self.assertRaises(ValueError):
                pack._copy_tree(leak, dest, allowed)
            self.assertFalse(dest.exists())

    def test_repeated_zip_builds_are_byte_identical(self):
        with tempfile.TemporaryDirectory() as temp:
            temp_path = Path(temp)
            first = temp_path / "first.zip"
            second = temp_path / "second.zip"
            pack.create_zip(first)
            pack.create_zip(second)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                names = archive.namelist()
            self.assertIn(
                "workspace-specflow/.codex-plugin/plugin.json",
                names,
            )
            self.assertFalse(any("/scripts/pack.py" in name for name in names))


class LockTests(unittest.TestCase):
    def test_source_lock_matches_current_workspace_skills(self):
        lock = json.loads(pack.SOURCE_LOCK.read_text(encoding="utf-8"))
        self.assertEqual(lock, pack.make_source_lock())


if __name__ == "__main__":
    unittest.main()
