---
name: tier-triage
description: 判断用户请求属于 Onion SDD 的 Tier 0、0+、0++、1、2 或 3，并给出产物与验证路由。
---

# Tier 分级判断

本技能用于所有 Onion SDD slash command 的入口判断。目标是让小变更保持轻，复杂变更及时升级，而不是把所有请求都塞进完整流程。

## 输入

- 用户的原始请求。
- 当前已有的 OpenSpec 产物，如 `openspec/changes/<change-id>/proposal.md`、`tasks.md`、`specs/**/spec.md`。
- 与请求直接相关的代码、测试、配置、错误信息或运行证据。
- `.onion-sdd/current.json`（如果存在）。

按需读取上下文即可；优先围绕用户给出的路径、change-id、错误信息、相关模块和验证入口展开。

## 冲突检测

分级前扫描 `openspec/changes/` 下所有未归档的 change。如果本次变更涉及的文件与任一活跃 change 的 `proposal.md` 中「影响范围」所列文件重叠，在输出中标注警告。

不阻断流程，但要求用户确认知晓冲突。如果有 `.onion-sdd/current.json` 的活跃 change，优先提示先完成该变更。

## Tier 定义

| Tier | 判断标准 | 默认产物 |
|------|----------|----------|
| 0 | 只解释、排查、审阅或给建议，不需要修改 | 无 OpenSpec |
| 0 | 纯内部修正（类型/lint/格式化/无行为变化重构）或纯配置/文档变更 | 无 OpenSpec，commit 说明验证 |
| 0+ | 已确认的小修复，影响极小且验证路径明确 | mini change |
| 0++ | 线上 P0/P1 紧急故障，修复方案明确且 < 30 分钟 | 先修后补 mini OpenSpec（24h 内） |
| 1 | 单点轻量体验或行为调整，有有限产品语义 | light change |
| 2 | 跨模块、接口、状态流、数据契约、权限或 E2E 验收 | onion 完整 SDD 流程 |
| 3 | 多仓、多角色、多阶段，或需要拆分父子任务 | 拆分后走 Tier 2+ |

### Tier 判定决策树

```
Q1: 这个变更是否需要修改代码/配置/文档？
    否 → Tier 0（纯问答/排查/审阅）
    是 → 继续 Q2

Q2: 变更是否影响用户可感知的行为、产品语义、接口契约或数据结果？
    否 → 继续 Q2a（内部修正判定）
    是 → 继续 Q3

Q2a: 是否属于纯内部修正（类型标注/非用户可见 lint/注释/纯重构）或纯配置/文档变更（CI/CD 配置/环境变量/README/.gitignore/无 breaking 依赖升级）？
    是 → Tier 0，不落 OpenSpec
    否 → 继续 Q3（说明有用户可感知影响）

Q3: 变更是否涉及任一升级红线？
    是 → Tier 2+
    否 → 继续 Q4

Q4: 是否属于线上 P0/P1 紧急故障且预计修复 < 30 分钟？
    是 → Tier 0++，先修后补（24h 内补 OpenSpec）
    否 → 继续 Q5

Q5: 是否属于明确且低风险的修复？特征：问题已定位、修复方案唯一、验证路径清晰、预计改动 ≤ 3 个文件？
    是 → Tier 0+，mini change
    否 → 继续 Q6

Q6: 是否属于单模块内的小范围行为/体验调整？特征：1 个页面/组件、有限产品语义、无新接口？
    是 → Tier 1，light change
    否 → Tier 2+
```

### 具体示例

**Tier 0（纯内部/纯配置）**：修复 TS 类型标注不影响运行时 · 更新 .prettierrc · README 修正 · 非用户可见的日志格式调整
**Tier 0+**：支付按钮事件绑定错误 · 用户头像裂图 · 用户可见的错别字 · 空数据状态缺失
**Tier 1**：搜索防抖 · 下拉菜单加"最近使用" · 表单加"全选"（无新接口） · Toast 位置调整
**Tier 2+**：角色权限扩展 · 新增登录方式 · 优惠券选择步骤 · 客户端分页改服务端 · 任何涉及接口/权限/支付/状态机的变更

## 升级红线

出现任一情况时，不要继续 mini/light 流程，应升级到 `/onion-plan` 的 Tier 2+ 路由：

- 需求或验收标准不清，且不能通过一次简短确认解决。
- 涉及接口字段、错误码、数据模型、状态机、权限、安全、支付、资金或审计。
- 影响多个页面、多个模块、多个仓库或多个角色。
- 需要后端 spec、QA spec、设计稿或 E2E 报告作为门禁。
- 用户明确要求完整设计、完整 OpenSpec 或完整验收链路。

## 输出格式

```markdown
## Onion Tier 判断

- Tier: <0 | 0+ | 0++ | 1 | 2 | 3>
- 依据: <为什么这样分级>
- 建议命令: </onion-hotfix | /onion-tweak | /onion-plan | /onion-continue | /onion-finish>
- 建议产物: <无 | mini change | light change | onion 完整 OpenSpec>
- 验证方式: <定向验证 / 小范围回归 / E2E / 待确认>
- 升级条件: <继续过程中一旦出现什么情况就升级>
- 紧急 hotfix 候选: <是/否>  # Tier 0++，先修后补
- 活跃冲突: <无 / change-id-A（共享文件: xxx）>
- auto 模式判定: 人工  # Phase 0 固定为人工，后续阶段扩展
```

## 纪律

- Phase 0 只承诺 slash command 触发。
- 不使用 `/onion-auto`。
- 不读写 Trellis workflow-state。
- 不修改试点目录外的既有插件。
- Tier 2+ 进入 onion 完整 SDD 路径；不能把其他插件作为执行依赖。
