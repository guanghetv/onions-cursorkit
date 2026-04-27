---
name: /telemetry:audit-from-csv
id: telemetry-audit-from-csv
category: Telemetry
description: 基于 repo-resolution.csv 执行只读 telemetry 审计并生成 telemetry-audit-results.csv。
---

# /telemetry:audit-from-csv

读取并遵循 `skills/telemetry-audit-from-csv/SKILL.md`。这是第二阶段，只读审计，不改业务仓。

## 命令约定

- 命令文件按 namespace 目录组织在 `commands/telemetry/audit-from-csv.md`。
- frontmatter `name` 是真实推荐命令 `/telemetry:audit-from-csv`。
- 如需机械层脚本，优先使用插件内 `scripts/telemetry_cli.py`。
