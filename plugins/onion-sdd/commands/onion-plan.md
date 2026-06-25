---
name: onion-plan
description: 对变更做 Onion SDD Tier 分级，并路由到 mini、light 或 onion 完整 SDD 流程。
---

# /onion-plan

用于在动手前判断变更复杂度，并选择合适流程。它是 Phase 0 的主入口，但仍只依赖 slash command 触发。

## 执行顺序

1. 读取 `skills/tier-triage/SKILL.md`，输出 Tier、依据、建议产物和验证方式。
2. Tier 0：只回答或排查，不创建 OpenSpec。
3. Tier 0+：转入 `/onion-hotfix` 与 `mini-change`。
4. Tier 1：转入 `/onion-tweak` 与 `light-change`。
5. Tier 2：进入 onion 完整 SDD 路径，通常包括需求澄清、完整 OpenSpec、任务拆解、实现、联调、E2E、归档判断。
6. Tier 3：先拆分父子任务或多阶段计划，再让每个子任务进入 Tier 2+ 流程。

## Tier 2+ 衔接

当需要完整流程时，以 onion 的 Tier 判断和当前变更产物为准。Phase 0 先用命令文档沉淀完整 SDD 路径；后续成熟能力应拆成 onion 自有 skills、模板和规则，不能要求用户安装其他插件。

## 约束

- 不修改试点目录外的既有插件。
- 不把其他插件作为执行依赖。
- 不要求先遍历整个项目；围绕用户请求、OpenSpec 产物、相关代码和验证路径按需读取。
- `/onion-auto` 不属于 Phase 0。
