---
name: /telemetry:instrument-from-csv
id: telemetry-instrument-from-csv
category: Telemetry
description: 基于 telemetry-audit-results.csv 自动生成计划、改代码、验证、提交并创建 MR。
---

# /telemetry:instrument-from-csv

读取并遵循 `skills/telemetry-instrument-from-csv/SKILL.md`。这是第三阶段，会修改业务仓、push 分支并创建或复用 MR。

## 命令约定

- 命令文件按 namespace 目录组织在 `commands/telemetry/instrument-from-csv.md`。
- frontmatter `name` 是真实推荐命令 `/telemetry:instrument-from-csv`。
- 如需机械层脚本，优先使用插件内 `scripts/telemetry_cli.py`。
