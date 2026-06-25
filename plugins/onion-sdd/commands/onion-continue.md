---
name: onion-continue
description: 从已有 OpenSpec 变更产物恢复 Onion SDD 上下文并继续执行。
---

# /onion-continue

用于继续已有 `openspec/changes/<change-id>/`。当前优先使用 `.onion-sdd/current.json` 维护轻量状态；状态缺失或不可信时回退到 OpenSpec 产物和用户意图推断。Trellis adapter 接入后再叠加 task runtime。

## 执行顺序

1. 优先读取 `.onion-sdd/current.json` 中的 `active_change_id`、`tier`、`phase`、`last_action`。
2. 若状态文件不存在或不可信，定位用户指定的 change-id；若未指定，只列出候选并请用户选择。
3. 读取该变更目录下的 `proposal.md`、`tasks.md`、`specs/**/spec.md`、`backend-*.md`、`qa-*.md`、`e2e-report.md` 等存在的产物。
4. 使用 `skills/tier-triage/SKILL.md` 判断继续路径。
5. Tier 0+/1：继续使用 `mini-change` 或 `light-change` 的任务与验证纪律。
6. Tier 2+：读取 `full-change` 判断完整流程阶段；必要时调用 `openspec-change`、`external-spec` 或 `verify-change`。

## 状态推断

| 产物 | 推断阶段 | 下一步 |
|------|----------|--------|
| 无变更目录 | triage / plan | 使用 `tier-triage`，必要时 `/onion-plan` |
| 有 `proposal.md` + `specs/`，无 `tasks.md` | tasks | 使用 `openspec-change` 补 `tasks.md` |
| `tasks.md` 有未完成项 | implement | 继续当前任务并记录验证点 |
| `tasks.md` 全部完成，未见外部 spec 或报告 | integrate / verify | 等待外部 spec，或使用 `verify-change` |
| 存在 `backend-*.md` / `qa-*.md` | integrate / verify | 使用 `external-spec` 做差异分析，必要时更新任务 |
| 存在 `e2e-report.md` | finish | 以 `## 验收结论` 判断是否进入 `/onion-finish` |

## 完整流程恢复

- Tier 2+ 读取 `full-change` 作为阶段编排依据。
- 缺完整 OpenSpec 产物时，使用 `openspec-change` 补齐。
- 后端/API/QA 文档到达时，使用 `external-spec` 写入当前 change 并做差异分析。
- 验证阶段使用 `verify-change` 生成或更新 `e2e-report.md`。

## 约束

- 只读取当前变更相关产物和必要代码。
- 当前不使用 Trellis workflow-state；只读写 `.onion-sdd/current.json` 轻量状态。Trellis adapter 接入后优先读取 Trellis active task，再 fallback 到该状态文件和 OpenSpec。
- 不自动归档，不自动提交。
