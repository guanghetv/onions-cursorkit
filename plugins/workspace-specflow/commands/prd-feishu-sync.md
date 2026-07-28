---
name: prd-feishu-sync
description: PRD 与飞书文档同步（create/push/reconcile/status/rebind）。默认 XML 富格式写入；禁止裸 BEGIN/END 与默认 markdown；不做一致性结论。
---

# /prd-feishu-sync

将当前需求目录的 `prd.md` 与绑定的飞书文档同步。

**硬规则**：`create` / `push` 一律 `--doc-format xml`；人读用 callout + 短心跳码（`prd-sync:status:v1` 等），禁止裸 `[PRD-SYNC:BEGIN/END]`。

常用：

- `/prd-feishu-sync create`
- `/prd-feishu-sync push --stage v5`
- `/prd-feishu-sync push --stage v9`
- `/prd-feishu-sync push --stage v5 --force`
- `/prd-feishu-sync reconcile`
- `/prd-feishu-sync status`

完整规程见技能 `prd-feishu-sync`。一致性校验用 `/prd-consistency-check` 或一键 `/prd-publish`。
