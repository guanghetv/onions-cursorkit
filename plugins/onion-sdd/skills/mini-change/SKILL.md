---
name: mini-change
description: 为 Tier 0+ 小修复生成最小 Onion SDD 产物，并约束实现和验证。
---

# Mini Change

Mini change 适用于已确认、低风险、影响很小的 Tier 0+ 变更。它保留最小可追溯性，但避免引入完整设计流程。

## 适用条件

- 用户目标明确，不需要继续探索需求。
- 影响范围可定位到少数文件或一个局部行为。
- 不改变接口契约、数据模型、权限、安全、支付、资金或复杂状态流。
- 验证方式明确，可以用定向测试、类型检查、lint、局部手动验证或小范围回归覆盖。

## 产物目录

```text
openspec/changes/<change-id>/
├── proposal.md
└── tasks.md
```

只有当变更确实改变用户可感知行为或规格语义时，才补充：

```text
openspec/changes/<change-id>/specs/<capability>/spec.md
```

## proposal.md 模板

```markdown
# <change-id>

## 背景
- <为什么要做这个小修复>

## 变更
- <本次改什么>

## 影响范围
- 文件/模块: <直接相关范围>
- 用户影响: <可见影响或无>

## 不做范围
- <明确不处理的相邻问题>

## 验证
- <计划执行的定向验证>
```

## tasks.md 模板

```markdown
# Tasks

- [ ] 确认影响范围与升级红线
- [ ] 完成最小实现
- [ ] 执行定向验证并记录结果
- [ ] 检查是否需要升级到 light/full 流程
```

## 实施纪律

1. 写产物前先确认仍符合 Tier 0+。
2. 只读取直接相关上下文。
3. 若实现中发现红线，停止 mini change 并升级到 `/onsf-plan`。
4. 完成后在最终回复中给出变更文件、验证命令和残余风险。

## 质量自检（写完后必须过一遍）

写完 `proposal.md` 后，Agent 自问 3 个问题：

1. **可理解性**：如果 3 个月后有人看这个 change，能从 proposal 理解为什么改、改了什么吗？
2. **可定位性**：如果这个修改引入了回归，能从 proposal 定位到根因和影响范围吗？
3. **可复现性**：验证步骤别人能照着复现吗？

3 个都是"否" → 不满足最低标准，重写 proposal。

### 最低内容标准

| 字段 | 不合格示例 | 合格示例 |
|------|-----------|----------|
| 背景 | "修 BUG" | "用户在 Safari 17 点击支付按钮无响应，控制台无报错" |
| 变更 | "让按钮可以点" | "事件绑定使用了不兼容语法，改为 addEventListener" |
| 影响范围 | "改了点东西" | "src/payment/Button.tsx L42-L48" |
| 验证 | "测过了" | "Safari 17 点击支付 → 跳转收银台；Chrome/Firefox 回归通过" |

## 归档

mini change 在任务完成、定向验证通过、无升级红线后，调用 `/onsf-finish` 自动归档。`/onsf-finish` 会执行门禁检查，通过后自动调用 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档。
