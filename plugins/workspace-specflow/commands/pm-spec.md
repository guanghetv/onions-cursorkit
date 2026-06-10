---
name: pm-spec
description: 在原型基础上补充并结构化增强 prd.md，可读性强门禁（9 条 P0 阻断）；AI Review 详细记录外置，prd.md 仅保留可开工结论。
---

# /pm-spec

在原型基础上补充并结构化增强 `prd.md`。保留产品原始内容，输出阅读友好且结构清晰的 MODULE 文档。

**门禁（不可跳过）**：须先 **Read 并遵循 `superpowers:brainstorming`**，与产品确认 MODULE 拆分、需求类型、灰区与（迭代时）本轮变更 MODULE 清单后，才可改写 `prd.md` 并执行 AI Review。禁止因「prd/飞书已有内容」跳过澄清。

可读性作为 `confirmed` 强门禁（9 条 P0：内容 5 + 可读性 3 + 用户场景 1）。迭代需求按「本轮变更 MODULE 清单」聚焦评审。支持本地空模板时读取飞书文档回填（`lark-cli` 优先，`feishu-mcp` 兜底）。AI Review 详细结果写入 `prototypes/ai-review.md`，`prd.md` 仅保留可开工结论。
