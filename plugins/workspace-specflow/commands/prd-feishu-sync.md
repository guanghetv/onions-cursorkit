---
name: prd-feishu-sync
description: PRD 与飞书文档同步（create/push/reconcile/status/rebind）。增量契约推送；禁止默认整篇覆盖；不做一致性结论。
---

# /prd-feishu-sync

将当前需求目录的 `prd.md` 与绑定的飞书文档同步。

常用：

- `/prd-feishu-sync create`
- `/prd-feishu-sync push --stage v5`
- `/prd-feishu-sync push --stage v9`
- `/prd-feishu-sync push --stage v5 --force`
- `/prd-feishu-sync reconcile`
- `/prd-feishu-sync status`

完整规程见技能 `prd-feishu-sync`。一致性校验用 `/prd-consistency-check` 或一键 `/prd-publish`。
