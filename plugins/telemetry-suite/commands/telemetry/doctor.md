---
name: /telemetry:doctor
id: telemetry-doctor
category: Telemetry
description: 检查 telemetry-suite 前置依赖、配置、权限、CSV schema 和 Agent CLI 可用性。
---

# /telemetry:doctor

读取并遵循 `skills/telemetry-doctor/SKILL.md`。默认只读诊断，不改业务仓、不写结果 CSV。

## 命令约定

- 命令文件按 namespace 目录组织在 `commands/telemetry/doctor.md`。
- frontmatter `name` 是真实推荐命令 `/telemetry:doctor`。
- 如需机械层脚本，优先使用插件内 `scripts/telemetry_cli.py`。
