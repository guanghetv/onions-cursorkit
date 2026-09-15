---
name: prd-risk
description: 对当前需求执行产品需求风险预检，写入独立报告 prototypes/prd-risk-precheck.md。5稿确认前也会自动调用。
---

# /prd-risk

对 specs 仓库目标需求做业务方案评审前风险预检。

完整规程见技能 `prd-risk`。必须 Read 同插件内 `product-requirement-risk-gate` 规则包，禁止口头结论代替扫描。

报告路径：`requirements/<需求>/prototypes/prd-risk-precheck.md`。本期不同步飞书。

`/pm-spec-5` 在用户确认 5 稿、写快照之前会自动调用本命令对应技能；HIT 或待补时硬阻断确认。
