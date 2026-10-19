# 产品工作区插件优化

## Goal

把产品工作区插件从 5 稿 / 9 稿改成一份持续更新的飞书需求文档，并让发布、基线和需求群通知接上。

## Requirements

- 变更正文以 `openspec/changes/workspace-specflow-prd-flow-upgrade/proposal.md` 和 `specs/` 为准。脑暴账本仍在同目录 `brainstorm.md`。
- 子任务：
  - `10-19-prd-baseline`：取消稿次，第一次 publish 设 `confirmed`，之后只前进基线。
  - `10-19-prd-three-way-sync`：原型、飞书文档、`prd.md` 三端对齐。
  - `10-19-prd-writing-spec`：七章模板、验收清单、AI Review 改以《产品组 PRD 写作规范》为准，不单设验收章。`/qa-spec` 从需求详情提取规则，并兼容飞书 CLI 直接读需求文档链接。规范正文已单独提交 `6702435`。
  - `10-19-prd-change-skill`：短通知和提交引导在 `/prd-publish`。`prd-change` 只做群内查询。
  - `10-19-prd-proto-core`：原型生成去掉占位文案和引导，只留核心页面流程及交互。

## Acceptance Criteria

- [ ] 五个子任务各自有可执行的规格和实现
- [ ] 未决项在脑暴里关闭后才进入实现

## 已确认决策

见 `openspec/changes/workspace-specflow-prd-flow-upgrade/brainstorm.md`。

| 决策 | 结论 |
| --- | --- |
| Trellis | 创建父任务 `10-19-workspace-specflow-prd-flow-upgrade`，下设子任务。 |
| 原型 | 本轮纳入，去掉占位文案和引导。 |
| 提交代码引导 | 本轮纳入，并入产品变更技能。 |
| 写作规范落地 | 飞书正文和 `prd.md` 都不单设验收章。`/qa-spec` 从需求详情提取，并兼容飞书 CLI 读文档链接。 |
| `/qa-spec` 门禁 | 不阻断生成，只提示。有本地快照且正文已漂移时，用例仍按上一版快照生成。 |
| Agent 禁令 | 写作禁令、飞书评论二次确认、已有内容禁止整篇覆盖、查询先调用 CodeWiki `search_wiki`，写入 `rules/agent-hard-rules.mdc`。 |
