---
name: prd-risk
description: 对当前需求执行产品需求风险预检。判定严格按 product-requirement-risk-gate；报告写 prototypes/prd-risk-precheck.md。/prd-publish 在报告缺失或 prd.md 更新后调用。待补可继续，仅需调整阻止发布。
---

# /prd-risk

对 specs 仓库目标需求做业务方案评审前风险预检。

**必须 Read** 同插件内 `product-requirement-risk-gate`（`SKILL.md`、`references/input-output.md`、`references/rules.json`）并按其原文判定。禁止适配层发明必填项、禁止把「待补信息」或「上线日未定」说成硬阻断或规则命中。

报告：`requirements/<需求>/prototypes/prd-risk-precheck.md`（预检包产品正文 + 运行历史）。本期不同步飞书。

`/pm-spec` 改稿不自动调用。`/prd-publish` 在无报告、结论不可读或 `prd.md` 新于上次预检时调用。**仅需调整阻止发布**；待补软提醒后可继续。
