---
name: pm-spec
description: 在原型基础上补充并结构化增强 prd.md，默认启用 WYSIWYG 友好输出；AI Review 详细记录外置，prd.md 仅保留可开工结论。
---

# /pm-spec

在原型基础上补充并结构化增强 `prd.md`。保留产品原始内容，输出阅读友好且结构清晰的 MODULE 文档（默认启用面向 WYSIWYG 的自适应富文本）；支持本地空模板时读取飞书文档回填（`lark-cli` 优先，`feishu-mcp` 兜底）。AI Review 详细结果写入 `prototypes/ai-review.md`，`prd.md` 仅保留可开工结论。
