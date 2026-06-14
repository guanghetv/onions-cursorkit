# prd.md 模板（5稿）

对齐飞书 PRD 模板：https://guanghe.feishu.cn/docx/S38Id4fxAofdz8xsWCVcRkHjnHg

5稿用于产品内审与交互评审会；方案可未定。相对 9稿模板：允许 `[待定]`，验收标准可写「待交互后补充」，AI Review 结论为「交互评审」口径。

结构与 `pm-spec/references/prd-template.md` 相同，差异如下：

## 5稿特有规则

- **一、需求概述** 开发速览表增加 `当前阶段: 5稿`
- **五、说明列** 允许：`a. [待定] 交互方案待确认`
- **3.3 关键关注** 允许开放问题：`待交互评审决议：…`
- **验收标准** 可写 `- [ ] 待交互评审后补充`
- **不得** 在 5稿确认时设置 `prd.status = confirmed`（下游仍须等 9稿）

## 5稿确认时 Agent 动作

1. 在 **二、版本及进度跟踪** 追加一行：`版本号 = 5-x`，`日期 = 确认当天`，`变更内容` 含摘要与待定项计数
2. 复制 `prd.md` → `snapshots/prd-v5-YYYY-MM-DD.md`
3. 更新 `metadata.yaml`：`prd.v5.status = confirmed`，`prd.stage = v5_confirmed`

## AI Review 结论（5稿）

写入 `prototypes/ai-review-v5.md` 全文；`prd.md` **二、变更内容** 对应行记：`AI Review: 可进入交互评审` / `建议补充后进入` / `暂不建议`
