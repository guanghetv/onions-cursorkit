---
name: onion-plan
description: 对变更做 Onion SDD Tier 分级，并路由到 mini、light 或 onion 完整 SDD 流程。
---

# /onion-plan

用于在动手前判断变更复杂度，并选择合适流程。它是 Onion SDD 的主入口：轻量变更走 mini/light，标准变更走 onion 自有完整 SDD 基座能力。

## 执行顺序

1. 读取 `skills/tier-triage/SKILL.md`，输出 Tier、依据、建议产物和验证方式。
2. Tier 0：只回答或排查，不创建 OpenSpec。
3. Tier 0+：转入 `/onion-hotfix` 与 `mini-change`。
4. Tier 1：转入 `/onion-tweak` 与 `light-change`。
5. Tier 2：读取 `skills/full-change/SKILL.md`，按完整流程完成需求接入、澄清、OpenSpec 落盘、任务规划、实现纪律、外部 spec 事件、E2E/验收与归档判断。
6. Tier 3：先拆分父子任务或多阶段计划，再让每个子任务进入 Tier 2+ 流程；Phase 1 接入 Trellis 后再使用 parent/child task tree 承载运行时。

## Tier 2+ 衔接

当需要完整流程时，以 onion 的 Tier 判断和当前变更产物为准，按以下 onion 自有 skill 串联：

| 阶段 | Skill | 产物 |
|------|-------|------|
| 完整流程编排 | `full-change` | 需求事实、范围、决策、任务阶段 |
| OpenSpec 落盘 | `openspec-change` | `proposal.md`、`specs/**/spec.md`、`tasks.md` |
| 外部 spec 接入 | `external-spec` | `backend-*.md`、`qa-*.md`、差异分析 |
| 验收验证 | `verify-change` | `e2e-report.md` |

这些能力属于 onion 自有流程；不能要求用户安装或调用其它 SDD 插件。

## 约束

- 不修改试点目录外的既有插件。
- 不把其他插件作为执行依赖。
- 不要求先遍历整个项目；围绕用户请求、OpenSpec 产物、相关代码和验证路径按需读取。
- `/onion-auto` 不属于当前基座能力范围。
