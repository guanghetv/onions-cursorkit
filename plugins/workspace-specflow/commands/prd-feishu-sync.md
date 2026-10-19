---
name: prd-feishu-sync
description: 飞书文档的创建、回收、状态和换绑。把正文同步到飞书并发布时走 /prd-publish。push 只在发布第 4 步里执行。
---

# /prd-feishu-sync

创建飞书文档、把飞书手改收回本地、查看绑定或换绑。

用户说「同步到飞书」或「推到飞书」时，改走 `/prd-publish`。不要在这里只推正文。

**硬规则**：`create` 与发布第 4 步里的 `push` 一律 `--doc-format xml`（格式≠全量覆盖）；飞书文档已有内容时禁止整篇覆盖，即使用户要求重建也不 `overwrite`；增量失败 STOP 询问（策略 A）；画板不得降级为文本；`push` 不把文末 `prd-sync:check:v1` 写成通过或失败，改了正文就重置为未校验态（emoji `📎`、蓝底、蓝边一起改）；禁止裸 `[PRD-SYNC:BEGIN/END]`。

常用：

- 把正文同步到飞书：`/prd-publish`
- `/prd-feishu-sync create`
- `/prd-feishu-sync reconcile`（飞书先改贴回本地时走这里；须先读 `three-way-sync.md`）
- `/prd-feishu-sync status`

完整规程见技能 `prd-feishu-sync`。`/prd-check` 由 `/prd-publish` 在 push 之后调用。
