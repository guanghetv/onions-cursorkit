---
name: onsf-plan
description: 对变更做 Onion SDD Tier 分级，并路由到 mini、light 或 onion 完整 SDD 流程。
---

# /onsf-plan

用于在动手前判断变更复杂度，并选择合适流程。它是 Onion SDD 的主入口：轻量变更走 mini/light，标准变更走 onion 自有完整 SDD 基座能力。

## 执行顺序

1. **运行态 / 0++ 逾期扫描**：`python3 <onion-sdd>/scripts/onion_state.py --repo-root . get`。若 `tier0pp_openspec_pending` 已逾期，输出硬提示后再继续本请求的分级。
2. 读取 `skills/tier-triage/SKILL.md`，输出 Tier、依据、建议产物和验证方式。
3. Tier 判断完成后调用 `onion_state.py set --tier <t> --phase triage --last-action "<摘要>"`（有绑定 task 时主写 meta + 镜像 current）。
4. Tier 0：只回答或排查，不创建 OpenSpec。
5. Tier 0+：转入 `/onsf-fix` 与 `mini-change`。
6. Tier 0++：转入 `/onsf-fix`，并 `mark-tier0pp`。
7. Tier 1：转入 `/onsf-tweak` 与 `light-change`。
8. Tier 2：读取 `skills/full-change/SKILL.md`，按完整流程完成需求接入、澄清、OpenSpec 落盘、任务规划、实现纪律、外部 spec 事件、E2E/验收与归档判断；各阶段结束调用 `onion_state.py set`。
9. Tier 3：先拆分父子任务或多阶段计划，再让每个子任务进入 Tier 2+ 流程；使用 `trellis-adapter` / `bind-trellis` 将 parent/child change 映射到 Trellis parent/child task tree。

## Tier 2+ 衔接

当需要完整流程时，以 onion 的 Tier 判断和当前变更产物为准，按以下 onion 自有 skill 串联：

| 阶段 | Skill | 产物 |
|------|-------|------|
| 完整流程编排 | `full-change` | 需求事实、范围、决策、任务阶段 |
| OpenSpec 落盘 | `openspec-change` | `proposal.md`、`specs/**/spec.md`、`tasks.md` |
| 外部 spec 接入 | `external-spec` | `backend-*.md`、`qa-*.md`、差异分析 |
| 验收验证 | `verify-change` | `e2e-report.md` |

这些能力属于 onion 自有流程；不能要求用户安装或调用其它 SDD 插件。

前端 Tier 2+ 还需要在 `full-change` / `openspec-change` / `external-spec` / `verify-change` 内补齐：Figma 与局部范围、前端灰区决策、workspace-native spec 拉取、Browser 自动化确认和 check 阶段代码审查纪律。该补齐不等于新增 brainstorming 硬门禁。

## 约束

- 不修改试点目录外的既有插件。
- 不把其他插件作为执行依赖。
- 不要求先遍历整个项目；围绕用户请求、OpenSpec 产物、相关代码和验证路径按需读取。
- 阶段切换必须调用 `onion_state.py`；0++ 逾期必须硬提示。
- 需要无交互自动执行 SDD 流程时，使用 `/onsf-auto`；手动规划仍以本命令为主入口。`/onsf-auto` 与手动路径的行为差异是刻意设计，不视为缺陷。
- 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`；如必须改 Trellis 才能继续，先向用户确认。
