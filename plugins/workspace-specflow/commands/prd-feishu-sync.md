---
name: prd-feishu-sync
description: PRD 与飞书文档同步（create/push/reconcile/status/rebind）。默认 XML 富格式写入；禁止裸 BEGIN/END 与默认 markdown；不做一致性结论。
---

# /prd-feishu-sync

将当前需求目录的 `prd.md` 与绑定的飞书文档同步。

**硬规则**：`create` / `push` 一律 `--doc-format xml`（格式≠全量覆盖）；飞书文档已有内容时禁止整篇覆盖，即使用户要求重建也不 `overwrite`；增量失败 STOP 询问（策略 A）；画板不得降级为文本；`push` 不把文末 `prd-sync:check:v1` 写成通过或失败，改了正文就重置为「未校验」；禁止裸 `[PRD-SYNC:BEGIN/END]`。

常用：

- `/prd-feishu-sync create`
- `/prd-feishu-sync push`
- `/prd-feishu-sync reconcile`（飞书先改贴回本地时走这里；须先读 `three-way-sync.md`）
- `/prd-feishu-sync status`

完整规程见技能 `prd-feishu-sync`。发布前检查用 `/prd-check`，由 `/prd-publish` 在 push 之后调用。
