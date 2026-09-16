---
name: prd-risk
description: 对当前需求执行产品需求风险预检。报告按预检 skill 产品正文写入 prototypes/prd-risk-precheck.md（含运行历史）。5稿/9稿写出后会自动调用。
---

# /prd-risk

对 specs 仓库目标需求做业务方案评审前风险预检。

完整规程见技能 `prd-risk`。必须 Read 同插件内 `product-requirement-risk-gate`，报告正文对齐该包「产品正文」（评估结论 / 需处理事项 / 下一步 / 请业务回复）。禁止把 5稿/9稿门禁、AI Review、工作台 JSON、37 条全表写入预检报告。

报告路径：`requirements/<需求>/prototypes/prd-risk-precheck.md`。同一文件复检更新；追加预检时间与结论。本期不同步飞书。

`/pm-spec-5` 与 `/pm-spec` 均在写出 `prd.md` 之后、AI Review 之前自动调用。确认时：无报告必须先预检；需调整硬阻断；待补软提醒可确认。
