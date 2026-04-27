---
name: /telemetry:setup
id: telemetry-setup
category: Telemetry
description: 初始化 telemetry-suite 本机配置，检查并引导配置 GitLab、飞书 CLI、工作区与默认过滤规则。
---

# /telemetry:setup

读取并遵循 `skills/telemetry-setup/SKILL.md`。用于首次安装或更换 GitLab/飞书/工作区配置。

## 命令约定

- 命令文件按 namespace 目录组织在 `commands/telemetry/setup.md`。
- frontmatter `name` 是真实推荐命令 `/telemetry:setup`。
- 如需机械层脚本，优先使用插件内 `scripts/telemetry_cli.py`。
