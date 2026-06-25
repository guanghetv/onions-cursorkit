---
name: onion-continue
description: 从已有 OpenSpec 变更产物恢复 Onion SDD 上下文并继续执行。
---

# /onion-continue

用于继续已有 `openspec/changes/<change-id>/`。Phase 0 使用 `.onion-sdd/current.json` 维护轻量状态，不接入 Trellis adapter；状态缺失时回退到 OpenSpec 产物和用户意图推断。

## 执行顺序

1. 优先读取 `.onion-sdd/current.json` 中的 `active_change_id`、`tier`、`phase`、`last_action`。
2. 若状态文件不存在或不可信，定位用户指定的 change-id；若未指定，只列出候选并请用户选择。
3. 读取该变更目录下的 `proposal.md`、`tasks.md`、`specs/**/spec.md`、`backend-*.md`、`qa-*.md`、`e2e-report.md` 等存在的产物。
4. 使用 `skills/tier-triage/SKILL.md` 判断继续路径。
5. Tier 0+/1：继续使用 `mini-change` 或 `light-change` 的任务与验证纪律。
6. Tier 2+：按 onion 完整 SDD 路径继续，或使用已经沉淀到 onion 的自有能力。

## 状态推断

- 无 `tasks.md`：通常需要补任务或确认是否仍是轻量变更。
- `tasks.md` 有未完成项：继续实现或验证。
- 存在外部 spec：检查是否需要差异分析或联调。
- 存在 `e2e-report.md`：以验收结论判断是否可进入 finish。

## 约束

- 只读取当前变更相关产物和必要代码。
- 不使用 Trellis workflow-state；只读写 `.onion-sdd/current.json` 轻量状态。
- 不自动归档，不自动提交。
