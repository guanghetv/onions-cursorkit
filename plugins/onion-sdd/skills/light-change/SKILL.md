---
name: light-change
description: 为 Tier 1 轻量行为或体验调整生成 Onion SDD 产物，并约束实现、验证和升级。
---

# Light Change

Light change 适用于单点轻量行为或体验调整。它比 mini change 更重一点：需要清楚描述行为语义、用户场景和小范围回归，但仍不进入 onion 完整 SDD 路径。

## 适用条件

- 影响主要集中在一个页面、组件、命令或局部流程。
- 允许有有限产品语义，但验收条件可以简明表达。
- 不涉及跨模块协作、复杂接口契约、权限、安全、支付、资金或多角色流程。

## 产物目录

```text
openspec/changes/<change-id>/
├── proposal.md
├── tasks.md
└── specs/
    └── <capability>/
        └── spec.md
```

## proposal.md 模板

```markdown
# <change-id>

## 背景
- <用户问题或调整动机>

## 目标
- <本次希望达成的行为>

## 变更
- <具体改动点>

## 影响范围
- 页面/模块: <范围>
- 数据/API: <无变化或说明>
- 兼容性: <需要注意的旧行为>

## 不做范围
- <本次明确不处理的内容>

## 验证计划
- <单测/类型/lint/局部回归/手动验收>
```

## spec.md 模板

```markdown
# <capability>

<一句话说明能力。>

## MODIFIED Requirements

### Requirement: <行为要求>

系统 MUST <清楚描述期望行为>。

#### Scenario: <主要场景>

- **WHEN** <触发条件>
- **THEN** <期望结果>

#### Scenario: <边界场景>

- **WHEN** <边界条件>
- **THEN** <期望结果>
```

如果是新增能力，可把 `MODIFIED Requirements` 改为 `ADDED Requirements`。如果只是删除行为，可使用 `REMOVED Requirements` 并说明迁移影响。

## tasks.md 模板

```markdown
# Tasks

- [ ] 确认 Tier 1 范围与升级红线
- [ ] 写入 proposal/spec/tasks
- [ ] 完成实现
- [ ] 执行定向验证
- [ ] 执行小范围回归
- [ ] 更新任务状态与验证记录
```

## 升级条件

开发中出现以下任一情况，停止 light change 并升级到 `/onsf-plan`：

- 需要重新讨论产品方案。
- 需要后端、QA 或设计稿交叉确认。
- 影响范围扩展到多个模块或多个仓库。
- 验证需要完整 E2E 门禁。
- 出现安全、权限、资金、支付、审计或复杂状态流。

## 完成标准

- OpenSpec 产物能解释为什么改、改什么、怎么验。
- `tasks.md` 已更新。
- 定向验证与小范围回归有明确结果。
- 残余风险已在最终回复或产物中说明。

## 质量自检（写完后必须过一遍）

写完所有产物后，Agent 自问 3 个问题（同 mini-change + 额外 1 问）：

1. **可理解性**：3 个月后有人能从 proposal + spec 理解为什么改、改了什么？
2. **可定位性**：如果引入回归，能从 spec 的 Scenario 定位到受影响的场景？
3. **可复现性**：验证步骤别人能照着复现吗？
4. **边界覆盖**：spec.md 中至少 1 个主场景 + 1 个边界场景，且边界场景确实覆盖了非主路径？

任一是"否" → 不满足最低标准，补充对应产物。

### 最低内容标准（除 mini 要求外）

| 字段 | 最低要求 |
|------|----------|
| 不做范围 | 必须至少列出 1 条明确排除的相邻变更 |
| spec.md | 至少 1 个 Requirement + 1 个 WHEN/THEN 主场景 + 1 个 WHEN/THEN 边界场景 |
| 验证计划 | 必须列出具体验证工具/命令（不接受纯"手动测试"） |
