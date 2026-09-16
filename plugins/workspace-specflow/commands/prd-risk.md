---
name: prd-risk
description: 对当前需求执行产品需求风险预检。判定严格按 product-requirement-risk-gate；报告写 prototypes/prd-risk-precheck.md。5稿/9稿写出后自动调用。待补可确认，仅需调整硬拦。
---

# /prd-risk

对 specs 仓库目标需求做业务方案评审前风险预检。

**必须 Read** 同插件内 `product-requirement-risk-gate`（`SKILL.md`、`references/input-output.md`、`references/rules.json`）并按其原文判定。禁止适配层发明必填项、禁止把「待补信息」或「上线日未定」说成硬阻断或规则命中。

报告：`requirements/<需求>/prototypes/prd-risk-precheck.md`（预检包产品正文 + 运行历史）。本期不同步飞书。

`/pm-spec-5` 与 `/pm-spec` 在写出后、AI Review 前自动调用。确认时：无报告先预检；**仅需调整硬阻断**；待补软提醒可确认。
