#!/usr/bin/env python3
"""Build and validate the isolated workspace-specflow Agent Plugin."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.parse import urlsplit


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = Path(__file__).resolve().parents[3]
SOURCE_SKILLS = REPO_ROOT / "plugins" / "workspace-specflow" / "skills"
SOURCE_LOCK = PLUGIN_ROOT / "source-lock.json"
MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
README = PLUGIN_ROOT / "README.md"
ADAPTER_SKILLS = PLUGIN_ROOT / "skills"
APPENDIX = PLUGIN_ROOT / "codewiki-appendix.md"
APPENDIX_MARKER = "<CODEX-WORKSPACE-CONTEXT>"
PACKAGE_NAME = "workspace-specflow"
ALLOWED_MANIFEST_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "skills",
    "mcpServers",
    "apps",
    "interface",
}
ALLOWED_AUTHOR_FIELDS = {"name", "email", "url"}
REQUIRED_INTERFACE_STRINGS = (
    "displayName",
    "shortDescription",
    "longDescription",
    "developerName",
    "category",
)
IGNORED_NAMES = {"__pycache__", ".DS_Store"}
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SEMVER_RE = re.compile(
    r"^(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)\."
    r"(0|[1-9]\d*)"
    r"(?:-(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*)(?:\."
    r"(?:0|[1-9]\d*|\d*[A-Za-z-][0-9A-Za-z-]*))*)?"
    r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?$"
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]*]\(([^)]+)\)")
ALLOWED_SKILL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NON_PORTABLE_SKILL_FIELDS = {"disable-model-invocation"}


def _assert_within(root: Path, path: Path) -> None:
    root_resolved = root.resolve()
    resolved = path.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"路径越出源目录: {path}") from exc


def _require_source_within(source: Path, allowed_root: Path) -> None:
    if source.is_symlink():
        raise ValueError(f"拒绝目录/文件 symlink: {source}")
    _assert_within(allowed_root, source)


def iter_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file() and not path.is_symlink():
            continue
        if any(part in IGNORED_NAMES for part in path.parts):
            continue
        if path.suffix in {".pyc", ".pyo"}:
            continue
        _assert_within(root, path)
        if not path.is_file():
            continue
        yield path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def make_source_lock() -> dict:
    if not SOURCE_SKILLS.is_dir():
        raise FileNotFoundError(f"源技能目录不存在: {SOURCE_SKILLS}")
    files = {
        path.relative_to(REPO_ROOT).as_posix(): sha256(path)
        for path in iter_files(SOURCE_SKILLS)
    }
    return {
        "version": 1,
        "source": SOURCE_SKILLS.relative_to(REPO_ROOT).as_posix(),
        "files": files,
    }


def sync_source_lock() -> None:
    SOURCE_LOCK.write_text(
        json.dumps(make_source_lock(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"[workspace-specflow-codex] 已更新 {SOURCE_LOCK.relative_to(REPO_ROOT)}")


def normalize_remote_path(remote: str) -> str | None:
    value = remote.strip()
    if not value:
        return None
    if "://" in value:
        value = urlsplit(value).path
    elif re.match(r"^[^/@\s]+@[^:\s]+:", value):
        value = value.split(":", 1)[1]
    value = value.strip().strip("/")
    if value.endswith(".git"):
        value = value[:-4]
    return value or None


def map_registry_repos(registry: list[dict], gitnexus_repos: list[str]) -> list[dict]:
    canonical = [name.strip().strip("/") for name in gitnexus_repos if name.strip()]
    by_lower = {name.lower(): name for name in canonical}
    results = []
    for item in registry:
        remote_path = normalize_remote_path(str(item.get("remote") or ""))
        matched = by_lower.get(remote_path.lower()) if remote_path else None
        method = "remote" if matched else "unmatched"
        if not matched and not remote_path:
            logical_name = str(item.get("name") or "").strip().lower()
            candidates = [
                name for name in canonical if Path(name).name.lower() == logical_name
            ]
            if len(candidates) == 1:
                matched = candidates[0]
                method = "unique-name"
        results.append(
            {
                "name": item.get("name"),
                "path": item.get("path"),
                "remote": item.get("remote"),
                "remote_path": remote_path,
                "gitnexus_repo": matched,
                "match": method,
            }
        )
    return results


def _copy_tree(
    source: Path, destination: Path, allowed_root: Path | None = None
) -> None:
    _require_source_within(source, allowed_root or source)
    shutil.copytree(
        source,
        destination,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pyo", ".DS_Store"),
        symlinks=True,
        ignore_dangling_symlinks=True,
    )
    for path in destination.rglob("*"):
        if path.is_file() or path.is_symlink():
            _assert_within(destination, path)


INVOCATION_GATE = """
<HARD-GATE>
本技能不得由模型自动触发。仅当用户明确要求上传 Case Flow 或执行 qa-execute 时才允许运行；禁止在其它技能流程中静默调用上传脚本。
</HARD-GATE>
""".strip()


def sanitize_skill_frontmatter(content: str) -> str:
    if not content.startswith("---\n"):
        return content
    end = content.find("\n---", 4)
    if end < 0:
        return content
    frontmatter = content[4:end]
    lines = frontmatter.splitlines()
    sanitized = []
    stripped_fields = []
    for line in lines:
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):", line)
        if match and match.group(1) in NON_PORTABLE_SKILL_FIELDS:
            stripped_fields.append(match.group(1))
            continue
        sanitized.append(line)
    if "disable-model-invocation" in stripped_fields:
        sanitized.append("metadata:")
        sanitized.append('  disable-model-invocation: "true"')
    body = content[end:]
    if "disable-model-invocation" in stripped_fields and INVOCATION_GATE not in body:
        closer, rest = body[:4], body[4:]
        body = closer + "\n\n" + INVOCATION_GATE + rest
    return "---\n" + "\n".join(sanitized) + body


def build_package(work_dir: Path) -> Path:
    package_root = work_dir / PACKAGE_NAME
    if package_root.exists():
        shutil.rmtree(package_root)
    package_root.mkdir(parents=True)
    manifest_dir = package_root / ".codex-plugin"
    manifest_dir.mkdir()
    shutil.copy2(MANIFEST, manifest_dir / "plugin.json")
    shutil.copy2(README, package_root / "README.md")

    packaged_skills = package_root / "skills"
    packaged_skills.mkdir()
    for source_skill in sorted(SOURCE_SKILLS.iterdir()):
        if source_skill.is_dir() and (source_skill / "SKILL.md").is_file():
            destination = packaged_skills / source_skill.name
            _copy_tree(source_skill, destination, SOURCE_SKILLS)
            skill_file = destination / "SKILL.md"
            content = sanitize_skill_frontmatter(
                skill_file.read_text(encoding="utf-8")
            )
            if "workspace-repos.json" in content:
                appendix = APPENDIX.read_text(encoding="utf-8").strip()
                content = content.rstrip() + "\n\n" + appendix + "\n"
            skill_file.write_text(content, encoding="utf-8")

    for adapter_skill in sorted(ADAPTER_SKILLS.iterdir()):
        if adapter_skill.is_dir() and (adapter_skill / "SKILL.md").is_file():
            destination = packaged_skills / adapter_skill.name
            if destination.exists():
                raise ValueError(f"Codex 适配 skill 与源 skill 重名: {adapter_skill.name}")
            _copy_tree(adapter_skill, destination, ADAPTER_SKILLS)
    return package_root


def _frontmatter_field(content: str, field: str) -> str | None:
    if not content.startswith("---\n"):
        return None
    end = content.find("\n---", 4)
    if end < 0:
        return None
    match = re.search(rf"(?m)^{re.escape(field)}:\s*(.+)$", content[4:end])
    return match.group(1).strip() if match else None


def _non_empty_str(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_manifest(root: Path) -> list[str]:
    errors = []
    path = root / ".codex-plugin" / "plugin.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path}: manifest 无法解析: {exc}"]
    unknown = sorted(set(manifest) - ALLOWED_MANIFEST_FIELDS)
    if unknown:
        errors.append(f"{path}: 含 Codex 插件未允许字段: {', '.join(unknown)}")
    if manifest.get("name") != PACKAGE_NAME:
        errors.append(f"{path}: name 必须为 {PACKAGE_NAME}")
    if not _non_empty_str(manifest.get("description")):
        errors.append(f"{path}: 缺少 description")
    version = manifest.get("version")
    if not _non_empty_str(version) or not SEMVER_RE.fullmatch(str(version)):
        errors.append(f"{path}: version 必须为 strict semver")
    if manifest.get("skills") != "./skills/":
        errors.append(f"{path}: skills 必须为 ./skills/")
    author = manifest.get("author")
    if not isinstance(author, dict):
        errors.append(f"{path}: 缺少 author")
    else:
        unknown_author = sorted(set(author) - ALLOWED_AUTHOR_FIELDS)
        if unknown_author:
            errors.append(
                f"{path}: author 含未允许字段: {', '.join(unknown_author)}"
            )
        if not _non_empty_str(author.get("name")):
            errors.append(f"{path}: 缺少 author.name")
    interface = manifest.get("interface")
    if not isinstance(interface, dict):
        errors.append(f"{path}: 缺少 interface")
        return errors
    for field in REQUIRED_INTERFACE_STRINGS:
        if not _non_empty_str(interface.get(field)):
            errors.append(f"{path}: 缺少 interface.{field}")
    prompts = interface.get("defaultPrompt")
    if not isinstance(prompts, list) or not any(
        _non_empty_str(item) for item in prompts
    ):
        errors.append(f"{path}: 缺少 interface.defaultPrompt")
    capabilities = interface.get("capabilities")
    if not isinstance(capabilities, list) or not all(
        _non_empty_str(item) for item in capabilities
    ):
        errors.append(f"{path}: interface.capabilities 必须为非空字符串数组")
    return errors


def validate_skills(root: Path) -> list[str]:
    errors = []
    skills_root = root / "skills"
    if not skills_root.is_dir():
        return [f"{skills_root}: skills 目录不存在"]
    for skill_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            errors.append(f"{skill_dir}: 缺少 SKILL.md")
            continue
        content = skill_file.read_text(encoding="utf-8")
        name = _frontmatter_field(content, "name")
        description = _frontmatter_field(content, "description")
        end = content.find("\n---", 4)
        frontmatter = content[4:end] if end >= 0 else ""
        fields = {
            match.group(1)
            for match in re.finditer(
                r"(?m)^([A-Za-z][A-Za-z0-9-]*):", frontmatter
            )
        }
        unknown = sorted(fields - ALLOWED_SKILL_FIELDS)
        if unknown:
            errors.append(
                f"{skill_file}: 含 Agent Skills 未允许字段: {', '.join(unknown)}"
            )
        if name != skill_dir.name:
            errors.append(
                f"{skill_file}: frontmatter name={name!r} 与目录名不一致"
            )
        if not name or not SKILL_NAME_RE.fullmatch(name):
            errors.append(f"{skill_file}: name 不符合 Agent Skills 命名规则")
        if not description:
            errors.append(f"{skill_file}: 缺少 description")
    return errors


def validate_markdown_links(root: Path) -> list[str]:
    errors = []
    for markdown in iter_files(root):
        if markdown.suffix.lower() != ".md":
            continue
        content = markdown.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(content):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
                or "://" in target
                or "<" in target
            ):
                continue
            local_target = target.split("#", 1)[0]
            if local_target and not (markdown.parent / local_target).exists():
                errors.append(f"{markdown}: 相对引用不存在: {target}")
    return errors


def validate_source_lock() -> list[str]:
    try:
        recorded = json.loads(SOURCE_LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{SOURCE_LOCK}: 源锁无法解析，请先执行 sync: {exc}"]
    current = make_source_lock()
    if recorded == current:
        return []
    recorded_files = recorded.get("files", {}) if isinstance(recorded, dict) else {}
    current_files = current["files"]
    added = sorted(set(current_files) - set(recorded_files))
    removed = sorted(set(recorded_files) - set(current_files))
    changed = sorted(
        path
        for path in set(current_files) & set(recorded_files)
        if current_files[path] != recorded_files[path]
    )
    details = []
    if added:
        details.append(f"新增 {len(added)}")
    if removed:
        details.append(f"删除 {len(removed)}")
    if changed:
        details.append(f"修改 {len(changed)}")
    summary = "、".join(details) or "元数据变化"
    return [f"{SOURCE_LOCK}: 源技能已漂移（{summary}），请审阅后执行 sync"]


def validate_cursor_isolation() -> list[str]:
    marketplace = REPO_ROOT / ".cursor-plugin" / "marketplace.json"
    try:
        data = json.loads(marketplace.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{marketplace}: 无法验证 Cursor 隔离: {exc}"]
    errors = []
    for entry in data.get("plugins", []):
        source = str(entry.get("source") or "")
        if "codex-plugins" in source or entry.get("name") == "workspace-specflow-codex":
            errors.append(f"{marketplace}: Codex 插件不得注册到 Cursor marketplace")
    return errors


def run_checks() -> list[str]:
    errors = []
    errors.extend(validate_source_lock())
    errors.extend(validate_cursor_isolation())
    with tempfile.TemporaryDirectory() as temp:
        try:
            package_root = build_package(Path(temp))
        except (OSError, ValueError) as exc:
            return errors + [f"构建临时包失败: {exc}"]
        errors.extend(validate_manifest(package_root))
        errors.extend(validate_skills(package_root))
        errors.extend(validate_markdown_links(package_root))
    return errors


def create_zip(output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        package_root = build_package(Path(temp))
        with zipfile.ZipFile(
            output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            for path in iter_files(package_root):
                relative = path.relative_to(package_root.parent).as_posix()
                info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o100644 << 16
                archive.writestr(info, path.read_bytes())


def display_path(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(resolved)


def _load_gitnexus_names(path: Path) -> list[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return [str(item["name"] if isinstance(item, dict) else item) for item in data]
    repositories = data.get("repositories", [])
    return [str(item["name"] if isinstance(item, dict) else item) for item in repositories]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="同步、校验并打包 workspace-specflow Codex 插件"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("sync", help="更新源技能内容锁")
    subparsers.add_parser("check", help="检查源漂移和包结构")
    pack_parser = subparsers.add_parser("pack", help="生成确定性 ZIP")
    pack_parser.add_argument(
        "--output",
        type=Path,
        default=PLUGIN_ROOT / "dist" / f"{PACKAGE_NAME}.zip",
    )
    map_parser = subparsers.add_parser(
        "map-repos", help="将 workspace registry 映射为 GitNexus 规范仓名"
    )
    map_parser.add_argument("--registry", type=Path, required=True)
    map_parser.add_argument("--gitnexus-repos", type=Path, required=True)
    args = parser.parse_args(argv)

    try:
        if args.command == "sync":
            sync_source_lock()
            return 0
        if args.command == "check":
            errors = run_checks()
            if errors:
                for error in errors:
                    print(f"[workspace-specflow-codex][error] {error}", file=sys.stderr)
                return 1
            print("[workspace-specflow-codex] 校验通过")
            return 0
        if args.command == "pack":
            errors = run_checks()
            if errors:
                for error in errors:
                    print(f"[workspace-specflow-codex][error] {error}", file=sys.stderr)
                return 1
            create_zip(args.output)
            print(
                f"[workspace-specflow-codex] 已生成 "
                f"{display_path(args.output)}"
            )
            return 0

        registry_data = json.loads(args.registry.read_text(encoding="utf-8"))
        registry = registry_data.get("repos", registry_data)
        mapped = map_registry_repos(
            registry,
            _load_gitnexus_names(args.gitnexus_repos),
        )
        print(json.dumps(mapped, ensure_ascii=False, indent=2))
        return 0 if all(item["gitnexus_repo"] for item in mapped) else 2
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"[workspace-specflow-codex][error] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
