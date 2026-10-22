---
name: prd-check
description: 一次检查内容质量、本地与飞书对齐、可读性告警。发布前由 /prd-publish 调用，也可单独自检。
---

# /prd-check

对当前需求做一次发布前检查。先读《产品组 PRD 写作规范》、chapter-map 和 `prd-check/references/ai-review-rubric.md`。结果写入 `prototypes/prd-check-YYYY-MM-DD.md`，并回写飞书文末「文档状态」里的 `prd-sync:check:v1`。`metadata.consistency` 就是这次检查的结论，不要另写一套字段。

不推正文，不写基线。`/pm-spec` 改稿时不自动调用。

详见技能 `prd-check`。
