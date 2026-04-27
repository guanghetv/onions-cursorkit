---
name: /telemetry:resolve-repos
id: telemetry-resolve-repos
category: Telemetry
description: 从飞书服务清单解析 GitLab 仓库并生成 repo-resolution.csv。
---

# /telemetry:resolve-repos

读取并遵循 `skills/telemetry-resolve-repos/SKILL.md`。这是第一阶段，会在 repo-resolution.csv 生成后停下等待人工确认。

## 命令约定

- 命令文件按 namespace 目录组织在 `commands/telemetry/resolve-repos.md`。
- frontmatter `name` 是真实推荐命令 `/telemetry:resolve-repos`。
- 如需机械层脚本，优先使用插件内 `scripts/telemetry_cli.py`。
